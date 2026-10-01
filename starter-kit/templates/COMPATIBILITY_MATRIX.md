# Compatibility Matrix

| Component | Configuration | Status | Build ID | Date | Scope / Evidence / limitation |
| --- | --- | --- | --- | --- | --- |
| After Effects | <version> | **VERIFIED** | <id> | <date> | <runtime evidence> |
| After Effects | <version> | **API-COMPATIBLE** | <id> | <date> | <static audit only> |
| After Effects | <version> | **RISK / UNKNOWN** | <id> | <date> | <why> |
| After Effects | <version> | **UNSUPPORTED** | <id> | <date> | <concrete blocker> |
| macOS | <version / arch> | <status> | <id> | <date> | <scope> |
| Windows | <version / arch> | <status> | <id> | <date> | <scope> |

## Status rules

- **VERIFIED** = real runtime test in AE.
- **API-COMPATIBLE** = static audit found no known API/binary blocker; runtime test not done.
- **RISK / UNKNOWN** = version-specific behavior or insufficient evidence.
- **UNSUPPORTED** = concrete blocker exists.
