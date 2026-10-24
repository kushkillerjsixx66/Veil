# Veil

**Veil (Ω-10), Liminal Boundary Regulator** is the independently versioned mediation environment between Vara observations, governed Lattice processes, and explicitly permitted external systems.

Veil is responsible for isolation, weak-signal incubation, evidence evaluation, and packaging proposals for governed transitions. It is not a canonical store and does not grant itself authority to mutate canonical state.

## Current status

**Bootstrap / design stage.** This repository currently contains architecture and migration documentation. The runtime has not yet been extracted from `canonical-vault`, runtime isolation is not established by this repository's existence, and no production-readiness claim is made.

## Responsibility boundaries

- **Vara:** observation, harvesting, normalization, clustering, drift detection, source provenance.
- **Veil:** mediation, isolation, incubation, evaluation, hold/reject/defer dispositions, evidence and proposal packaging.
- **Canonical Vault:** canonical records and revisions, authority/constraint enforcement, governed transitions, lineage and audit.

## Non-negotiable invariants

1. No direct canonical writes from Veil.
2. Recurrence is evidence, never authority or automatic promotion.
3. Corrupt, stale, ambiguous, or unverifiable state fails closed.
4. Rejected, expired, deferred, and superseded signals retain auditable history.
5. Network egress and credentials are explicitly scoped.
6. Every proposed transition carries provenance, policy version, expected Vault revision, idempotency key, and reversibility information.
7. A schema-valid proposal is not necessarily an authorized proposal.

## Documents

- [Architecture](docs/ARCHITECTURE.md)
- [Interface contracts](docs/INTERFACE_CONTRACTS.md)
- [Migration plan](docs/MIGRATION_PLAN.md)
- [Legacy runtime audit](docs/LEGACY_RUNTIME_AUDIT.md)
- [Threat model](THREAT_MODEL.md)

## Current implementation source

The existing legacy runtime is in [canonical-vault/05_runtime/vara_veil_vault.py](https://github.com/kushkillerjsixx66/canonical-vault/blob/main/05_runtime/vara_veil_vault.py). The older [05_runtime/veil.py](https://github.com/kushkillerjsixx66/canonical-vault/blob/main/05_runtime/veil.py) is a legacy primitive, not the live environment.

The legacy runtime is not yet conformant with the target boundary. Do not treat it as a production implementation or enable write-capable integration until the migration gates are satisfied.

## Status language

Use **proposed**, **implemented**, **tested**, **reviewed**, and **deployed** precisely. Documentation is not runtime enforcement; unit tests are not proof of network isolation; a repository boundary is not a security boundary.
