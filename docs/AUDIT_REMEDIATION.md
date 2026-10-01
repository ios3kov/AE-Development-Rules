# Audit remediation

Baseline: v4.0.0 / 58d14aa12375757f4e52396d951f1557ae4f453c.
Scope: A01–A13 and the adoption, routing, Evidence and governance improvements from the 2026-10-01 audit. No merge or public release is part of this change.

## Acceptance

- R1: artifact records bind file types, paths, executable modes and safe internal symlinks; historical records cannot be overwritten.
- R2: missing required tools, unreadable candidate input and failed required probes cannot report successful completion.
- R3: bundle checks state their exact scope; required stapling/timestamp checks fail closed.
- R4: applicability data is strictly validated and routing scenarios preserve independent risk/delivery axes.
- R5: directives/includes work within a documented JSX syntax subset; unresolved includes fail.
- R6: workspace creation resolves ownership safely and rejects symlinked configured ancestors.
- R7: milestone and micro-helper requirements agree across canonical text and templates.
- R8: stable requirement IDs, project records, adoption examples, visual fixtures, Evidence lifecycle and change governance are documented and tested.

## Remediation mapping

| Finding | Resulting behavior | Regression evidence |
| --- | --- | --- |
| A01 | Empty resources fail; bundle PASS explicitly covers structure only, with PiPL semantics NOT RUN | macOS native fixture |
| A02 | Artifact manifest binds types, relative paths, modes, contents and bounded internal symlinks | Modes/content/link mutations |
| A03 | UUID run IDs and exclusive destinations preserve artifact/binary/dependency records; INCOMPLETE artifact records are rejected | Overwrite/overlap rejection |
| A04 | Staged and selected committed changes are checked; missing tools and failing hooks block | POSIX negative fixtures; Windows subset in CI |
| A05 | Schema 3 rejects missing/empty profiles, unknown fields/rules, duplicate IDs and missing core/gate rules | Manifest mutation suite |
| A06 | Target directives and literal includes are preprocessed; missing/cyclic/invalid includes block | JSX subset fixtures |
| A07 | Internal milestone has its own acceptance; full Release Gate applies to RC | Canonical text and routing scenarios |
| A08 | Required binary probe failure produces PARTIAL and nonzero exit | Valid/invalid Mach-O fixtures; dumpbin fixture in Windows CI |
| A09 | Public micro-helper may remain Light while Delivery becomes Release | Canonical text, routing and filled JSX example |
| A10 | Unreadable/empty/unsupported source inventory is INCOMPLETE | Source fixtures and candidate hash inventory |
| A11 | Configured workspace ancestors are checked and arbitrary symlinks rejected | Root/ancestor link fixtures |
| A12 | Required stapling failure blocks; N/A requires explicit policy and reason | Isolated command stubs |
| A13 | Public Windows check requires validated signature with timestamp certificate | Missing-timestamp fixture in Windows CI |

R8 additions: stable requirement markers/registry, optional project-record schema/validator, Native/JSX/CEP contracts, four numerical RGBA fixtures/comparator, Evidence lifecycle guidance, source claims and deviation ownership, contribution/PR/issue templates and credential-restricted CI. These tools do not introduce a universal required service or new process gate.

## Verification ledger

| Scope | Status | Evidence |
| --- | --- | --- |
| Local macOS self-test | PASS | Node self-test: 98 files; smoke PASS; 10 hardening tests PASS, 2 Windows tests skipped; 6 contract groups PASS |
| Manifest/routing/project-record/visual tests | PASS | 11 routing scenarios; mutation/stale-hash/status/context-negative cases in contracts.mjs |
| Static re-audit | PASS in scanned scope | production-engineering code scanner: no findings; runtime/release not assessed |
| Linux/macOS/Windows CI | See current PR checks | [PR #8](https://github.com/ios3kov/AE-Development-Rules/pull/8/checks); required runtime flags prevent silent omission. Initial Linux/macOS run passed; Windows found fixture exit propagation and was corrected before retry |
| Actual AE load, notarization, Windows signing | N/A | No product or release candidate is being certified; wrapper contracts use isolated fixtures |

Procedure: `node starter-kit/scripts/self-test.mjs --dry-run --require-posix` locally; CI selects `--require-posix` or `--require-powershell`. Test stubs establish wrapper behavior only. Source claims added for Apple notarization, Microsoft timestamping and Adobe CEP distribution were checked against primary documentation. Source-registry age checks alone do not revalidate those claims.

Windows behavior is not inferred from the local macOS run. Exact final commit and platform results are recorded in the PR and handoff. The first run is [36916966194](https://github.com/ios3kov/AE-Development-Rules/actions/runs/36916966194) for 11b56c5; its Windows failure is preserved. The nested PowerShell test harness now explicitly propagates collector exit codes. No merge, tag or public release is included.

Adjacent A03 coverage: dependency collectors now use UUID report names and exclusive writes. A fixed-clock regression runs them twice and verifies both historical reports and unchanged first bytes.

The dependency regression also reproduced an existing zsh `path` variable collision that replaced PATH during hashing. The loop now uses manifest_file, and find/sort failures propagate outside process substitution.

Verified CI baseline: [run 36917756681](https://github.com/ios3kov/AE-Development-Rules/actions/runs/36917756681) passed Linux/macOS/Windows for 11b9bdc8aacd7fa1d0aca12ba657cd3246c0d2cc, including fixed-clock dependency-history tests. Subsequent JSX subset refinement explicitly rejects absolute includes; its final result is available in current PR checks.

## Follow-up audit remediation

Baseline: main commit 05bd9a8d71c11280d972b96caf64b776f2a075d7. Scope: R01–R06 from the fresh whole-repository audit. These changes enforce existing contracts and clarify applicability; they introduce no new universal MUST or release of the standard.

| Finding | Acceptance | Rule or requirement | Regression evidence |
| --- | --- | --- | --- |
| R01 | DIRTY blocks Validation and Release; Development remains permitted | IDENTITY §7, ART-001 | All six source-state/delivery combinations |
| R02 | PKG uses pkgutil, app/dmg use codesign; Gatekeeper selects the matching format and DMG context; required failures block | MAC-DIST §28, MAC-001 | Command-routing fixtures plus failing pkgutil; existing stapling/quarantine contracts |
| R03 | Valid regex/division before include passes; comments/strings/templates retain literal directives; malformed included code still fails | TESTABILITY §41; JSX subset tooling | Regex, control/return context, division, comments, strings and template fixtures |
| R04 | Mixed lowercase/uppercase supported source extensions appear in inventory and symbols | COMPAT §21, COMPAT-001 | cpp, C, H and CPP mixed inventory |
| R05 | Unknown prototype-named keys and inherited required values are rejected | Optional schema contract | constructor, toString, __proto__ and inherited required-field fixtures |
| R06 | Internal milestone alone does not select Level 2; Release Candidate keeps Level 2 | REGRESSION §9 | Canonical clarification reconciled with §§1 and 11; existing routing scenarios |

Before implementation, the new fixtures reproduced five failing groups against the baseline. After the fixes, the full local macOS self-test passed across 101 files, including 13 hardening tests and 7 contract groups, with 2 Windows-specific skips. A real unsigned, no-payload PKG fixture also confirmed pkgutil rejects an absent signature with exit 1; nothing was installed. Wrapper fixtures establish command selection and error handling, not real Apple signing or Adobe runtime semantics. Cross-platform CI must be evaluated against the final candidate commit before handoff.

JSX tokenization uses the unchanged, integrity-checked js-tokens 10.0.0 source. Its license/provenance accompanies copied tooling; Node's parser still provides the final syntax decision. See [vendor record](../starter-kit/scripts/lib/vendor/README.md). Platform signature checks follow [Apple signature guidance](https://developer.apple.com/documentation/security/resolving-common-notarization-issues).
