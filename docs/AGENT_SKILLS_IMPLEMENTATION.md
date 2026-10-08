# Agent skills extension — unreleased

User-approved scope: attached development plan, 2026-10-08. Standard baseline 9.0.0; actual remote main and isolated worktree base `a43c75aba8c714658822277835909c4726d5a523`. Original feature checkout clean; reference changes already merged and retained. Work is limited to AE; AS, product/marketing/publication, installed external skills/hooks/MCP, GitHub settings, merge/release/deploy and paid pilots are excluded. Branch: `feat/agent-skills-governance`.

## Baseline reconciliation

| Classification | Existing mechanism / scoped delta |
| --- | --- |
| Already implemented | Smart Entry trust/permissions/state; scoped manifest routing; Process ownership/parallelism/regression/Evidence/completion; Engineering safety/dependencies/SDK sources/pure core; render alpha/depth/color comparators; reference policy/witness and 55 negative contracts; AI fixtures and real-action evaluation protocol. Preserve these. |
| Extend | Skill resources share existing trust/Evidence; existing evaluation gets a launch/observer adapter and held-out skill cases; task contracts clarify readiness/resources; native review gets dimensional/coverage receipts and bounded executable properties. |
| New | Conditional §43 skill admission registry, exact full-package integrity, managed local lifecycle and protected policy/scan admission; standard SKILL.md remains upstream format. |
| Deferred / unavailable | Installation of upstream tools; operational reviewer/protection changes; paid/live-model and AE pilots; product publication. Do not infer effectiveness/security/host acceptance from synthetic tests. |

## Obligation → execution → acceptance

| Obligation | Canonical home / execution | Acceptance |
| --- | --- | --- |
| Applicable admitted skill, ordinary task unaffected | §43 / optional `skills` reading overlay, local selector | No skill overlay for old/small-task context; missing task/tool match cannot activate |
| Pin and restore full package, one owner | §43 / package inventory and local managed lifecycle | Changed resource, source, symlink, archive traversal, collision/foreign update/removal fail |
| Admission policy independent from candidate | §43 / externally pinned policy, complete scan and protected verifier | Candidate/rejected/revoked, failed/incomplete/unavailable scan, changed policy or stale bytes fail; telemetry off still requires scan |
| Enforce supported environment rights | §43 / runner capability probe and actual isolation | Required unavailable isolation BLOCKED; text permissions and temporary paths never substitute |
| Observe actual agent actions and outcomes | Existing evaluation protocol / launch + protected observer | Held-out answers inaccessible; critical breach hard failure; real usage only; synthetic tests do not certify models |
| Task readiness/resource ownership and review | Process §§5,11 / task and review receipts | Dependency cycle/unready task/overlap and unjustified review findings fail; original defect is detected by regression check |
| Native risks/units/coverage | Engineering §§14,32,41; Native §23 / offline C++ fixture and review receipts | Memory/numeric/units counterexamples and deterministic property/fuzz corpus; host correctness remains separate |

## Version and migration decision

Per Engineering §34 this is an **unreleased normative delta**, not a rewritten 9.0.0 release. Skills become subject to new conditional admission obligations; significant delegated work/native changes gain scoped evidence clarifications. Already compliant projects without these triggers do not acquire skill infrastructure. Compatibility conclusion: a previously compliant project using an external skill can need new admission/review/scan actions, so this normative delta belongs to the **major class** under §34; no numeric version is assigned before an authorized release. Task/native additions are risk-scoped SHOULD refinements. A future release must publish the applicable adoption/migration note. VERSION and historical release Evidence remain unchanged. New schema v1 records have no prior compatible format; reference/project-record schemas and IDs are preserved. Read schema, validator and tests together when copying new tools.

## Progress / verification

Independent owners: root — registry/routing/protected workflow/integration; skill package block — package/lifecycle tool; evaluation block — runner/observer/fixtures; engineering block — process/native tools. No overlapping writable files. Shared resource: this worktree; no AE/device/cache sessions allocated. Root verifies the combined candidate after all blocks and conducts a separate spec/diff review.

Local combined-candidate self-test PASS on macOS with required POSIX runtime: 225 files, 183 Python tests and existing Node contracts. PowerShell parser NOT_RUN locally; Windows/Linux validation belongs to the PR matrix. Offline C++17 examples PASS with ASan/UBSan, 20,000 seeded iterations, red/green defect detection and rejected invalid-units API. Separate spec/diff review resolved four evaluation defects: task/tool admission arguments, observer-only checker access, synthetic-to-live relabelling and exact identity validation; independent evaluation rerun 23/23 PASS.

Static code audit completed its bounded scope; its only finding is the unchanged historical release workflow's write permission, required for its authorized publishing job. No new permission/trigger was added there; release readiness is not assessed. This is reviewed scope, not a global security certificate. The extension is submitted for draft-PR CI only; no merge, release, settings change or paid pilot is authorized. Live model pilot NOT_RUN; live AE pilot NOT_RUN. Built-in observation covers broker actions/results and independent diffs/checks; individually audited denied OS syscalls require an external reviewed runner. Operational protections/reviewer custody remain BLOCKED as documented in the protection audit.
