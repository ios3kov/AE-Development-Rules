# Static After Effects Compatibility Audit

## Target

- Product/component:
- Git commit:
- Build ID:
- SDK used to build (exact version/header revision):
- Final artifact SHA-256 / manifest:
- Audit scope / source inventory digest / omitted components:
- Target AE versions / scripting or panel runtime:
- Target platform:

## Source verification for new or changed API use

The normative contract is [Process §3](../../core/PROCESS.md#3-research-перед-разработкой). Record exact target-source support before relying on a newly used or changed host API. Reuse an existing current inventory for unchanged calls.

| API / suite / callback / flag | Exact declaration or contract / suite revision | Selected SDK header path or official doc section + version | Target availability and limitations | Verification date / unresolved question |
| --- | --- | --- | --- | --- |
| <actual identifier> | <checked signature/contract> | <actual source> | <AE/SDK/OS/runtime> | <result> |

Do not fabricate a declaration or infer host applicability from another Adobe product. Unresolved contracts block dependent design/implementation; independent authorized work can continue. Source confirmation and compilation do not establish runtime Compatibility: VERIFIED.

## Adobe API inventory

Run:

```sh
./starter-kit/scripts/scan-adobe-api.sh <source-dir>
```

| API / suite / revision / runtime capability | Used where / branch | Required or optional / fallback | Minimum documented AE build / SDK separately | Source revision/date / unresolved question |
| --- | --- | --- | --- | --- |
| <actual identifier> | <call site, wrapper or dynamic route> | <requirement and fallback> | <AE minimum; SDK revision; unknown if unconfirmed> | <checked header/doc, date, uncertainty> |

The scanner collects lexical native identifiers only. COMPLETE is collection scope, not a compatibility verdict. Record review of wrappers, indirect calls, generated/build dependencies and conditional paths separately. Audit JSX/CEP/UXP APIs and runtimes separately. Missing material availability/coverage remains UNKNOWN; do not infer minimum host version from the SDK label alone.

## Plugin metadata

- PiPL:
- Effect Spec Version:
- flags/capabilities:
- compile-time guards:
- SmartFX/MFR declarations:
- suite revisions:

## Binary/platform audit

- deployment target:
- architectures:
- linked frameworks/dylibs:
- weak/strong linking:
- external symbols:
- runtime dependencies:

## Baseline SDK build probe and fallback checks

- Minimum target AE / selected baseline SDK and why it is applicable:
- Toolchain / exact headers / build options / command / result / Evidence:
- Relationship of probe build to final distributed artifact; differences/limits:
- Missing API/suite/capability cases simulated / expected fallback or safe refusal:
- Actual adapter test observations / Test Status / Evidence:
- Unavailable checks / reason / next action:

Compilation is not runtime acceptance. Adapter/mock PASS covers decision logic only; do not alter installed AE or claim its old ABI/MFR/UI behavior was tested.

## Version-specific host behavior

Check lifecycle/callback ordering, MFR, SmartFX, Custom UI, AEGP, render queue/aerender, project-file ABI and known Adobe changes.

## Runtime selection and remote execution

- Exact minimum/current target AE versions/builds and additional API/behavior boundaries:
- Reason for each selected or omitted configuration:
- Link to [remote packet](REMOTE_COMPATIBILITY_CHECK.md) / actual run record:
- Actual runtime Evidence per officially supported version; no interpolation between endpoints:

## Result

| AE full version/build + OS/architecture | Candidate identity | Compatibility Status | Scope / Evidence / limitation |
| --- | --- | --- | --- |
| <actual configuration> | <commit, Build ID, SHA-256/manifest> | **VERIFIED / STATIC-COMPATIBLE / LIMITED / UNKNOWN / UNSUPPORTED** | <observations, omissions, reason> |

Static audit may estimate a minimum probably compatible version; only runtime AE evidence can establish Compatibility: VERIFIED. A sufficiently complete static-only result with no known blocker is Compatibility: STATIC-COMPATIBLE; material unknowns remain UNKNOWN. A specific confirmed blocker is UNSUPPORTED for that configuration.
