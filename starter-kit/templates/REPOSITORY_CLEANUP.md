# Safe repository cleanup plan and report

Canonical contract: [Process §6](../../core/PROCESS.md#безопасная-уборка-репозитория-после-разработки), safety boundary §4 and Smart Entry §4.1. This form is a plan until actual observations/actions are recorded. Embed it in an existing checkpoint for small scopes. No invented cleanup work, blanket deletion, history rewrite, merge/publication or automatic backup purge.

## Scope and initial state

- Task / operator / date / authorization source and permitted actions:
- Repository/worktree / branch / HEAD / actual staged/unstaged state:
- Allowed canonical roots and file types / excluded paths:
- Untracked/ignored materials inventory / parallel owners and active scopes:
- Objective / budget / acceptance criteria / pre-release or post-release stage:
- Frozen/released artifacts and Evidence to preserve (identity/hash/reference):
- No-op rationale if nothing requires cleanup:

## Reviewed plan — before mutation

| Item | Exact original path / type / expected hash or manifest | Owner / active-use evidence | Operation / reason / scope permission | Dependency and path checks | Recovery / retained destination | Actual action or skip reason |
| --- | --- | --- | --- | --- | --- | --- |
| <ID> | <actual path and state> | <proof or unknown> | <delete/move/keep, not yet executed> | <links/build/loader/real ancestors> | <verified copy or reproducibility evidence> | <planned until actual action> |

Review the list without running mutations. Unknown ownership, purpose, dependencies, permission or recovery means KEEP IN PLACE, not move-to-archive. Dry-run output is not permission or proof. Do not expose secret contents or commit sensitive inventory/backups.

## Preservation and immediate pre-operation checks

- Valuable source/settings/user data/fixtures/decisions/Evidence/release assets identified:
- Backup outside cleanup area and plugin/build/release discovery paths:
- Copy coverage: tracked/untracked/ignored, bytes/types/links/essential permissions:
- Backup verification / critical restore rehearsal / owned restore destination:
- Build-output reconstruction evidence: source, dependency availability, SDK/toolchain, settings, actual result:
- Exact source/path/ancestors/content/type/ownership/use rechecked just before action:
- Agreed writer pause/isolation if needed; limits of race protection:
- Destination absent/no overwrite; move dependencies and active references checked:

If a planned item changes, skip and reassess it. If concurrent mutation cannot be excluded safely, do not perform the destructive action. A private lock does not prove that other writers comply.

## Branch/worktree closure where applicable

- All needed commits/changes preserved in target or verified retained snapshot:
- Squash/cherry-pick content preservation checked if ancestry alone is insufficient:
- Unique commits/refs, staged/unstaged/untracked/ignored files reviewed:
- No active owner/process relying on the worktree; embedded repositories/submodules reviewed:
- Managed archive procedure/result / retained identity / recovery route:

Do not remove managed worktree directories manually. Closing this task does not authorize deleting another task, a backup or published tags.

## Execution and verification — actual observations only

- Action journal (paths/items, observed state, timestamp, outcomes/partial failures):
- Unknown-outcome reconciliation before any retry; changed items left in place:
- Documentation/current-status updates; historical provenance retained:
- Final diff and filesystem changes match reviewed plan:
- Links/dependent scripts and affected scenarios checked:
- Clean isolated build if structure changed:
- Frozen/released artifact/Evidence identity unchanged:
- Recovery performed if needed; newer work preserved:

| Check / scope | Expected | Actual | Test Status | Evidence / limitation |
| --- | --- | --- | --- | --- |
| <actual check> | <criterion> | <none until execution> | NOT RUN | <reason/condition> |

Use canonical Test Status; a skipped cleanup item is not a passed test. Do not claim complete cleanup or recovery from a clean Git status.

## Handoff and retention

- Completed/deferred items and exact reasons:
- Commit / actual working state / verified checks and remaining blockers:
- Retained backup/archive paths and tested restoration procedure:
- Separate retention owner, period/condition and deletion authorization:
- Next concrete action or no further necessary work:

Planning is not execution. Move/archive can break the project; unknown materials remain at the original path. Retention expiry is not automatic purge permission. Never alter an already frozen/published artifact to make cleanup appear complete.
