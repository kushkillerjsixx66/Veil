"""Versioned data contracts for the initial Veil runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Disposition(StrEnum):
    HOLD = "HOLD"
    REJECT = "REJECT"
    DEFER = "DEFER"
    PROPOSE = "PROPOSE"


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: str
    source_id: str
    observed_at: str
    source_revision: str
    collection_method: str
    source_trust_class: str
    payload: dict[str, Any]
    provenance: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "0.1"

    def validate(self) -> None:
        required = {
            "observation_id": self.observation_id,
            "source_id": self.source_id,
            "observed_at": self.observed_at,
            "source_revision": self.source_revision,
            "collection_method": self.collection_method,
            "source_trust_class": self.source_trust_class,
        }
        missing = [key for key, value in required.items() if not isinstance(value, str) or not value.strip()]
        if missing:
            raise ValueError("observation missing required fields: " + ", ".join(missing))
        if not isinstance(self.payload, dict) or not isinstance(self.provenance, dict):
            raise ValueError("payload and provenance must be objects")


@dataclass(frozen=True, slots=True)
class SignalRecord:
    signal_id: str
    claim: str
    lifecycle_state: str
    first_seen_at: str
    last_seen_at: str
    recurrence_count: int
    evidence_refs: tuple[str, ...]
    uncertainty: str = "UNASSESSED"
    scope: str = "UNASSESSED"
    schema_version: str = "0.1"


@dataclass(frozen=True, slots=True)
class TransitionProposal:
    request_id: str
    idempotency_key: str
    actor_identity: str
    authority_reference: str
    requested_transition: dict[str, Any]
    constraints: tuple[str, ...]
    evidence_bundle_ref: str
    expected_vault_revision: str
    policy_version: str
    reversibility_plan: str
    lineage: dict[str, Any]
    schema_version: str = "0.1"

    def validate(self) -> None:
        required = {
            "request_id": self.request_id,
            "idempotency_key": self.idempotency_key,
            "actor_identity": self.actor_identity,
            "authority_reference": self.authority_reference,
            "evidence_bundle_ref": self.evidence_bundle_ref,
            "expected_vault_revision": self.expected_vault_revision,
            "policy_version": self.policy_version,
            "reversibility_plan": self.reversibility_plan,
        }
        missing = [key for key, value in required.items() if not isinstance(value, str) or not value.strip()]
        if missing:
            raise ValueError("proposal missing required fields: " + ", ".join(missing))
        if not isinstance(self.requested_transition, dict) or not isinstance(self.lineage, dict):
            raise ValueError("requested_transition and lineage must be objects")
        if not self.constraints:
            raise ValueError("proposal must state constraints explicitly")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "idempotency_key": self.idempotency_key,
            "actor_identity": self.actor_identity,
            "authority_reference": self.authority_reference,
            "requested_transition": self.requested_transition,
            "constraints": list(self.constraints),
            "evidence_bundle_ref": self.evidence_bundle_ref,
            "expected_vault_revision": self.expected_vault_revision,
            "policy_version": self.policy_version,
            "reversibility_plan": self.reversibility_plan,
            "lineage": self.lineage,
        }
