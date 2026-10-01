# User Protection / Security Checklist

## Inputs

- [ ] File paths/names treated as untrusted where applicable
- [ ] Imported text/JSON/config/preset validated
- [ ] IPC/bridge messages validated
- [ ] Network responses validated
- [ ] Size/count/range limits defined
- [ ] Timeouts/retry limits defined

## Filesystem

- [ ] Paths normalized/canonicalized before destructive operations
- [ ] Path traversal blocked
- [ ] Writes/deletes restricted to intended scope
- [ ] Symlink-sensitive destructive paths guarded
- [ ] User project/preferences not deleted by automation

## Command / code execution

- [ ] No shell command built by concatenating untrusted strings
- [ ] No external code/scripts executed without an explicit trusted mechanism
- [ ] Helper commands use constrained arguments/protocol
- [ ] Download/update artifacts have integrity/authenticity checks

## Permissions

- [ ] Least privilege used
- [ ] Permission denial handled safely
- [ ] Revoked/stale permissions handled
- [ ] Secrets not written to logs

## UI safety

- [ ] Destructive actions are clearly named
- [ ] Scope/consequences are visible before irreversible actions
- [ ] Dangerous ambiguous states fail closed
- [ ] No security-bypass instructions are required for normal installation
