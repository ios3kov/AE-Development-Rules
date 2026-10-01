# UXP Engineering Checklist

## Target

- After Effects version:
- UXP/runtime version if available:
- Plugin version:
- Manifest version:
- Plugin ID:
- Build ID:
- Technology Lifecycle Status: `PREVIEW | BETA | GA | DEPRECATED | RETIRED`
- Lifecycle source ID / last verified date:

## Host support

- [ ] Technology Lifecycle Status checked against SOURCES.md
- [ ] PREVIEW/BETA use has documented acceptance + fallback/exit plan
- [ ] Required AE UXP APIs exist in target AE
- [ ] Min Version checked for every version-sensitive host API
- [ ] No capability inferred from another Adobe host without AE evidence
- [ ] Current Adobe AE UXP status/release notes reviewed

## Runtime

- [ ] No accidental browser-only API dependency
- [ ] No accidental Node-only runtime dependency
- [ ] TypeScript/framework bundle checked after build
- [ ] Runtime feature detection/fallback where required

## Async

- [ ] Promise rejections handled
- [ ] Timeouts defined for external I/O
- [ ] Host context revalidated after long await
- [ ] Stale async results rejected
- [ ] Duplicate invocation/re-entry semantics defined
- [ ] Cancellation/operation token used where needed
- [ ] Busy/error UI state defined
- [ ] Lifecycle callback work kept within documented UXP timeout
- [ ] Async lifecycle only used where current UXP entrypoint contract allows it

## Manifest / permissions

- [ ] host/minVersion correct
- [ ] entrypoints correct
- [ ] requiredPermissions minimal
- [ ] network domains minimal
- [ ] filesystem scope minimal
- [ ] IPC/process permissions justified
- [ ] Denied/revoked permission handled

## Lifecycle

- [ ] create
- [ ] show
- [ ] hide
- [ ] destroy
- [ ] reload
- [ ] AE restart
- [ ] listeners/timers do not duplicate
- [ ] critical safety does not depend on hide/destroy callbacks
- [ ] actual lifecycle behavior verified in target AE
- [ ] multi-panel lifecycle ambiguity tested where applicable
- [ ] command entrypoints do not assume persistent panel lifecycle

## Storage / network

- [ ] Persistent vs temp data correctly separated
- [ ] Stale/revoked file references handled
- [ ] HTTPS used where applicable
- [ ] Response schema/size validated
- [ ] Offline/timeout behavior defined

## Packaging / distribution

- [ ] Pure vs hybrid UXP identified
- [ ] Production package created as .ccx with supported Adobe tooling
- [ ] Plugin ID matches distribution channel
- [ ] No CEP ZXP signing requirement copied onto pure UXP CCX
- [ ] Hybrid .uxpaddon platform/architecture layout verified where applicable
- [ ] macOS hybrid .uxpaddon native binary signed/notarized where applicable
- [ ] Clean install tested through supported Creative Cloud Desktop / distribution flow

## Runtime tests

- [ ] Install/load through supported UXP tooling
- [ ] Panel reopen/reload
- [ ] Manifest change reload
- [ ] Permission grant/deny/revoke
- [ ] Network blocked/timeout where applicable
- [ ] Persistence across restart
- [ ] Concurrent/stale async scenario
- [ ] Diagnostics report host/runtime/plugin identity

## Sources

- https://developer.adobe.com/after-effects/uxp/
- https://developer.adobe.com/after-effects/uxp/after-effects-api/
- https://developer.adobe.com/uxp/guides/explanation/concepts/entrypoints/
- https://developer.adobe.com/uxp/guides/how-to/distribution/package/
- https://developer.adobe.com/uxp/
