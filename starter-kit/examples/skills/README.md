# Agent skill byte-management fixtures

`owned-package` is original synthetic test data. It is not an externally installed
skill, an Adobe SDK checker, a security certificate, or measured agent Evidence.
No approved policy is shipped: candidate-authored approval would defeat the trust
boundary. Source hashes in tests are synthetic identities, not upstream commits.

Python 3.11+ is sufficient. From the repository root:

```sh
python3 starter-kit/scripts/agent_skills.py inventory --package starter-kit/examples/skills/owned-package
python3 starter-kit/scripts/agent_skills.py scan --package starter-kit/examples/skills/owned-package
python3 -m unittest discover -s starter-kit/tests -p test_agent_skills.py
```

Admission uses an independently maintained policy matching
`starter-kit/schemas/agent-skills-policy.schema.json`. The trusted caller supplies
SHA256 of its **raw file bytes**, the exact candidate revision and source commit;
the candidate must not select the policy or its expected digest. The policy is
outside the candidate checkout (`--candidate-root`) and installation scope.
Protected policy custody is an operational prerequisite; a command-line pin by
itself does not authenticate an identity or establish GitHub protections.

Lifecycle states apply to exact `(name, package_sha256)` versions. A policy may
retain a revoked old version alongside an allowed replacement. Every activation
needs status `allowed`, current independent approval, a complete independent scan
receipt covering exact files/bytes/modes, scanner version/config/check IDs and no
errors/omissions. Unknown licenses or nonempty bypass exceptions are BLOCKED.
A stale receipt never validates newly restored bytes. Mandatory scan remains
required when telemetry is false. An empty heuristic finding list is not safety.

`check --package ... --source-commit ... --policy ...
--expected-policy-sha256 ... --expected-candidate-revision ...
--candidate-root ...` performs admission consistency. Workflow callers must
validate actual candidate Git HEAD themselves using their trusted checkout.
`select` loads only protected description/purpose metadata for an explicit task
and available tool list; it returns CANDIDATE, never an activation approval.
`load` rechecks exact bytes and admission, requires `--task`, all required
`--available-tool` values and one `--resource` path. It does not load unrelated
resources or execute scripts/hooks/MCP. Resource content is marked untrusted.

`install`/`update` require a user-selected `--install-root`, `--owner`, package,
source revision and independently pinned policy. They manage original package
bytes in one owner scope, not global agents' config. Atomic exclusive directory
locks serialize cooperating lifecycle operations; a stale lock is BLOCKED and
requires explicit recovery after checking the recorded PID/owner. No automatic
stale-lock deletion occurs. Update verifies current and restored inventories,
then retains the previous exact bytes under `.history/NAME/DIGEST/NAME`.
`rollback` requires `--name` and `--target-digest` and current independent admission
of that exact historical version; a revoked version cannot activate. `remove`
needs owner and name and refuses modified/foreign files. Historical bytes are
preserved; deletion of unknown/history material is outside this tool's scope.
The lock and owner marker are conflict controls, not protection against a hostile
local process with filesystem rights.

`import` accepts **local ZIP only** and never fetches network content. It refuses
existing destinations, traversal/absolute/Windows-reserved paths, symlinks and
other special files, hardlinks in local packages, duplicates/case/unicode aliases,
encryption, special permission bits, compression bombs, more than 1000 entries,
files above 4 MiB and packages/archives above 20 MiB. Import is byte inspection;
it does not grant admission. Package SHA256 seals sorted file records
`{path,size,sha256,mode}` and sorted directory paths, including empty directories.
Directory permissions are not part of the package contract. Restored file modes
and bytes are rechecked on the target filesystem; incompatible modes fail closed.

Only `static-read-only` inspection is supported. An execution/isolation profile
requires an enforcing external adapter; requesting it here is BLOCKED. Temporary
use, textual allowed-tools and instructions do not enforce a sandbox. Complex
valid YAML requiring a full YAML parser is BLOCKED by the portable subset parser,
not declared incompatible with Agent Skills. An adapter may use the standard
parser while preserving the standard SKILL.md bytes and package digest.

Formats are new optional adapter records; no existing project/Evidence schema is
changed. Adoption does not rewrite published 9.0.0 records. On schema changes,
retain old Evidence as historical and regenerate approval/scan for changed bytes
or policy. Root canonical rules and existing Evidence remain the sole authority;
agent adapters reference them instead of managing a second divergent rule copy.
