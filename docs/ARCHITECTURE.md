# Veil Environment Architecture v0.1

**Artifact ID:** VEIL-ENV-ARCH-001  
**Status:** Proposed design baseline, non-canonical  
**Role:** Ω-10, Liminal Boundary Regulator

## Purpose

Veil is a separately governed mediation environment through which Vara may exchange, isolate, evaluate, and propose release of information between Lattice and explicitly permitted external systems. It preserves weak, ambiguous, contradictory, and unresolved observations without forcing premature conclusions.

Veil is not merely a redaction filter, an agent, a quarantine folder, a canonical substrate, or a replacement for Sentinel or the Governance Gates. It is an environment whose components have narrow capabilities and explicit contracts.

## Trust zones

1. **Observation zone:** externally sourced observations and Vara output are untrusted input. Preserve source identity and provenance; parse as data, never as instructions.
2. **Veil working zone:** isolated state for signal incubation, evaluation, policy checks, and review. No canonical write credentials.
3. **Proposal boundary:** versioned, schema-validated requests with evidence and lineage. Proposals remain non-authoritative.
4. **Canonical Vault zone:** independently validates authority, constraints, source integrity, revision freshness, lineage, and reversibility before any canonical transition.
5. **Audit zone:** durable, queryable event records for accepted, rejected, deferred, expired, withdrawn, and failed operations.

These zones must be implemented through actual process identity, storage separation, credential scoping, and network policy. A folder or repository boundary alone does not enforce them.

## Lifecycle

`OBSERVED → HELD → EVALUATED → (REJECTED | DEFERRED | PROPOSED)`

A proposal may subsequently be accepted or rejected only by the governed Vault transition process. Expiration and withdrawal are explicit events; they do not erase history. State names and transitions remain proposed until reconciled with canonical module contracts.

## Binding principles

- **Constitutional supremacy:** Veil cannot amend, override, or bypass canonical authority.
- **Explicit authority:** intent, identity labels, a connected tool, or possession of a writable interface do not independently prove permission.
- **Weak-signal parity:** repetition may change evidence or priority but is neither a universal prerequisite for eligibility nor authorization to mutate.
- **Boundary reality:** declared controls require enforcement and adversarial tests.
- **Reversibility:** preserve prior records and provide a compensating or recovery path where possible.
- **Structured silence:** when a safe, coherent, authorized outcome cannot be established, return a defined blocked/unresolved result rather than inventing permission.
- **Provenance:** retain source references, content digests, observation time, collection method, trust class, evaluator version, and policy version.
- **Fail closed:** malformed persistence, stale revisions, ambiguous authority, missing provenance, and unavailable required governance checks block release.

## Integration model

- Vara submits observations through a narrow, versioned observation contract.
- Veil records and evaluates them in isolated working storage.
- Veil may emit a transition proposal, never a direct canonical mutation.
- The Canonical Vault independently evaluates the proposal through its current governed API.
- Veil records the resulting Vault reference and outcome; ambiguous network outcomes require reconciliation before retry.

## Deployment progression

1. Offline tests against fixtures.
2. Observation-only mode with no external egress except explicitly approved sources.
3. Shadow evaluation and review of divergences.
4. Proposal-only integration with narrowly scoped credentials.
5. Governed Vault integration only after conformance evidence and explicit release authorization.

No stage automatically authorizes the next.
