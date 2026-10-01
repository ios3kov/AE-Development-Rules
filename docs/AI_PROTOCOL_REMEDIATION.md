# AI protocol F01–F12 remediation

Date: 2026-10-01. Original rules baseline: `b27f45467e0a9152fc82c1072438dfed07f0c36e`; repeat-audit baseline: `eab6d9b93fb818bf7abaa5c51c4e59bf485be224`. The [finding ledger](AI_PROTOCOL_BACKLOG.md) preserves historical observations. This correction implements all twelve recorded items within the unreleased 5.0.0 candidate; stable publication/tagging is not part of this change.

| Finding | Delivered behavior | Acceptance evidence |
| --- | --- | --- |
| F01 | Task overlays select diagnostics/API sources; Light exposes applicable minimal process sections | followup.mjs: all five component routes, docs/audit/research distinction; generated table |
| F02 | No unchanged failed attempt without a basis; change hypothesis/signal or scoped blocker | Workflow §8, Engineering §16, debugging record; AI-EVAL-17 |
| F03 | Recording critical unknowns alone does not close dependent Stage 0; bounded nonblocking assumptions remain possible | Discovery §0.4/0.11 and matching template; AI-EVAL-18 |
| F04 | Compact product requirement → task → acceptance → check/Evidence mapping in existing records | Engineering §32, optional traceability template; AI-EVAL-20 |
| F05 | Versioned controlled starting files, permissions, simulated responses, rubrics, illustrative outcomes and preparation/inspection | 21 fixtures / 20 scenarios; followup.mjs preparation, resume preservation and unauthorized changes |
| F06 | Explicit pre-handoff prerequisites versus safe user-only question versus final Release acceptance | Release §26, Process, Validation checklist, optional record phase; followup.mjs legacy/Release/dirty/failure cases; AI-EVAL-12 variants |
| F07 | PKG container uses pkgutil; executable payload verification remains separate; app/DMG use codesign | Release §28 and Release checklist aligned with existing macOS wrapper; existing hardening tests |
| F08 | Bounded ordered ranges and every real section verified | followup.mjs reversed/oversized/missing/valid ranges |
| F09 | Dense own finite pixel values; stable finite metrics; overflowing derived differences reject | followup.mjs sparse, 1e200 RMSE and maximum subtraction, direct library and JSON CLI |
| F10 | N/A needs substantive trimmed rationale, without claiming semantic approval | followup.mjs whitespace cases; valid rationale still NOT_ASSESSED readiness |
| F11 | Reread applicable adopted rules before stages; pin milestone version/SHA/date; no silent upgrade | README / Smart Entry reconciled with §34; AI-EVAL-19 |
| F12 | Dense own unique known component list required before selection | followup.mjs sparse/inherited/mixed/duplicate/unknown inputs |

Verification: repository self-test exercises syntax, local links, manifest/table, source/requirement contracts, wrapper logic and regressions; platform-specific checks run in the Linux/macOS/Windows CI matrix. Exact candidate and CI Evidence are retained on [PR #11](https://github.com/ios3kov/AE-Development-Rules/pull/11). Scope-specific automated results are not a guarantee of complete error absence.

Semantic documentation review reconciles canonical rules, Smart Entry, templates and migration notes. Supplied AI cases enable reproducible evaluation but no actual model has been run on them here: **NOT RUN**. Product AE runtime is also **NOT RUN** and is not a rules-repository merge gate. The file inspector never turns its partial observations into agent PASS. Trusted policy/approval and actual host behavior remain outside helper certification.

Before merge, the previous current main was preserved remotely as `backup/main-before-ai-fixes-2026-10-01-b27f454`, pointing to `b27f45467e0a9152fc82c1072438dfed07f0c36e`. Merge is conditional on the exact candidate passing the required CI matrix and the previous current main being preserved. No baseline release/tag or real product publication is authorized by this correction.
