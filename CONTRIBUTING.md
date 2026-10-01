# Changing AE Development Rules

Use an isolated branch and review the actual diff. Keep one canonical requirement location; templates and automation implement that contract. Project-specific mechanisms belong in project tooling unless general reuse is demonstrated.

For each change record the problem, affected stable Rule/Requirement IDs, applicability and evidence. Compare the old/new behavior on representative requests: audit-only, JSX bugfix, public micro-helper, internal native milestone, reference scopes and mixed components. Update the source registry after actually checking the source; advancing a date is not verification.

Run `node starter-kit/scripts/self-test.mjs --dry-run` and the required platform subset. A skipped runtime is NOT RUN. Tests with mocked commands establish wrapper logic, not Apple/Microsoft/Adobe runtime semantics. Do not label a static scanner as release certification.

For AI instruction/routing changes, reconcile the [behavior scenarios](docs/AI_BEHAVIOR_SCENARIOS.md), affected routing regressions and task-state/migration examples. When assessing an actual AI configuration, retain observed model/tool traces against the exact standard and fixture revisions. Passing structural or typed-context tests does not constitute a model behavior run.

Use the [controlled fixture pack](starter-kit/fixtures/ai/README.md) for repeatable starting states, permission boundaries and tool responses. Inspect actual actions and semantic acceptance; illustrative expected source text does not exclude an equivalent correct implementation. Fixture preparation/inspection tests never establish agent PASS.

Use [§34 versioning](core/ENGINEERING.md) and state the impact on already compliant projects. Breaking mandatory process changes require a major version and migration notes. Clarifications, enforcement of existing requirements and optional capabilities must describe tooling migration where formats or exit codes change. Keep previous project baselines frozen until consciously adopted.

Before authorized publication, reconcile VERSION, CHANGELOG and README; verify the exact candidate SHA with the required CI matrix and review migration notes. Create an annotated version tag pointing to the approved commit only as part of the explicitly authorized release. Branch protection and release permissions are account settings and are not configured by this document.

For accepted deviations, record the actual decision-maker, owner, date, reason, scope, compensating controls and expiry/revisit condition. No bot or contributor may invent approval. Critical mandatory failures remain release blockers unless a permitted, actually approved project deviation defines an equivalent control.

MIT licensing and original notices apply to copied substantial code/documents. Keep private diagnostics and credentials out of commits, issues and PRs.
