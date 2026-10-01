# AI protocol update — 5.0 candidate

## Goal and boundary

Update the standard for an AI implementing the user's product. Preserve the existing engineering requirements and approved product decisions; make instruction priority, current-scope routing, continuation and recovery explicit.

Starting baseline: `f17c056b292631a0832b894050e204a3ca7bc2dd` on main. The user authorized all seven improvements proposed in the preceding review. This update does not publish a version tag/release or upgrade adopting product baselines automatically.

## Changes and acceptance

| Item | Previous problem | Result / canonical contract | Verification |
| --- | --- | --- | --- |
| AI-01 | Workflow could read BLOCKED as permission to start dependent reference design | Workflow and Reference Audit require exit criteria; independent completed scope may continue | Review the two contracts against AI-EVAL-05 |
| AI-02 | Routing considered contract existence without current-scope coverage | Three explicit boolean fields; uncovered product changes require discovery regardless of task label; already confirmed changes reuse Stage 0 | Failing-before/passing-after routing regression |
| AI-03 | Global decision precedence and untrusted instruction authority were underspecified | `AI-TRUST-001`, Smart Entry §2.1 | AI-EVAL-06–08 |
| AI-04 | No explicit resume/checkpoint contract for an AI losing context | `AI-STATE-001`, Smart Entry §2.2; integrate a compact template into existing canonical status | AI-EVAL-09 |
| AI-05 | Automatic work did not explicitly define continued authorization and scoped blocking | `AI-AUTO-001`, Smart Entry §4.1; status is not a new permission gate | AI-EVAL-10–12, 14–15 |
| AI-06 | General research did not require exact target-source records for newly used host APIs | `API-SOURCE-001`, Process §3; selected headers/docs, signatures, revisions and applicability | AI-EVAL-13; API audit template review |
| AI-07 | Typed routing tests did not evaluate actual AI decisions/actions | 16 free-text scenarios, observable expected/forbidden actions and run-record procedure | Catalogue reviewed; live model runs are separate NOT RUN Evidence |

The new mandatory process contracts require a major candidate under Engineering §34. VERSION and README now identify 5.0.0; the previous unreleased 4.1.0 remediation is retained. Stable 4.0.0 is unchanged. Manifest schema 3, project-record schema 1 and route output keys are unchanged; routing input migration is documented in CHANGELOG and starter-kit README.

## Verification state

- Regression reproduction: PASS — the new routing test failed on the previous helper because an existing contract incorrectly suppressed discovery for uncovered scope.
- Focused routing/contracts: PASS — all eight test groups pass after the correction, including missing/type-invalid product fields, inconsistent coverage, mislabeled product changes and already confirmed scope.
- Full repository self-test and required local POSIX subset: PASS on macOS — 104 files, behavioral smoke, 13 hardening tests and eight contract groups. Two Windows-only regressions and PowerShell parsing are NOT RUN locally; the CI Windows subset is evaluated separately.
- Static code-profile audit: PASS for its bounded scope — 94 text files, no findings. This does not assess production readiness or actual model/host behavior.
- CI matrix: Linux / macOS / Windows subsets are required by the existing workflow. Results are recorded on the pull request for the exact candidate commit; a local platform run does not establish the other platform results.
- Live AI behavior scenarios: NOT RUN. The catalogue specifies how to evaluate a concrete model/configuration; automated helper tests do not supply model traces.
- Product-specific AE runtime: N/A for this rules-repository change. Adopting products retain their applicable host checks; no host verification result is claimed.

## Next action

The seven-item implementation scope is complete. Review/CI results belong to the exact candidate in the repository's normal pull-request path; adopt the major baseline consciously after approval. Live model runs remain a separate configuration-specific evaluation, without replacing historical Evidence from another revision.
