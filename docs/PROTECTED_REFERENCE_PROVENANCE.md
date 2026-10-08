# Protected reference observation provenance

Status: conditional experimental protocol. Does not claim any real AE/iOS observation.

## Trust boundary
The implementation agent MUST NOT be the sole authority for its own evidence. A separate trusted runner or reviewer owns the capture manifest, immutable observation files and verification results. Candidate PRs may propose evidence, but cannot approve or overwrite the protected baseline. Content digests establish integrity relative to a manifest, not truth of observation.

## Capture record
For each observation capture: reference artifact SHA-256, source version, exact platform/device/host and build, scenario and case IDs, command/tool and version, UTC time, environment, raw output file SHA-256, runner identity, run ID, and reviewer decision. Record privacy-safe redactions and any inaccessible capability.

## Independent acceptance
1. Trusted reviewer verifies scope/authorization and reference identity.
2. Trusted runner executes or reviewer directly witnesses the claimed scenario.
3. Capture manifest and raw evidence are stored outside candidate-write permissions.
4. Verification compares candidate evidence IDs, artifact digests, and observation authority to protected manifest.
5. Any missing, stale, contradictory, untrusted or unwitnessed required evidence is BLOCKED.
6. Host/device claims require actual host/device observation; simulation is not sufficient.

## Integration boundaries
The starter-kit reference ledger validator verifies JSON structure, inventory coverage and local artifact hashes. It **does not** implement trusted runner identity, signature validation, external provenance or reviewer approval. Do not mark those controls PASS until implemented and exercised against negative fixtures (forged capture, substituted manifest, replayed old run, changed artifact, unauthorized reviewer).

## Pilot acceptance
AE: an authorized plugin/effect in real After Effects with a pinned host version and render fixtures.
AS: an authorized app on a real iPhone with pinned OS/build, cold-start, interruption, permission and recovery cases.
Keep synthetic CI PASS separate from host/device pilot results. Do not merge a claim of end-to-end parity on synthetic evidence alone.
