# Codex Agent Skills — selective orchestration (candidate)

Status: optional candidate; not an adopted standard or release. Applies only after the existing AGENT_SKILLS admission and scoped approval.

## Sources and limits
- Ruflo (https://github.com/ruvnet/ruflo): agent tracking, swarm coordination, state and hooks. Do not assume registering an agent starts execution; coordination_orchestrate can record without executing.
- Model Picker (https://github.com/firecrawl/model-picker): benchmark-driven model selection, task classification, cost reporting and independent-file parallel steps. Benchmark scores do not prove task success; no automatic escalation on failure is guaranteed.
- Existing AI_ENTRYPOINT.md, core/PROCESS.md and core/AGENT_SKILLS are authoritative. This document is not a second rulebook.

## Skills (proposed)
1. `task-router`: classify task difficulty, risk and tool requirements; choose an available model and effort when the host exposes choices. Prefer the existing model when it cannot. Never claim control over inaccessible model settings. Record route rationale.
2. `parallel-worktree`: construct dependency graph; run independent work concurrently only with disjoint owned files/worktrees; serialize shared files, schema, lockfiles and release steps; integrate and re-test.
3. `failure-recovery`: capture exact failure, reproduce, diagnose, retry once only if the failure is transient, then escalate model/effort only when available. Cap attempts and budget; unresolved errors remain failed, never successful.
4. `context-handoff`: checkpoint objective, accepted decisions, scope, branch/SHA, file ownership, open blockers, next command, test evidence. Restore and revalidate against current checkout; never treat memory as evidence.
5. `independent-review`: separate author and reviewer context where possible; review diff against requirements, regressions, security and evidence. Require actual tests, not self-reported completion.
6. `cost-observer`: record model/provider when known, real token and cost measurements when exposed; mark estimates as estimates. Compare equal task acceptance and quality, not only nominal token prices.

## Codex implementation contract
Each skill lives in its own folder with SKILL.md, minimal instructions and optional scripts/tests. Skills are invoked conditionally, not all at once. Do not import external executable hooks, auto-run remote install scripts, secrets, or network MCP without existing scoped admission. Respect host capabilities, permissions, user approvals and existing release gates.

## Pilot and acceptance
Use one representative bugfix and one multi-file feature on isolated branches. Baseline: current Codex workflow. Candidate: selective skills. Compare accepted requirements, reproducible tests, elapsed time, actual/estimated token cost (distinguished), merge conflicts and recovery behavior. No automatic adoption unless candidate is at least as reliable and provides measurable benefit. Never deploy or publish as part of this pilot.

## Next steps
Implement six bounded SKILL.md packages and unit/smoke tests; add optional entrypoint links only after passing scoped review; run pilots; then consider version bump and release with explicit authorization.
