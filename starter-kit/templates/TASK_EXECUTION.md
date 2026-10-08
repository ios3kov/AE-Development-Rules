# Optional task execution contract (unreleased)

Embed in the existing checkpoint/plan. [Process §5](../../core/PROCESS.md#контракт-задачи-и-объединённый-candidate-unreleased) extends existing parallelism and task reconciliation; a single small task does not require another file, second agent or tracker.

| Task ID | Owner | Depends on / actual readiness | Allowed files/subtrees | Observable acceptance | Budget unit/limit/spent | Result / candidate / Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| <task> | <one owner> | <met prerequisites or scoped blocker> | <repository-relative paths> | <requirement/check> | <bounded time/iterations etc> | <changed paths, outcome, limits> |

| Shared resource kind/key | Tasks | read/exclusive | Actual isolation or serial owner | Release condition |
| --- | --- | --- | --- | --- |
| <device/cache/output> | <IDs> | <mode> | <owned session or separate directory> | <actual condition> |

A row is not an OS lock or action permission. Device/session identity must be actual, cache/output roots canonical, aliases resolved by the owner before recording. A budget is not authorization for paid execution. Do not schedule overlapping writers/leases concurrently. READY in the optional machine format means reserved for concurrent execution, not a backlog item waiting for the same lease.

- Combined candidate identity after integrated work:
- Reviewed required integration check IDs, actual reruns and current Evidence:
- Separate [spec / quality review](IMPLEMENTATION_REVIEW.md):
- Original-defect regression sensitivity, if applicable:
- Remaining blockers and independent allowed work (reuse existing stop criteria):

Optional JSON schema: `../schemas/task-execution.schema.json`; Python 3.11+ validator:

```sh
python3 starter-kit/scripts/check_task_execution.py --record TASK.json --evidence-root PROJECT --expected-candidate FULL_SHA --required-check CHECK_ID
```

Repeat `--required-check` for the complete affected check set supplied by the trusted check owner. Evidence records include candidate, contained regular path and SHA-256; delegation results may refer to their earlier source candidate, integration PASS must refer to the final combined candidate. The validator checks actual bytes and record consistency, not actual command execution, signature/independence, permissions, file locking or host readiness. Use the existing Evidence lifecycle and protected verifier boundary; never run candidate-supplied validator as an independent gate.

This additive v1 format is opt-in. Existing Markdown checkpoints remain valid. When adopted, populate observed facts, run the matching schema/validator revision and preserve old Evidence. Do not relabel old receipts to cover new bytes.

The Evidence root is selected by the trusted caller and resolved to its actual directory identity (including OS aliases). It is not taken from the record; verify its ownership before invocation. Symlinks in source/Evidence paths below that root are rejected. The checker does not reject OS root aliases or replace filesystem sandbox/lease enforcement. Copy schema and both Python validator dependencies together; unknown fields/types fail closed in the v1 shapes, with additional candidate/scope/byte semantics checked separately.
