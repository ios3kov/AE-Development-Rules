# Test Case: <ID> — <name>

## Purpose

- Requirement / risk:
- Component type: `native effect | script/panel | CEP/UXP | helper`
- Risk Profile: `Light | Standard | Critical`
- Delivery Gate: `Development | Validation | Release`
- Test type: `static | unit | integration | runtime AE | performance | distribution`

## Identity

- Git commit:
- Build ID:
- Artifact:
- Artifact SHA-256:
- AE version:
- OS / architecture:

## Preconditions

- Initial state:
- Fixture:
- Ownership proof:
- Required permissions:
- Cache state if relevant:

## Steps / runner

1. <step or versioned runner command>
2. <step>

## Expected result

- <observable expected behavior>
- Allowed tolerance if numeric/pixel comparison:

## Actual result

- <result>

## Status

**PASS / FAIL / BLOCKED / NOT RUN / N/A**

## Evidence

- <log / screenshot / video / render / profiler / hash>

## Cleanup / recovery

- <what the test may safely clean>
- <what must remain untouched>

## Limitations

- <what this test does not prove>

---

## Component-specific prompts

### Native effect / render plugin

Consider: default application, parameter boundaries, RAM Preview, Render Queue, aerender, SmartFX/MFR, 8/16/32 bpc, alpha/HDR, ROI/downsample, cancellation, repeated render, CPU/GPU parity, save/reopen, cache invalidation and extreme values.

### Script / ScriptUI panel

Consider: no project/comp/selection, wrong selection type, locked/deleted items, repeated execution, restart, exception/early return, Undo/Redo, cancel, corrupted state, Unicode paths/names and permissions.

### CEP / UXP

Consider: open/close/reload/restart, bridge validation, empty/malformed/delayed responses, timeout, retries, changed host context, permissions/sandbox, stale state, helper disconnect/recovery and loaded Build Identity.

### Helper / background process

Consider: startup/shutdown/crash recovery, IPC validation, malformed/oversized messages, path validation, duplicate instance, timeout/cancel, orphan cleanup and version mismatch.
