# Static After Effects Compatibility Audit

## Target

- Product/component:
- Git commit:
- Build ID:
- SDK used to build:
- Target platform:

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
| <version> | **VERIFIED / API-COMPATIBLE / RISK / UNKNOWN / UNSUPPORTED** | <evidence> |

Static audit may estimate a minimum probably compatible version; only runtime AE evidence can establish VERIFIED.
