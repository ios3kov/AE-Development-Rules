# Compatibility Matrix

Technology Lifecycle Status is tracked separately from Compatibility Status; do not merge them into one value.

Use only **Compatibility Status** from `core/PROCESS.md §10`.

| Component | Configuration | Compatibility Status | Build ID | Date | Scope / Evidence / limitation |
| --- | --- | --- | --- | --- | --- |
| After Effects | <full AE version/build + OS/architecture> | **VERIFIED** | <id> | <date> | <runtime evidence> |
| After Effects | <full AE version/build + OS/architecture> | **STATIC-COMPATIBLE** | <id> | <date> | <static audit only> |
| After Effects | <full AE version/build + OS/architecture> | **LIMITED** | <id> | <date> | <verified limited scope> |
| After Effects | <full AE version/build + OS/architecture> | **UNKNOWN** | <id> | <date> | <why evidence is insufficient> |
| After Effects | <full AE version/build + OS/architecture> | **UNSUPPORTED** | <id> | <date> | <concrete blocker> |
| macOS | <version / arch> | <status> | <id> | <date> | <scope> |
| Windows | <version / arch> | <status> | <id> | <date> | <scope> |

## Status rules

- **VERIFIED** = real runtime test in the stated scope.
- **STATIC-COMPATIBLE** = static audit found no known API/binary blocker; runtime test not done.
- **LIMITED** = only the documented subset is verified/supported.
- **UNKNOWN** = evidence is insufficient.
- **UNSUPPORTED** = a concrete blocker exists.

Do not put Test Status or Evidence Confidence values in the Compatibility Status column.

## Evidence and selection

Follow [Engineering §21](../../core/ENGINEERING.md#21-совместимость-и-применимость-технологий). All target hosts need not be installed locally; [remote runtime evidence](REMOTE_COMPATIBILITY_CHECK.md) can establish the tested scope.

- Candidate commit, Build ID, final SHA-256 / package manifest:
- Links to [API/source + binary audit](API_COMPATIBILITY_AUDIT.md) and scope/coverage limits:
- Chosen minimum/current targets and additional version/build boundaries; rationale:
- Omitted configurations and uncertainty / condition for execution:
- Per-run Test Status and actual installed/loaded identity in linked test records:

Do not turn two endpoint tests into a VERIFIED interval. Each officially supported version needs actual runtime evidence for the stated scope. Do not carry a result to another artifact/host/OS/architecture automatically. Missing required runtime execution remains BLOCKED / NOT RUN in the test record; it is not a Compatibility Status. Mock/compile/collector PASS alone never establishes VERIFIED.
