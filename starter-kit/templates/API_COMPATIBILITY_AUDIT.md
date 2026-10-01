# Static After Effects Compatibility Audit

## Target

- Product/component:
- Git commit:
- Build ID:
- SDK used to build:
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

| API / suite / revision | Used where | Minimum documented AE/SDK | Risk / notes | Source |
| --- | --- | --- | --- | --- |
| <name> | <file/function> | <version> | <notes> | <Adobe doc/header> |

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

## Version-specific host behavior

Check lifecycle/callback ordering, MFR, SmartFX, Custom UI, AEGP, render queue/aerender, project-file ABI and known Adobe changes.

## Result

| AE version | Status | Reason |
| --- | --- | --- |
| <version> | **VERIFIED / STATIC-COMPATIBLE / LIMITED / UNKNOWN / UNSUPPORTED** | <evidence> |

Static audit may estimate a minimum probably compatible version; only runtime AE evidence can establish Compatibility: VERIFIED. A static-only result is Compatibility: STATIC-COMPATIBLE.
