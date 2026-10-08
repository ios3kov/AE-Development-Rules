# Optional implementation review (unreleased)

Embed in the existing review/checkpoint. [Engineering §14](../../core/ENGINEERING.md#14-качество-и-безопасность-кода) applies at the actual scope; one person can perform both reviews. A second agent is optional.

- Exact candidate / affected scope:
- Current requirement/spec revision and reviewed acceptance/checks:
- Reviewed locations; unreviewed locations and impact:
- **Spec conclusion:** PASS / FAIL / BLOCKED / NOT RUN; observed acceptance, missing/extra scope, basis/Evidence:
- **Quality conclusion:** PASS / FAIL / BLOCKED / NOT RUN; correctness/security/maintainability, applicable risk and basis/Evidence:

| Location | Concrete consequence | Reproducible input/code path/contract/Evidence | Blocking? | Resolution / current recheck |
| --- | --- | --- | --- | --- |
| <file:line or function> | <observable impact> | <checkable basis> | <yes/no> | <candidate/result or open> |

No blocking failure is offset by an average score. Missing a required check stays explicit. After fixes, conclusions and affected checks refer to new bytes. A style preference needs a practical basis before becoming a blocking demand.

For native changes, use [native scope coverage](NATIVE_REVIEW.md); for a bugfix, the existing [Debugging Record](DEBUGGING_RECORD.md) carries original-defect regression sensitivity. Do not add a second debugging/stop/handoff system.
