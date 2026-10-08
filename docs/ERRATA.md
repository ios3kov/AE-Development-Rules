# Versioned errata

Known defects and temporary controls for adopted baselines. This registry does not change an adopted version in place, authenticate approvals, close mandatory product checks or certify an AI configuration. Keep original reports/Evidence. Adoption remains governed by [Engineering §34](../core/ENGINEERING.md#34-версия-стандарта-и-фиксация-baseline).

## 10.0.0 tool corrections

Affected baseline: **10.0.0**, exact source `d65baf37d76cc7c25981250d64a8d93c55c4bff2`, checked 2026-10-08. [10.0.1 correction candidate and tests](releases/10.0.1.md) is prepared locally, unpublished; candidate CI is NOT_RUN.

| ID | Defect / temporary control | Correction state |
| --- | --- | --- |
| FIX-1001-01 | Reference dispatch requires reports inside their own subject commit. Keep source and Evidence separate; the 10.0.0 workflow cannot complete that path. | Local 10.0.1 candidate; separate source/Evidence checkouts and roots. |
| FIX-1001-02 | Unreadable directories can be omitted from package digest/complete scan. Do not admit a package whose complete readable inventory is unverified. | Local 10.0.1 candidate; enumeration errors block. |
| FIX-1001-03 | Blocking protocol writes can outlive agent timeout. Avoid relying on 10.0.0 timeout enforcement for a stalled adapter. | Local 10.0.1 candidate; nonblocking I/O and shared deadline. |
| FIX-1001-04 | Cross-kind cache/output overlap is missed. Review physical path overlaps independently. | Local 10.0.1 candidate; shared filesystem namespace. |
| FIX-1001-05 | Install guidance implies self-test validates a scripts-only copy. Run it in the full standard repository. | Guidance clarified in 10.0.1 candidate. |
| OPS-1001-01 | Main protection disabled and rulesets empty. Treat local checks as advisory until independent custody is enforced. | BLOCKED; account-side setup/rejection proof remain open. |

Historical released 10.0.0 artifacts and reports retain their original bytes and subjects. No pilot or publication is claimed by these corrections.

## Historical 5.0.0 errata

Affected baseline for the entries below: **5.0.0**, published tag peeled to `8d88b19afea726b7c79988c5f6958f65d13995ba`. Observation date: 2026-10-02. Historical findings/reproductions: [deep-audit ledger](DEEP_AUDIT_BACKLOG.md). Correction tracking: [5.1 remediation](DEEP_AUDIT_REMEDIATION_5_1.md).

Historical scope: D04 below describes the 5.0.0/5.1.0 checker contract. The [6.0.0 release](releases/6.0.0.md) removes that policy gate and changes the checker interface; the historical finding is retained, not a current requirement.

| ID | Impact on affected baseline | Temporary control while retaining 5.0.0 | Corrected version / availability |
| --- | --- | --- | --- |
| D01 | Reading map can omit applicable runtime/safety and unmapped sections. | Read Tools §22 for JSX/helper/IPC, Engineering §14 for security-sensitive panels and applicable missing sections directly. Keep micro-helper scope proportional. | 5.1.0 |
| D02 | Fixture file_scope misses chmod/empty directory metadata changes. | Review filesystem types/modes and actual tool traces separately; never infer agent PASS from file_scope alone. | 5.1.0, run snapshot v2 |
| D03 | Sparse/inherited direct-JS record arrays can be accepted. | Feed the validator parsed JSON through the CLI; do not use non-JSON/sparse direct-library inputs. | 5.1.0 |
| D04 | Whitespace-only stapling N/A explanation passes wrapper syntax. | Independently require a substantive project-approved explanation; signing/download checks retain their own scope. | 5.1.0 |
| D05 | Missing task overlays can produce undefined selected IDs. | Keep released definitions; manually verify DEBUGGING/API-SOURCES/PRODUCT-DISCOVERY identity and every returned ID against the manifest. | 5.1.0 |
| D06 | Canonical source link may escape checkout and change with clean Git. | Use ordinary canonical files/ancestors from the adopted checkout; verify source hashes, not HEAD alone. | 5.1.0 |
| D07 | Artifact comparison omits special POSIX mode bits. | Separately inspect relevant bits; do not claim that v1 record attests them. Preserve record/verifier v1 together. | 5.1.0, artifact/manifest v2 |
| D08 | Valid literal U+FFFD can be rejected as non-UTF-8. | Validate original bytes with strict UTF-8 tooling; record the false rejection rather than dropping the source from inventory. | 5.1.0 |
| D09 | Version substring/leading-zero checks can miss metadata errors. | Manually compare the authoritative README version, VERSION and current CHANGELOG heading before release. | 5.1.0 |
| D10 | Reordered object keys can conceal duplicate Evidence items. | Deduplicate Evidence by actual JSON value/path/hash; repeated items are not independent corroboration. | 5.1.0 |

Only the listed baseline was examined; other versions are not automatically declared affected or corrected. The corrected source is selected by immutable tag [v5.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.1.0). Its exact peeled commit, regression/platform CI and artifact hashes are recorded in the attached `release-evidence.json`; [remediation](DEEP_AUDIT_REMEDIATION_5_1.md) preserves the local stage. Do not edit the old findings into historical PASS.

For future entries SHOULD retain: stable ID, affected version/commit/range with basis, observation date, impact/applicability, actual owner where assigned, temporary control, correction version/commit and publication state, regression link, disposition/revisit condition. Unassigned ownership remains explicitly unassigned; no invented approval. A proposed process requirement that changes MUST/gate semantics still needs §34 compatibility/version analysis.
