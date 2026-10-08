# Reference Evidence Obligations — implementation proposal

Status: PROPOSED. This is a conditional extension of REFERENCE_AUDIT.md, not a replacement for existing gates. No release or production deployment is authorized.

## Trigger
Apply when a concrete external product, binary, screen, API, or behavior is explicitly selected as a parity target. Otherwise N/A; do not add overhead to ordinary bug fixes.

## Obligation ledger
For each material target behavior, record:
- stable obligation ID, reference identity/version/artifact digest, scope and priority;
- exact observed input, preconditions, action, output, timing/state, platform and environment;
- evidence IDs, provenance, observation authority (static, runtime, packaged host/device), claim status PROVEN/OBSERVED/INFERRED/UNKNOWN;
- positive, negative, malformed, boundary, cancellation and recovery cases as applicable;
- implementation owner and revision/build identity, linked acceptance tests and fixture digests;
- verifier command, execution authority, actual result and artifact hash;
- dependencies, contradictions, residual unknowns, explicit allowed differences and next evidence needed.

## Closure rules
A required obligation is PASS only when all required cases have authenticated reference observations, implementation ownership, matching revision, and actual successful verifier results at a comparable authority level. Static analysis never proves runtime behavior; unit tests never prove native host/device execution. Unavailable evidence means BLOCKED or NOT_RUN, not PASS. A single green percentage cannot override any open P0 obligation. Deliberate exclusions need a recorded product decision and cannot silently disappear from coverage.

## Machine validation (next implementation)
Create a schema and fail-closed CLI validator for ledger JSON; connect it to the existing requirement-to-check/evidence lifecycle, without inventing a parallel evidence authority. Validate unique IDs, references, case completeness, owner identity, verifier authority, stale hashes, contradictions, and unresolved blockers. Emit machine-readable diagnostics and nonzero exit on failure. Add negative tests (missing case, stale build, fake pass, static-only runtime claim, duplicated owner, changed reference). CI must consume exit status, not prose or weighted parity score.

## Safe investigation
Use a least-privilege, read-only-first tool router for binary/mobile/browser research. Record exact tools and versions, permission boundaries, artifact hashes, timeouts and limits. Treat third-party binaries and browser content as untrusted. No DRM/access-control bypass or extraction of secrets. Only authorized analysis. Keep raw observations separate from AI interpretations.

## Visual and temporal parity
For UI: record navigation graph, empty/loading/error/offline states, screenshots with matching device/viewport/font/scaling, and region-level diffs. For AE: preserve alpha, bit depth, color management, host/render path; a thumbnail edge score cannot prove pixel parity. For event traces: compare ordering, cancellation, failure and recovery; report the first divergence with source evidence.

## Adoption stages
1. Add schema, fixtures, validator and negative tests.
2. Pilot on one authorized AE reference and one iOS reference; measure false passes, missed cases, effort and tool costs.
3. Integrate conditional routing and CI only after pilot results.
4. Extend to binary Ghidra, mobile and browser investigation profiles only when justified.

## Exit criteria
- No false PASS in adversarial fixtures.
- Every P0 obligation has actual verifier evidence or is explicitly blocked.
- Standard ordinary development remains unaffected when no reference trigger.
- Exact build, reference and verifier identities are reproducible.
