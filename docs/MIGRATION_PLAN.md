# Veil Runtime Extraction and Migration Plan v0.1

**Status:** Proposed, non-canonical. No runtime relocation, deployment, or authority change is authorized by this document.

## Source baseline

- Live legacy runtime: [canonical-vault/05_runtime/vara_veil_vault.py](https://github.com/kushkillerjsixx66/canonical-vault/blob/main/05_runtime/vara_veil_vault.py)
- Legacy primitive: [canonical-vault/05_runtime/veil.py](https://github.com/kushkillerjsixx66/canonical-vault/blob/main/05_runtime/veil.py)
- Architecture proposal: [canonical-vault/VEIL_ENVIRONMENT_ARCHITECTURE_SPEC_v0.1.md](https://github.com/kushkillerjsixx66/canonical-vault/blob/chatgpt/04_system_spec/VEIL_ENVIRONMENT_ARCHITECTURE_SPEC_v0.1.md)
- Conformance matrix: [canonical-vault/VEIL_ENVIRONMENT_CONFORMANCE_MATRIX_v0.1.md](https://github.com/kushkillerjsixx66/canonical-vault/blob/chatgpt-veil-env-conformance-v01/04_system_spec/VEIL_ENVIRONMENT_CONFORMANCE_MATRIX_v0.1.md)

Re-fetch source revisions before implementation. The legacy runtime is not yet conformant: it automatically promotes after consecutive recurrence and routes signals through legacy JSON persistence; its old behavior must not be copied as the target policy.

## WP-0: Repository foundation

- Keep this repository named **Veil**.
- Maintain independent versioning, CI, security policy, threat model, and reviewed release process.
- Review repository visibility. This repository is currently public; confirm no secrets, sensitive operational data, or restricted artifacts are committed before adding runtime material.
- Define branch protection and required checks.

## WP-1: Inventory and characterize

- Inventory callers, imports, data files, environment variables, and all uses of `vara_veil_vault.py`, `veil.py`, legacy signal storage, and canon JSON.
- Record current tests and data migration requirements.
- Identify every direct-write and recurrence-promotion path as a blocker.
- Do not merge the interim hardening PR merely to facilitate extraction.

## WP-2: Extract a bounded core

- Move Veil-specific lifecycle, evaluation, persistence, and tests to this repository on a feature branch.
- Replace repository-relative imports with explicit public interfaces.
- Preserve signal IDs, source references, and lineage.
- Do not silently migrate or discard existing held, expired, rejected, or promoted records.
- Add a compatibility adapter only if required, with explicit deprecation and shutdown criteria.

## WP-3: Remove unsafe legacy semantics

- Recurrence changes evidence only; it never authorizes or automatically promotes.
- Corrupt state must raise an explicit integrity error, never silently become an empty store.
- Preserve expired and rejected records under retention policy.
- Use safe atomic persistence and explicit concurrency control; atomic replace alone does not prevent lost updates across processes.
- Canonicalization must never be implemented as a local JSON rewrite.

## WP-4: Governed Vault integration

- Verify the current Vault transition API and its schemas before writing the adapter.
- Veil can submit proposals only; the Vault independently checks authority, constraints, source integrity, revision freshness, lineage, and reversibility.
- Scope credentials so they cannot call direct-write or canonicalization endpoints.
- Use idempotency keys and reconcile unknown timeout outcomes before retrying.

## WP-5: Runtime isolation

- Run Veil as a separate process/service with a distinct identity and minimal credentials.
- Separate working-state storage from canonical storage.
- Deny network egress by default; allowlist required endpoints and data classes.
- Test prompt injection in observations, replay, stale revisions, duplicate delivery, concurrent updates, corrupt persistence, credential leakage, and network egress denial at the runtime layer.

## WP-6: Shadow mode and cutover

- Run observation-only and shadow evaluation first.
- Compare outputs with the existing runtime and review divergences.
- Require contract, adversarial, recovery, and integration tests to pass.
- Cut over only after explicit operator review and release authorization.
- Demonstrate rollback without deleting or rewriting canonical audit history.

## Acceptance gates

- [ ] CI and dependency pins exist.
- [ ] No direct canonical write path or credential exists in Veil.
- [ ] Recurrence cannot trigger promotion or authorization.
- [ ] Corrupt persistence fails closed and is not overwritten silently.
- [ ] Stale revisions, ambiguous authority, missing provenance, and unavailable governance checks block release.
- [ ] Duplicate requests are idempotent and concurrent updates are safe or rejected.
- [ ] Expired, rejected, deferred, withdrawn, and superseded records retain audit history.
- [ ] Egress restrictions are tested outside unit mocks.
- [ ] Shadow-mode divergences are reviewed.
- [ ] Rollback is demonstrated and release is explicitly authorized.

## Governance boundary

This plan does not ratify a Veil specification, amend canon, authorize runtime mutation, or grant Veil authority to mutate canonical state. Those are separate decisions. The Canonical Vault remains authoritative for canonical records and governed transitions.
