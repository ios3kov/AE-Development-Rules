# Product requirement traceability

Embed this table in the existing plan, issue or spec for significant requirements. A separate document is optional; a small local fix may use a single linked acceptance statement. Engineering §32 is the canonical guidance.

| Product requirement ID / confirmed source | Task ID / scope | Observable acceptance | Check ID / phase | Candidate / Test Status / Evidence |
| --- | --- | --- | --- | --- |
| PR-EXPORT-01 / approved spec | TASK-EXPORT-01 / serializer | Export preserves approved layer names | TC-EXPORT-01 / pre-handoff | <actual revision, result, evidence> |

The example is illustrative and has not been executed. Use the project's IDs; REQUIREMENTS.json IDs identify standard rules, not product requirements.

Record a derived requirement's rationale and confirmed parent. Link risk-control tasks to the risk they address. Unlinked ideas remain proposals outside the approved scope. Do not convert missing tests into PASS or discard valid acceptance criteria to match an implementation.

## Applicable scope and final reconciliation

Follow [Process §11](../../core/PROCESS.md#контроль-прохождения-задачи-и-финальная-сверка) for significant multi-block work. An equivalent existing plan record is sufficient; a separate template file is optional.

- Scope revision / permission source / delivery and phase:
- Applicable requirements and excluded/non-applicable items with substantive reasons:
- Dependencies and mandatory versus optional checks identified before implementation:
- Implementation state, actual check status/Evidence and remaining task distinguished:
- Scope updates/deferrals preserve source decisions and previous obligations:
- Final reconciliation against current files/artifact: missing rows, open requirements/checks, documentary mismatch:
- Specific justified completion/handoff claim and unresolved work/unblocking condition:

Reconcile the complete current requirement set, not only rows already marked complete. An omitted requirement is not N/A. Do not weaken acceptance criteria or replace valid tests merely to match code. Do not copy prior PASS to changed candidate bytes; retain the old record and perform applicable checks. Use canonical Test Status for checks, not invented task-progress values. Validation deferral is allowed only under its actual phase policy, not to bypass pre-handoff or release prerequisites.
