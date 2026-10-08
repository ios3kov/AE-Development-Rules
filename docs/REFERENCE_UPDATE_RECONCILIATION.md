# Reference update reconciliation — 2026-10-08

Source of scope: archived conversation **Анализ репозиториев** (6ac73339-bdec-83ed-983c-9b1dbe3263dc), initial 50-item list and acceptance, followed by the explicit pause of section 4. The full list was recovered through the authenticated archive, beyond the bounded read_thread preview. Current user instruction authorizes standard fixes/tests/CI/push/merge and excludes releases/publication and product work.

Baselines: AE PR #22 head f1801dcb58e8bddb961b315dd0ce462529318384 / main d22ede2ddead8576e468b96f40ef0da12c5216e0; AS PR #3 head 2a3ac699f4b6e798fae129034ea7b590a70967d2 / main 63b12e552a2c1d053e50ee7f7dc1bd2c98203139. Both checkouts began clean. Existing standard adoption/version remains frozen; this extension implements optional tooling for the existing Reference Audit/requirements/Evidence, with draft-tool format migration. It does not impose a new universal product/release gate.

## Requirement mapping

Numbers preserve the original agreed list. “Method” means the standard now gives an actionable conditional procedure and output/exit contract; actual external-tool execution is project-specific. “Tool” means an executable offline helper with synthetic negative tests. Retained canonical mechanisms are referenced rather than duplicated. Source completeness is reviewed separately from mechanical inventory coverage.

| # | Agreed improvement | Final home / implementation / bounded verification |
| --- | --- | --- |
| 1 | Function → test → Evidence ledger | reference obligations adapter; reviewed policy, existing requirement/check IDs, typed verifier results |
| 2 | Find unstudied functions | compile observations reports reviewed inventory gaps; policy rejects dropped behaviors; unknown hidden functions still require review |
| 3 | Completeness before design | existing Reference Audit exit retained; coverage policy/cases checked; critical unknowns block dependent scope |
| 4 | Generate tests from observations | compile emits deterministic replay/assertion specifications, hash-bound oracles; generated execution stays NOT_RUN |
| 5 | Compare original/implementation | original, fixture and verifier records plus event/RGBA tools; product runner supplies actual executions |
| 6 | First divergence | ordered trace comparator, including shorter/longer traces, nonzero on mismatch |
| 7 | Order/cancel/recovery | required case minimum and event traces; cancellation/recovery method and negative tests |
| 8 | Internal dependencies | imported nodes/edges with fact/inference Evidence; graph method/tool |
| 9 | UI → API → process → native | layer/trace correlation method; fact-backed graph edges, unknown edges retained |
| 10 | Binary/function version differences | exact binary/component snapshots, changed-function mappings and impacted obligation tool; semantic matching is reviewed |
| 11 | Exact-identity reuse | existing Evidence lifecycle retained; version diff supplies impact, never automatic cross-candidate PASS |
| 12 | Contradictions/unknowns and next probe | adapter rejects unresolved required gaps; playbook requires hypothesis/impact/next discriminating experiment |
| 13 | File/tool router | magic-based plan; archive stops at inspection; no automatic execution |
| 14 | Installed tool/version checks | explicit version/operation/probe inventory; missing operation returns BLOCKED |
| 15 | Mach-O/DLL/EXE workflow | native inventory → targeted static graph → authorized discriminating probe → exact Evidence/exit |
| 16 | Swift/Obj-C/IPA/frameworks | mobile method and expanded AS template; architecture/signature/entitlement/resources/state bindings |
| 17 | Ghidra calls/dependency graphs | targeted xrefs/callers/callees export procedure; offline graph validates/render facts; Ghidra itself optional |
| 18 | Small decompilation fragments | playbook bounds question/range/address/context; no bulk-dump default |
| 19 | Test algorithm hypotheses | evidence-labelled hypothesis/counterexample experiment; static inference cannot close runtime obligation |
| 20 | Resources/schemas/formats | existing AE inventory retained; mobile/native methods extend output/identity/serialization observations |
| 21 | Extracted module isolation | owned harness, ABI/dependencies/resource/cleanup limits and controls; no untrusted automatic launch |
| 22 | Static versus execution | incomparable host/device and static/runtime rejected; fixture generation/graphs explicitly not execution |
| 23 | Automatic diagrams | safe-ID Mermaid graph output with claim labels and Evidence references |
| 24 | Screen/transition map | expanded AS table/navigation graph; existing AE systematic audit reused |
| 25 | Empty/loading/error/offline states | explicit mobile/UI states and observation/case bindings |
| 26 | Token extraction | measured-control token extractor with Evidence IDs; screenshot inference stays a reviewed observation |
| 27 | Region visual diff | matched full RGBA buffers, no resize/alpha flatten, whole-image and named-region differences |
| 28 | Token contrast | opaque sRGB luminance tool; reviewed applicable threshold; existing accessibility process retained |
| 29 | E2E from scenarios | deterministic scenario output feeds existing E2E runner; authorized own-target replay method |
| 30 | Prioritize gaps | mobile/spec coverage table includes priority/impact; reviewed required minimum defeats score-based bypass |
| 31 | Reference versus extensions | separate acceptance IDs in mobile template/method; owner-authorized differences cannot hide parity gaps |
| 32 | Material UI-state checks | reviewed inventory/state/case minimum; missing observations/cases fail; actual UI adapters remain project-specific |
| 41 | Actual agent actions | existing evaluation protocol retained, reference adversarial cases added; no self-report certification |
| 42 | Correct first tool | router capability plan and declared actual-trace first-tool metric; live evaluation separate |
| 43 | Useless repeated calls | identical-call/retry-reason metric and bounded retry/replan procedure |
| 44 | Tokens/cost | receipt-derived metrics; unavailable usage is unmeasured, not fabricated zero |
| 45 | Unavailable check never PASS | existing status rules retained; BLOCKED/NOT_RUN obligation yields nonzero; fixture generation not execution |
| 46 | Origin/freshness | external pin, independent reviewer, capture role/record digest, time/expiry/candidate checks |
| 47 | Requirement → test → Evidence | existing IDs/checks bound in policy/ledger/verifier artifact; no second normative registry |
| 48 | Imported result integrity | regular contained files, duplicate-key rejection, source/owner/artifact/whole-record hashes |
| 49 | Affected checks after changes | component/dependency impact tool and existing scoped regression/reuse review retained |
| 50 | CI stops on blockers | negative CLI exit tests, main standard test integration, fail-closed combined protected workflow |

Items **33–40 are PAUSED and excluded**. No implementation or edits to product discovery, competitor/review analysis, branding/assets publication rules, store metadata, marketing claims or release/preflight product mechanisms are part of this update. Existing publication workflows and published artifacts remain unchanged.

## Acceptance and review

- Standard contract/synthetic negative tests exercise policy removal, fake PASS, incomplete cases, forged/substituted/unpinned witness, stale owner/result/candidate, host/device mismatch, paths/symlinks, expired approval, duplicate JSON, first divergence, missing observations, visual alpha/HDR/regions and wrong tool operations.
- Main AE self-test now invokes the reference suite; AS Standard checks already discovers it. Manual trusted workflow validates local files and policy before witness acceptance and cannot run candidate code.
- Review is a separate diff/spec pass. Reconcile scope and every new helper error path before push; repeat affected checks after fixes. CI verifies exact PR candidate and merged main separately.
- NOT_RUN: actual AE/iPhone parity pilots, real Ghidra/LLDB/Frida/Rever captures and newly added live-agent evaluation scenarios. No runtime/product readiness is inferred from synthetic CI.
- NOT_VERIFIED: repository protection, independent reviewer membership/capture custody and operational trusted witness producer. These limit product enforcement; they do not block standard-only merge once standard tests/review pass.
- Historical package examples remain historical; provenance checks continue to bind current standards separately. Cleanup is no-op for historical Evidence; only owned temporary Python caches are disposable.

## Primary inspiration checked

- [replica-skill](https://github.com/Jakeschincariol/replica-skill): screen/state scenarios and measured design tokens; avoid score-based release decisions and downscaled alpha-flattened render claims.
- [REA obligation ledger](https://github.com/morluto/rea/blob/main/docs/reconstruction-obligation-ledgers.md): conservative owner/case/verifier/Evidence closure and unknowns; current adapter uses existing project authority.
- [Ghidra in Claude Code](https://github.com/coffeegrind123/ghidra-in-claude-code): operation/version capability verification for targeted native analysis.
- [Reverse Engineering Assistant](https://github.com/cyberkaida/reverse-engineering-assistant/blob/main/ReVa/skills/deep-analysis/SKILL.md): narrow questions/ranges/addresses and evidence-backed hypothesis refinement.
- [Mobile Reverse Skill](https://github.com/salamander97/mobile-reverse-skill): conditional mobile artifact/tool investigation methods.
- [Rever Browser](https://github.com/greekr4/rever-browser): authorized traffic/scenario capture and deterministic replay with data redaction.

Checked 2026-10-08 as design inspiration, not installed software or certified toolchain. No source implementations/skills were copied or executed. Future adoption checks the exact tool/source version and license separately.

## Completed local review / verification

Separate diff/spec review completed after implementation: policy downgrade/removal, owner and raw Evidence bytes, typed failed-case results, candidate/version replay, witness role/procedure/environment/time binding, safe paths, no candidate execution, workflow main/immutable verifier guard and suppressed protected logs inspected. No unresolved blocker in the standard-only scope.

Local results: AE complete Node/POSIX self-test PASS, including 55 reference tests; PowerShell NOT_RUN locally and covered by Windows CI. AS structure PASS and 216 contract tests PASS. Fixed a macOS temporary-path alias in the existing negative archive-symbol fixture; the product archive implementation is unchanged. Final exact-commit and merged-main CI results are reported separately by run URL/SHA.

Code scanner exit 1: only existing write-permission findings in untouched publication workflows. Reviewed permissions are scoped to existing publication jobs; this change neither expands them nor triggers those workflows (their push path filters are unchanged). No new scanner findings in the changed scripts/workflow. This advisory finding does not certify release readiness or authorize publication.
