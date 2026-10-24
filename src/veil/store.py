"""Transactional local ledger for Veil's non-canonical working state.

This store has no Vault client and cannot authorize canonical transitions.
SQLite transactions protect local updates from the read-modify-write races
inherent in the legacy whole-file JSON stores.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from .models import Observation, SignalRecord


class VeilIntegrityError(RuntimeError):
    """Persisted Veil state failed integrity validation."""


class VeilStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    claim TEXT NOT NULL,
                    lifecycle_state TEXT NOT NULL CHECK (
                        lifecycle_state IN ('HELD', 'REJECTED', 'DEFERRED', 'PROPOSED')
                    ),
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    recurrence_count INTEGER NOT NULL CHECK (recurrence_count >= 1),
                    uncertainty TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    record_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    signal_id TEXT NOT NULL REFERENCES signals(signal_id),
                    source_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    source_revision TEXT NOT NULL,
                    observation_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    signal_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS proposals (
                    request_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    proposal_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('PENDING', 'SUBMITTED', 'ACCEPTED', 'REJECTED', 'UNKNOWN'))
                );
                """
            )

    @staticmethod
    def signal_id(claim: str, scope: str = "default") -> str:
        normalized = " ".join(claim.casefold().split())
        digest = hashlib.sha256((scope + "\0" + normalized).encode("utf-8")).hexdigest()
        return "sig:" + digest[:32]

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def ingest(self, observation: Observation, *, claim: str, scope: str = "default") -> SignalRecord:
        observation.validate()
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("claim must be a non-empty string")
        sid = self.signal_id(claim, scope)
        observation_json = self._json({
            "schema_version": observation.schema_version,
            "observation_id": observation.observation_id,
            "source_id": observation.source_id,
            "observed_at": observation.observed_at,
            "source_revision": observation.source_revision,
            "collection_method": observation.collection_method,
            "source_trust_class": observation.source_trust_class,
            "payload": observation.payload,
            "provenance": observation.provenance,
        })
        event_id = "evt:" + hashlib.sha256(
            (observation.observation_id + "\0" + sid).encode("utf-8")
        ).hexdigest()[:32]
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                duplicate = conn.execute(
                    "SELECT signal_id FROM observations WHERE observation_id = ?",
                    (observation.observation_id,),
                ).fetchone()
                if duplicate:
                    if duplicate["signal_id"] != sid:
                        raise VeilIntegrityError("observation ID reused for a different signal")
                    row = conn.execute("SELECT * FROM signals WHERE signal_id = ?", (sid,)).fetchone()
                    if row is None:
                        raise VeilIntegrityError("observation exists without its signal record")
                    conn.execute("COMMIT")
                    return self._record_from_row(row)

                row = conn.execute("SELECT * FROM signals WHERE signal_id = ?", (sid,)).fetchone()
                if row is None:
                    record = SignalRecord(
                        signal_id=sid,
                        claim=claim.strip(),
                        lifecycle_state="HELD",
                        first_seen_at=observation.observed_at,
                        last_seen_at=observation.observed_at,
                        recurrence_count=1,
                        evidence_refs=(observation.observation_id,),
                    )
                else:
                    try:
                        existing = json.loads(row["record_json"])
                        self._validate_record(existing, sid)
                    except (json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
                        raise VeilIntegrityError("stored signal record is corrupt") from exc
                    refs = list(existing["evidence_refs"])
                    if observation.observation_id not in refs:
                        refs.append(observation.observation_id)
                    # New observations add evidence only. They never change a
                    # terminal/review state or promote a signal automatically.
                    state = existing["lifecycle_state"]
                    record = SignalRecord(
                        signal_id=sid,
                        claim=existing["claim"],
                        lifecycle_state=state,
                        first_seen_at=existing["first_seen_at"],
                        last_seen_at=max(existing["last_seen_at"], observation.observed_at),
                        recurrence_count=int(existing["recurrence_count"]) + 1,
                        evidence_refs=tuple(refs),
                        uncertainty=existing["uncertainty"],
                        scope=existing["scope"],
                    )
                record_json = self._json({
                    "schema_version": record.schema_version,
                    "signal_id": record.signal_id,
                    "claim": record.claim,
                    "lifecycle_state": record.lifecycle_state,
                    "first_seen_at": record.first_seen_at,
                    "last_seen_at": record.last_seen_at,
                    "recurrence_count": record.recurrence_count,
                    "evidence_refs": list(record.evidence_refs),
                    "uncertainty": record.uncertainty,
                    "scope": record.scope,
                })
                conn.execute(
                    """INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(signal_id) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at,
                    recurrence_count=excluded.recurrence_count,
                    record_json=excluded.record_json""",
                    (record.signal_id, record.claim, record.lifecycle_state,
                     record.first_seen_at, record.last_seen_at, record.recurrence_count,
                     record.uncertainty, record.scope, record_json),
                )
                conn.execute(
                    "INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)",
                    (observation.observation_id, sid, observation.source_id,
                     observation.observed_at, observation.source_revision, observation_json),
                )
                conn.execute(
                    "INSERT INTO events (event_id, event_type, signal_id, occurred_at, payload_json) VALUES (?, ?, ?, ?, ?)",
                    (event_id, "OBSERVATION_RECORDED", sid, observation.observed_at,
                     self._json({"observation_id": observation.observation_id, "recurrence_count": record.recurrence_count})),
                )
                conn.execute("COMMIT")
                return record
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise

    @staticmethod
    def _validate_record(record: Any, expected_id: str) -> None:
        if not isinstance(record, dict):
            raise ValueError("record must be an object")
        if record.get("signal_id") != expected_id:
            raise ValueError("signal identity mismatch")
        for key in ("claim", "lifecycle_state", "first_seen_at", "last_seen_at", "evidence_refs", "recurrence_count"):
            if key not in record:
                raise KeyError(key)
        if record["lifecycle_state"] not in {"HELD", "REJECTED", "DEFERRED", "PROPOSED"}:
            raise ValueError("unknown lifecycle state")
        if not isinstance(record["evidence_refs"], list) or int(record["recurrence_count"]) < 1:
            raise ValueError("invalid evidence refs or recurrence count")

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> SignalRecord:
        try:
            value = json.loads(row["record_json"])
            VeilStore._validate_record(value, row["signal_id"])
            return SignalRecord(
                signal_id=value["signal_id"],
                claim=value["claim"],
                lifecycle_state=value["lifecycle_state"],
                first_seen_at=value["first_seen_at"],
                last_seen_at=value["last_seen_at"],
                recurrence_count=int(value["recurrence_count"]),
                evidence_refs=tuple(value["evidence_refs"]),
                uncertainty=value.get("uncertainty", "UNASSESSED"),
                scope=value.get("scope", "UNASSESSED"),
                schema_version=value.get("schema_version", "0.1"),
            )
        except (json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
            raise VeilIntegrityError("stored signal record is corrupt") from exc

    def get_signal(self, signal_id: str) -> SignalRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM signals WHERE signal_id = ?", (signal_id,)).fetchone()
            return self._record_from_row(row) if row else None

    def list_events(self, signal_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_id, event_type, signal_id, occurred_at, payload_json FROM events WHERE signal_id = ? ORDER BY sequence",
                (signal_id,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "signal_id": row["signal_id"],
                "occurred_at": row["occurred_at"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def set_disposition(self, signal_id: str, disposition: str, *, actor: str, reason: str, occurred_at: str) -> SignalRecord:
        allowed = {"HELD", "REJECTED", "DEFERRED", "PROPOSED"}
        if disposition not in allowed:
            raise ValueError("unsupported Veil disposition")
        if not actor.strip() or not reason.strip() or not occurred_at.strip():
            raise ValueError("actor, reason, and occurred_at are required")
        event_id = "evt:" + hashlib.sha256(
            (signal_id + "\0" + disposition + "\0" + actor + "\0" + reason + "\0" + occurred_at).encode("utf-8")
        ).hexdigest()[:32]
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute("SELECT * FROM signals WHERE signal_id = ?", (signal_id,)).fetchone()
                if row is None:
                    raise KeyError(signal_id)
                current = self._record_from_row(row)
                if current.lifecycle_state in {"REJECTED", "PROPOSED"} and disposition != current.lifecycle_state:
                    raise VeilIntegrityError("terminal/review state requires an explicit superseding event")
                updated = SignalRecord(
                    signal_id=current.signal_id,
                    claim=current.claim,
                    lifecycle_state=disposition,
                    first_seen_at=current.first_seen_at,
                    last_seen_at=current.last_seen_at,
                    recurrence_count=current.recurrence_count,
                    evidence_refs=current.evidence_refs,
                    uncertainty=current.uncertainty,
                    scope=current.scope,
                )
                record_json = self._json({
                    "schema_version": updated.schema_version,
                    "signal_id": updated.signal_id,
                    "claim": updated.claim,
                    "lifecycle_state": updated.lifecycle_state,
                    "first_seen_at": updated.first_seen_at,
                    "last_seen_at": updated.last_seen_at,
                    "recurrence_count": updated.recurrence_count,
                    "evidence_refs": list(updated.evidence_refs),
                    "uncertainty": updated.uncertainty,
                    "scope": updated.scope,
                })
                conn.execute("UPDATE signals SET lifecycle_state = ?, record_json = ? WHERE signal_id = ?",
                             (disposition, record_json, signal_id))
                conn.execute(
                    "INSERT OR IGNORE INTO events (event_id, event_type, signal_id, occurred_at, payload_json) VALUES (?, ?, ?, ?, ?)",
                    (event_id, "DISPOSITION_SET", signal_id, occurred_at,
                     self._json({"disposition": disposition, "actor": actor, "reason": reason})),
                )
                conn.execute("COMMIT")
                return updated
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
