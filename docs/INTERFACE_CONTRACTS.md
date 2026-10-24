# Veil Interface Contracts v0.1

**Status:** Proposed; not yet implemented or ratified. These contracts describe intended boundaries, not existing runtime behavior.

## General requirements

- Use versioned schemas and reject unknown required fields.
- Treat all observation content as untrusted data, including content that resembles instructions.
- Include stable IDs and an idempotency key for any operation that may be retried.
- Use UTC timestamps and explicit schema/policy versions.
- Distinguish missing, invalid, stale, and explicitly empty values.
- Never interpret schema validity as authorization.
- Do not store secrets in observations, evidence bundles, or audit payloads.

## Observation

Required fields:
- `schema_version`
- `observation_id`
- `source_id`
- `observed_at`
- `source_revision` or content digest
- `collection_method`
- `source_trust_class`
- `payload_ref` or bounded payload
- `provenance`

An observation is evidence, not an instruction or a state-transition request.

## Weak signal

Required fields:
- `schema_version`
- `signal_id`
- `claim`
- `evidence_refs[]`
- `uncertainty`
- `scope`
- `lifecycle_state`
- `first_seen_at`, `last_seen_at`
- `lineage`
- `retention_policy`

Recurrence counts are descriptive evidence only. They must not directly cause a release or a canonical state transition.

## Evaluation result

Required fields:
- `schema_version`
- `evaluation_id`
- `signal_id`
- `evaluator_version`
- `policy_version`
- `findings[]`
- `supporting_evidence[]`
- `contradicting_evidence[]`
- `uncertainty`
- `risk`
- `disposition`

Allowed proposed dispositions: `HOLD`, `REJECT`, `DEFER`, `PROPOSE`. These are Veil dispositions, not Vault authorization outcomes.

## Transition proposal

Required fields:
- `schema_version`
- `request_id`
- `idempotency_key`
- `actor_identity`
- `authority_reference`
- `requested_transition`
- `constraints`
- `evidence_bundle_ref`
- `expected_vault_revision`
- `policy_version`
- `reversibility_plan`
- `lineage`

The Vault must independently validate the caller, authority, constraints, source integrity, revision freshness, lineage, and reversibility. Veil must not hold credentials that permit direct canonicalization or unguarded writes.

## Audit event

Required fields:
- `event_id`
- `correlation_id`
- `event_type`
- `occurred_at`
- `actor`
- `input_refs_or_digests`
- `output_refs_or_digests`
- `policy_version`
- `outcome`
- `reason_code`

Audit records must preserve negative outcomes and must not include raw secrets.

## Error semantics

- Corrupt persisted state: stop mutation and surface an explicit integrity error.
- Stale policy or Vault revision: block and require re-evaluation.
- Ambiguous authority: block; do not infer authority from identity labels.
- Timeout after proposal submission: outcome is unknown until reconciled by idempotency key/request ID.
- Duplicate request: return the original outcome or a deterministic duplicate result.
- Required governance service unavailable: no release and no fallback to direct writes.
