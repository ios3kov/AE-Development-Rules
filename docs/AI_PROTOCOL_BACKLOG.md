# AI protocol follow-up audit / backlog

Audit baseline: `b27f45467e0a9152fc82c1072438dfed07f0c36e` (5.0.0 candidate), 2026-10-01.

Scope: record the five previously proposed follow-ups and identify additional concrete weaknesses in the AI instructions, canonical-rule selection and supporting tools. This record is an audit/backlog, not authorization to implement its items. Normative rules and runtime-tool behavior are unchanged by recording a finding.

## Classification

- **CONFIRMED** — current behavior is reproduced or the absence/mismatch is directly established.
- **AMBIGUITY** — current wording admits a material wrong interpretation; no live-model failure is claimed.
- **IMPROVEMENT** — a useful additional mechanism, rather than proof that an existing requirement failed.
- **OPEN** — recorded, not fixed. These are finding states, not Test Status.
- **P1** — address a decision, scope or safety boundary before relying on it.
- **P2** — improve reliability, consistency or verifiability.

## Finding ledger

| ID | Priority | Classification | State | Item |
| --- | --- | --- | --- | --- |
| F01 | P2 | CONFIRMED | OPEN | Align text-defined bugfix routing with the selected DEBUGGING rule group |
| F02 | P2 | IMPROVEMENT | OPEN | Define a no-progress/repeated-failure policy for AI attempts |
| F03 | P1 | AMBIGUITY | OPEN | Distinguish recorded critical assumptions from permission to pass Stage 0 |
| F04 | P2 | IMPROVEMENT | OPEN | Trace significant requirements through tasks, acceptance and Evidence |
| F05 | P2 | IMPROVEMENT | OPEN | Turn free-text AI scenarios into reproducible controlled fixtures |
| F06 | P1 | AMBIGUITY | OPEN | Distinguish pre-handoff validation checks from the question the user is meant to test |
| F07 | P2 | AMBIGUITY | OPEN | Align macOS signature requirements/checklist with PKG versus nested-code verification |
| F08 | P2 | CONFIRMED | OPEN | Reject reversed canonical-section ranges instead of silently checking zero sections |
| F09 | P2 | CONFIRMED | OPEN | Reject sparse pixel arrays in the render comparison library |
| F10 | P2 | CONFIRMED | OPEN | Reject whitespace-only N/A rationales in project records |

F01–F05 are the previously proposed items. F06–F10 were added by this follow-up audit. [Recorded tool observations](evidence/ai-followup-probes.json) bind the isolated probes to the audit baseline. F01/F08/F09/F10 are reproduced tool-contract findings; F03/F06/F07 are wording ambiguities; F02/F04/F05 are improvement proposals. None is recorded as fixed.

### F01 — Bugfix routing omits the diagnostic module

**Evidence:** [Smart Entry](../AI_ENTRYPOINT.md) routes a bug through Debugging Protocol. The manifest declares `DEBUGGING` at Engineering §16, but [route()](../starter-kit/scripts/lib/applicability.mjs) adds no task-specific diagnostic overlay. Reproduced with `task: bugfix`, `components: [native]`, `risk: standard`, `delivery: development`, `reference: none`, `product_contract: true`, `contract_covers_scope: true`, `changes_product_contract: false`: `rules.includes('DEBUGGING')` returns false.

**Impact:** An AI following only the helper's selected sections may omit the recommended diagnostic protocol. The text still requires the AI to consider that protocol; this is a selection gap, not proof that an actual model ignored it.

**Related coverage:** Light JSX selects only `CORE-SCOPE`; §1 still requires applicable Regression Level 1, while the micro-helper template also describes runtime/versioned-source checks. Reconcile indirect requirements with the selected reading sections rather than count this as a second independent finding.

**Proposed correction:** Align task-specific module selection with Smart Entry and document any intentional eligibility exceptions. Review new/changed host-API source selection in the same reconciliation rather than maintaining two implicit rule-selection paths.

**Acceptance:** Representative host/native/bridge bugfix inputs select the applicable diagnostic section; audit/documentation requests do not become implementation. A new API call's required source verification remains discoverable regardless of Risk Profile.

### F02 — No explicit response to repeated attempts without progress

**Evidence:** [Engineering §16](../core/ENGINEERING.md) describes hypothesis/experiment/fix; [Workflow §8](../WORKFLOW.md) limits endless improvements. Neither gives an explicit agent-level policy for repeating the same failed action without new Evidence or changed conditions.

**Proposed correction:** Record rejected hypotheses/failed approaches in the existing debugging record; repeat only with a meaningful changed condition. If progress stalls, change the hypothesis, collect a new discriminating signal or report the scoped blocker. Avoid a universal arbitrary retry count and preserve independent authorized work.

**Acceptance:** A repeated identical failure causes a reasoned strategy change or scoped blocker instead of another unchanged attempt. A transient failure with a justified bounded retry remains supported.

### F03 — Recorded assumptions can be read as a Stage 0 exit

**Evidence:** [Product Discovery §0.4](../PRODUCT_DISCOVERY.md) permits a material assumption to be confirmed or explicitly recorded before a technical decision; §0.11 says critical assumptions may be confirmed or explicitly recorded. The same exit criteria prohibit remaining questions that block design. The boundary between a permissible documented assumption and a blocking unknown is not explicit.

**Proposed correction:** State that recording an unknown does not resolve a dependency. Identify owner, impact, decision boundary and validation condition for accepted nonblocking assumptions; critical unresolved behavior blocks its dependent design unless the actual decision-maker chooses a sufficiently defined alternative/scope.

**Acceptance:** A critical unknown cannot pass Stage 0 solely because it was written down. Bounded nonblocking assumptions and independent scope remain possible without an unnecessary interview.

### F04 — Requirements are not traced end to end by a compact project record

**Evidence:** The discovery template has a requirement ledger and the test templates have acceptance/Evidence fields, but the standard has no reusable compact mapping from a significant product requirement through implementation task to acceptance check and result. The stable registry identifies standard rules; it is not the project's product-requirement map.

**Proposed correction:** Add fields to an existing project plan/issue/table: requirement ID/source → task → acceptance → check/Evidence. Do not add separate paperwork for each local low-risk edit.

**Acceptance:** A significant requirement can be located in the plan and linked to an observable check; an implementation task with no requirement or necessary risk control is visibly outside scope.

### F05 — Agent scenarios lack supplied reproducible fixture repositories

**Evidence:** [AI behavior scenarios](AI_BEHAVIOR_SCENARIOS.md) define requests, context, expected and forbidden actions plus a run procedure. The described fixture repositories, tool responses and expected diffs are not supplied. No live-model execution was claimed.

**Proposed correction:** Supply small versioned fixture repositories/data, controlled tool responses, exact permissions and outcome checks for the relevant scenarios. Inspect actual calls/diffs, not the agent's self-reported checklist. Keep execution opt-in and avoid real user data or publication.

**Acceptance:** Two evaluators can start the same scenario from the same source/context and independently judge the same observable actions. Record model/configuration and actual traces; helper-test PASS remains separate.

## Additional findings

### F06 — Validation prerequisites and the user's test are not separated explicitly

**Evidence:** [Release §26 Validation Gate](../profiles/RELEASE.md) permits a limited identified build after relevant available internal checks, without a known mandatory FAIL or critical safety issue. [AI-EVAL-12](AI_BEHAVIOR_SCENARIOS.md) describes an unavailable required host acceptance scenario and expects the handoff gate to remain incomplete, without identifying whether that scenario is a pre-handoff safety prerequisite or the intended user validation itself. The [project record](../starter-kit/schemas/project-record.schema.json) has one `required` boolean per check, with no phase/dependency field.

**Impact:** An AI may block the very validation needed to obtain user-environment Evidence, or take the opposite approach and hand over a build with a genuinely missing required safety prerequisite. This is an ambiguity about required-check scope, not proof that every missing AE test is safe to defer.

**Proposed correction:** Define pre-handoff prerequisites separately from the post-handoff validation question and final release acceptance. Align the scenario, checklist and optional record policy; keep the exact candidate and actual Test Status. Do not weaken mandatory safety/known-critical-risk controls.

**Acceptance:** A safe identified build whose unresolved question is intentionally user-only can follow the limited Validation Gate after its prerequisites. A missing mandatory pre-handoff safety check or known relevant FAIL still blocks that handoff. Release requires its complete applicable gate.

### F07 — PKG signature guidance remains generic in the canonical checklist

**Evidence:** [Release §28](../profiles/RELEASE.md) includes executable installer/packages in scope but lists final signature verification through `codesign`; the [Release checklist](../starter-kit/templates/RELEASE_CHECKLIST.md) has a generic `codesign PASS` item. The corrected [macOS verifier](../starter-kit/scripts/macos-bundle-verify.sh) explicitly uses `pkgutil --check-signature` for the PKG container and `codesign` for app/dmg. A PKG can also contain executable code requiring its own verification.

**Impact:** Following the wording mechanically can apply the wrong container check or overlook the distinction between package signature and nested-code signature. The tool correction exists; the backlog item is to make the normative guidance and checklist equally explicit.

**Proposed correction:** Describe container-format verification and nested-code verification separately. Use `pkgutil` for PKG container signature, applicable `codesign` checks for executable bundles/code, and format-specific Gatekeeper/stapling policy.

**Acceptance:** A PKG checklist identifies both its package signature Evidence and applicable payload-code Evidence, without requiring `codesign` as the PKG container verifier. Existing app/dmg and actual download/install/host-load requirements remain intact.

### F08 — Reversed section range passes manifest validation

**Reproduction:** In an owned temporary copy of the manifest and its canonical files, change only `PERF.section` from `17-19` to `19-17`; call `loadManifest(tempRoot)`. It returns successfully.

**Root cause:** [Manifest schema](../starter-kit/schemas/rules-manifest.schema.json) accepts both orders. [loadManifest()](../starter-kit/scripts/lib/applicability.mjs) constructs an array of length `end-start+1`; a negative length becomes an empty array, so no canonical heading is checked.

**Impact:** A malformed applicability range can be accepted and rendered as a source link without validating any of its intended sections. The current checked-in `17-19` range is correct; this is a negative-input validation hole.

**Proposed correction:** Parse section/range values explicitly; require bounded valid integers and start ≤ end, then validate every actual canonical section. Keep the separate R0 case.

**Acceptance:** `19-17` and unreasonable/missing ranges reject; `17-19`, valid single sections and R0 remain accepted. A missing heading in a valid range still rejects.

### F09 — Sparse pixels can produce a false PASS in the library

**Reproduction:** Set `actual = structuredClone(fixtures().gradient)`, then `actual.pixels = new Array(reference.pixels.length)`; call `compare(reference, actual, 0)`. Actual result: `status: PASS`, zero failed samples, but max error and RMSE are NaN; there are zero actual pixel values in 64 allocated slots. JSON output turns the nonfinite max value into null.

**Root cause:** [compare()](../starter-kit/scripts/lib/render.mjs) uses `Array.some` to validate values, which skips holes. Subtracting undefined slots yields NaN; `NaN > tolerance` is false, so no failure is counted.

**Boundary:** Reproduced for direct JavaScript library input. Serializing that sparse array to JSON yields null values, which the CLI/library subsequently rejects. This finding does not claim the JSON CLI accepts a sparse array.

**Proposed correction:** Require a dense own value at every pixel index, validate every value, and reject nonfinite derived metrics rather than emitting PASS.

**Acceptance:** Sparse/holey arrays reject; dense valid fixtures retain their expected results. Malformed input cannot yield PASS with NaN/null metrics.

### F10 — Whitespace-only N/A rationale passes recorded policy

**Reproduction:** Copy the illustrative native record, set each check to `N/A`, set its reason to `String.fromCharCode(32, 9, 10, 32)` (space/tab/newline/space) and set `evidence: []`; call `inspectRecord` with the current schema/registry. Actual result: `recorded_policy: PASS`, despite a required check having no visible rationale. `release_readiness` correctly remains NOT_ASSESSED.

**Root cause:** [inspectRecord()](../starter-kit/scripts/lib/project-record.mjs) tests `!check.reason`, which rejects an empty string but accepts whitespace. The schema places no non-whitespace constraint on reason.

**Proposed correction:** Require a nonempty trimmed rationale for N/A and define semantic approval as a separate project decision. Do not claim that a nonblank sentence proves justified applicability or reviewer approval.

**Acceptance:** Empty/whitespace-only N/A reasons reject. A substantive rationale remains structurally accepted; ownership, required-check selection and runtime correctness remain outside this validator's proof.

## Audit result and repair order

The five earlier items are retained and five additional items are recorded. All ten remain OPEN. No normative rules or runtime scripts were changed in this audit; a recorded finding is not a completed repair.

Recommended order:

1. Resolve decision/gate ambiguities F03/F06 and reconcile PKG guidance F07.
2. Align selected reading rules F01 and close the reproduced validation holes F08/F09/F10 with focused negative regressions.
3. Add no-progress handling F02 and compact traceability F04.
4. Supply controlled agent fixtures F05, then run the relevant scenarios on an actual configuration and retain traces.

Verification for this audit: isolated tool probes reproduced F01/F08/F09/F10; manual source review established the wording gaps and improvement scope. No live model or product AE runtime was run. Repository self-test/CI for the documentation update are recorded on its exact candidate in the pull-request path.
