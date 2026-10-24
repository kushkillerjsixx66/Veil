# Veil Initial Threat Model v0.1

**Status:** Initial proposal; must be reviewed and updated against the actual deployment.

## Assets

- Source provenance and evidence integrity
- Incubated weak-signal records and their lineage
- Veil policy and evaluator versions
- Vault transition proposal integrity
- Service credentials and allowed egress destinations
- Audit events and recovery metadata

## Trust boundaries

- External systems and Vara observations into Veil
- Veil working state to proposal interface
- Veil service identity to Canonical Vault
- Runtime storage and outbound network
- Operators and deployment/release controls

## Threats and required controls

| Threat | Required control |
|---|---|
| Prompt injection embedded in observed content | Treat observations as data; no instruction execution from payload; adversarial tests |
| Recurrence used to force promotion | Recurrence affects evidence only; no automatic promotion |
| Unauthorized canonical mutation | No direct-write credentials; proposal-only interface; Vault-side authorization |
| Corrupt state interpreted as empty | Explicit integrity failure; preserve original bytes for investigation |
| Stale policy or Vault revision | Pin versions; reject stale proposals; re-evaluate |
| Replay or duplicate delivery | Stable request IDs, idempotency keys, replay detection |
| Concurrent updates / lost writes | Transactional storage or locking/version checks; race tests |
| Egress or credential exfiltration | Least-privilege credentials, network deny-by-default, runtime egress tests |
| Audit erasure | Append-only or retention-controlled event history; restricted deletion |
| Unsafe fallback during outage | Fail closed when required governance services are unavailable |
| Malicious or compromised dependency | Lockfiles, reviewed updates, provenance checks, reproducible CI where feasible |

## Assumptions to validate

- Actual runtime identity can be isolated from Vara and Vault credentials.
- The deployment platform can enforce outbound network restrictions.
- The Vault integration exposes a proposal path with independent authorization.
- Persistent working state supports integrity checks and safe concurrent updates.

If an assumption cannot be validated, mark the relevant capability unavailable rather than claiming protection.
