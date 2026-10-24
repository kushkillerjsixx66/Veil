# Legacy Veil Runtime Audit v0.1

**Status:** Implementation inventory, non-canonical  
**Observed:** 2026-10-24  
**Source repository:** `kushkillerjsixx66/canonical-vault`  
**Live runtime blob:** `f522bef65bcfd47613df6b41f586daf4a4b7b09b`  
**Test blob:** `bdac25343ba67090e463a5030544c0c3809f2788`

## Finding summary

The current live module is a legacy Vara signal router backed by whole-file JSON stores. It is not yet an independently isolated Veil environment and must not be copied into this repository unchanged.

| Severity | Location | Observed behavior | Required treatment |
|---|---|---|---|
| Critical | `run_veil`, around lines 134–200 | Consecutive recurrence at threshold 2 sets status to PROMOTED and routes the signal onward | Remove automatic promotion; recurrence may only add evidence |
| Critical | `route_signals`, `commit_to_vault` | Signals route into the legacy JSON signal store, not a verified governed transition request | Replace with proposal-only interface; Vault independently validates |
| High | `load_veil_hold`, lines 97–124 | Parse/type/key errors return an empty dictionary | Fail closed with explicit integrity error; preserve corrupt input for investigation |
| High | `load_vault`, lines 220–228 | Parse/value errors return an empty list | Fail closed; never interpret corruption as an empty canonical-like store |
| High | `run_veil`, line 200 | EXPIRED and PROMOTED records are removed from persisted hold state | Preserve terminal history under explicit retention policy |
| High | `save_veil_hold`, `save_vault`, `canonize_vault_entry` | Whole-file JSON rewrites have no demonstrated multi-process concurrency control | Use transactional storage and test concurrent writers |
| High | `canonize_vault_entry`, lines 342–372 | Local JSON canonicalization rewrites a canon file | Remove from Veil; canonicalization belongs behind governed Vault transitions |
| Medium | `VeilEntry` and report dataclasses | Legacy status model includes PROMOTED as a recurrence-driven lifecycle state | Replace with explicit non-authoritative dispositions and externally governed outcomes |
| Medium | `test_vara_identity.py` | Existing lifecycle tests encode recurrence promotion and hold-store removal | Replace assertions with parity, retention, idempotency, corruption, and no-authorization tests |

## Dependencies and integration risks

- The module imports `_compute_signal_id` from `vara_harvesters`. The new Veil package must define or consume a versioned identity contract rather than rely on a private Vara helper.
- The Canonical Vault's `05_runtime/vault.py` exposes a governed transition path and explicitly blocks unguarded direct writes. The Veil adapter contract must be checked against the current implementation before integration.
- The governance engine's existence is not proof that the legacy router invokes it. No such invocation was observed in the audited legacy routing path.
- The older `05_runtime/veil.py` is only a minimal `filter(pulse)` primitive and is not the live mediation implementation.

## Migration rules

1. Preserve source IDs, observation IDs, signal IDs, timestamps, and lineage when importing legacy records.
2. Do not automatically convert legacy PROMOTED records into accepted canonical records. Their historical status is evidence of prior behavior, not proof of current authorization.
3. Quarantine malformed legacy files for explicit review; do not normalize them into empty state.
4. Run import in dry-run mode and report counts, collisions, malformed records, and unresolved lineage before any persistent migration.
5. Keep the old runtime available for forensic comparison until cutover is explicitly authorized.
6. Do not enable write-capable integration while any direct JSON canonicalization or recurrence-driven promotion path remains reachable.

## Current new-repository implementation

The initial Veil package adds a transactional SQLite working-state ledger, typed observation and proposal models, and tests for held-by-default behavior, recurrence without promotion, duplicate-observation idempotency, and fail-closed identity collision handling. This is a bounded starting point, not yet a complete replacement for the legacy runtime. The CI result must be checked on the current branch before describing tests as passing.

## Non-actions

This audit does not change canonical policy, authorize a Vault write, ratify a Veil spec, or authorize production deployment.
