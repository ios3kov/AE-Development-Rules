# Crash Diagnostics / Symbols Record

## Release identity

- Product/version:
- Git commit:
- Build ID:
- Artifact SHA-256:
- Platform/architecture:
- Toolchain/profile:

## Symbols

### macOS

- dSYM path/storage ID:
- UUID:
- Retention policy:

### Windows

- PDB path/storage ID:
- Binary/PDB match evidence:
- Retention policy:

### Other

- map files / symbol server:
- identifiers:

## Crash handling

- Crash report contains Build ID or equivalent: yes/no
- Symbolication procedure:
- Privacy/redaction procedure:
- User consent/telemetry notes:

## Production crash workflow

1. Identify exact build.
2. Symbolicate.
3. Minimize/reproduce when possible.
4. Add regression coverage.
5. Verify fix on identified artifact.
