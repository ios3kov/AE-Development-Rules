# Cross-platform Porting Audit

## Product / target

- Product:
- Source platform:
- Target platform:
- Git commit:
- Build ID:
- Target AE versions:
- Target OS / architecture:

## Branch / architecture policy

- [ ] One shared main codebase remains the source of truth
- [ ] Temporary porting branch only, if needed
- [ ] Portable core separated from platform adapters
- [ ] No permanent macOS/Windows fork without documented necessity

## Inventory

| Area | Current dependency | Target equivalent | Status | Notes / evidence |
| --- | --- | --- | --- | --- |
| Build toolchain | <Xcode/clang> | <MSVC> | <status> | <notes> |
| Plugin packaging | <.plugin> | <.aex> | <status> | <notes> |
| Resources / PiPL | <source> | <target> | <status> | <notes> |
| Filesystem | <assumption> | <target behavior> | <status> | <notes> |
| IPC/process | <mechanism> | <target mechanism> | <status> | <notes> |
| Dynamic libs | <framework/dylib> | <DLL/import lib> | <status> | <notes> |
| Signing | <Apple Developer ID> | <Authenticode> | <status> | <notes> |
| GPU | <Metal/etc.> | <target> | <status> | <notes> |
| Installer/update | <mechanism> | <target> | <status> | <notes> |

Allowed status:

- **portable as-is**
- **platform adapter required**
- **rewrite required**
- **UNKNOWN / NOT VERIFIED**

## Shared acceptance contract

List user-visible behavior that must be identical across platforms.

| Behavior | macOS evidence | Windows evidence | Equivalent? |
| --- | --- | --- | --- |
| <behavior> | <evidence> | <evidence> | yes/no |

## Native AE checklist

- [ ] Correct target artifact type (.plugin / .aex)
- [ ] Adobe entry points exported
- [ ] PiPL/resources valid
- [ ] Architecture verified
- [ ] Runtime dependencies verified
- [ ] Unicode/path behavior verified
- [ ] MFR/SmartFX verified where claimed
- [ ] Render Queue / aerender verified where claimed
- [ ] 8/16/32 bpc verified where claimed
- [ ] Runtime Build Identity verified
- [ ] Compatibility matrix updated

## Result

- Minimum target platform status:
- Remaining blockers:
- Runtime tests still required:
