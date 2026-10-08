# Host-independent Core / Testing Pyramid

## Architecture map

| Area | Pure core? | Host boundary? | Test level |
| --- | --- | --- | --- |
| Math/geometry | yes | no | unit/property |
| Parsing/validation | yes | no | unit/fuzz |
| State machine | preferably | minimal | unit/contract |
| CEP/UXP bridge | no | yes | contract + AE runtime |
| ExtendScript host mutation | no | yes | AE runtime |
| PF/AEGP callbacks | no | yes | native + AE runtime |
| GPU backend | partly | yes | parity + AE runtime |

## Pyramid

### 1. Pure unit tests

- no After Effects;
- deterministic;
- fast;
- same source/production artifact logic;
- edge/boundary/error cases.

### 2. Contract / adapter tests

- fake/mock host only for our own adapter/protocol behavior;
- malformed replies;
- timeouts;
- retries;
- stale state.

### 3. Integration tests

- packaging;
- serialization;
- bridge;
- filesystem boundary;
- generated artifacts.

### 4. Real After Effects tests

- real host API semantics;
- Undo;
- selection/project mutation;
- lifecycle;
- render;
- UXP/CEP runtime.

### 5. Release / compatibility

- exact final artifact;
- supported AE versions/platforms;
- install/update/uninstall;
- distribution security.

## Rules

- Mock PASS != AE runtime PASS.
- Do not keep a separately rewritten test-only copy of production logic.
- If transpiling ExtendScript/UXP code, test the produced artifact too.
- Do not introduce abstractions more complex than the feature only for testability.
- Micro-helpers may stay direct if the logic is truly trivial.

## Optional risk-scoped native extension (unreleased)

- Scope inventory: REVIEWED / UNREVIEWED / BLOCKED, source digest and [native review](NATIVE_REVIEW.md).
- Units: frame/second/fps, pixel/coordinate/scale, selected SDK integer channel scale versus float HDR; rounding/range/tolerance explicit.
- Property/fuzz: actual source, seed, bounded iterations/time, invariant and malformed corpus; preserve minimized counterexample.
- Original-defect regression: same check fails at expected assertion on original fixture and passes corrected bytes; setup failure is not red evidence.
- [Runnable C++17 fixture](../examples/native-core/README.md): buffer boundary, ownership cleanup, time/color conversions, parser/state properties, seed fuzz, compile-rejected wrong units.
- This finite offline suite does not exercise MFR, SmartFX, thread affinity, Adobe suites, alpha/color management or real host. Missing compiler is BLOCKED; host checks stay NOT RUN.
