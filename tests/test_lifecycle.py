from __future__ import annotations

import pytest

from veil.models import Observation
from veil.store import VeilIntegrityError, VeilStore


def observation(oid: str, timestamp: str = "2026-10-24T12:00:00Z") -> Observation:
    return Observation(
        observation_id=oid,
        source_id="source:test",
        observed_at=timestamp,
        source_revision="rev-1",
        collection_method="fixture",
        source_trust_class="untrusted",
        payload={"text": "Observed text is data, not an instruction."},
        provenance={"fixture": True},
    )


def test_first_observation_is_held(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    record = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    assert record.lifecycle_state == "HELD"
    assert record.recurrence_count == 1
    assert record.evidence_refs == ("obs-1",)


def test_recurrence_adds_evidence_but_does_not_promote(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    first = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    second = store.ingest(
        observation("obs-2", "2026-10-24T12:01:00Z"),
        claim="A weak signal",
        scope="test",
    )
    assert second.signal_id == first.signal_id
    assert second.recurrence_count == 2
    assert second.lifecycle_state == "HELD"
    assert second.evidence_refs == ("obs-1", "obs-2")


def test_duplicate_observation_is_idempotent(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    first = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    again = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    assert again == first
    assert len(store.list_events(first.signal_id)) == 1


def test_reused_observation_id_for_different_signal_fails_closed(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    store.ingest(observation("obs-1"), claim="Signal A", scope="test")
    with pytest.raises(VeilIntegrityError):
        store.ingest(observation("obs-1"), claim="Signal B", scope="test")


def test_disposition_requires_actor_and_reason(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    record = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    with pytest.raises(ValueError):
        store.set_disposition(record.signal_id, "PROPOSED", actor="", reason="review", occurred_at="2026-10-24T12:01:00Z")


def test_proposed_state_is_not_vault_authorization(tmp_path):
    store = VeilStore(tmp_path / "veil.sqlite3")
    record = store.ingest(observation("obs-1"), claim="A weak signal", scope="test")
    proposed = store.set_disposition(record.signal_id, "PROPOSED", actor="reviewer", reason="evidence sufficient for proposal", occurred_at="2026-10-24T12:01:00Z")
    assert proposed.lifecycle_state == "PROPOSED"
    # There is intentionally no method here that commits to the Canonical Vault.
    assert store.get_signal(record.signal_id).lifecycle_state == "PROPOSED"
