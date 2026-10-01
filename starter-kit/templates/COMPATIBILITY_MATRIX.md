# Compatibility Matrix

Use only **Compatibility Status** from `DEVELOPMENT_RULES.md §10`.

| Component | Configuration | Compatibility Status | Build ID | Date | Scope / Evidence / limitation |
| --- | --- | --- | --- | --- | --- |
| After Effects | <version> | **VERIFIED** | <id> | <date> | <runtime evidence> |
| After Effects | <version> | **STATIC-COMPATIBLE** | <id> | <date> | <static audit only> |
| After Effects | <version> | **LIMITED** | <id> | <date> | <verified limited scope> |
| After Effects | <version> | **UNKNOWN** | <id> | <date> | <why evidence is insufficient> |
| After Effects | <version> | **UNSUPPORTED** | <id> | <date> | <concrete blocker> |
| macOS | <version / arch> | <status> | <id> | <date> | <scope> |
| Windows | <version / arch> | <status> | <id> | <date> | <scope> |

## Status rules

- **VERIFIED** = real runtime test in the stated scope.
- **STATIC-COMPATIBLE** = static audit found no known API/binary blocker; runtime test not done.
- **LIMITED** = only the documented subset is verified/supported.
- **UNKNOWN** = evidence is insufficient.
- **UNSUPPORTED** = a concrete blocker exists.

Do not put Test Status or Evidence Confidence values in the Compatibility Status column.
