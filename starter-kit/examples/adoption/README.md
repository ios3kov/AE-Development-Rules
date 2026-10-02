# Filled adoption examples

These are complete illustrative contracts. The products and candidate IDs are examples, not tested deliverables. All required runtime checks intentionally remain NOT RUN. Zero commit/hash values identify unbuilt example candidates; replace them with actual identity before adoption. The recorded baseline version 4.1.0 is the earlier unreleased remediation example, not the current 5.0.0 candidate or an accepted release. On actual adoption, consciously select the baseline, record its exact commit and apply its migration; these historical illustrative records are not rewritten as new Evidence.

## Native effect

Target: AE 2025+, macOS arm64; exact host/OS versions are selected before testing. Change: CPU/GPU implementation of a color transform. Risk Standard unless render ownership/threading/architecture changes make it Critical. Delivery Development for the internal milestone.

Acceptance: same fixture and parameter state on CPU/GPU; approved numeric tolerance; no unintended alpha/extended-range clipping; cancellation leaves buffers/checkout ownership correct. Run pure algorithm tests, structural packaging checks and owned AE tests for bit depth, preview/queue and claimed MFR/SmartFX. Use [render fixtures](../render/README.md); record actual host/project identity and difference output. See [native record](native.json).

A release switches Delivery Gate and selects actual installation/host-load checks separately. Apple distribution-service access is not a prerequisite under the current macOS policy.

## JSX micro helper

Target: a small command renaming selected layers in AE 2025+, no filesystem/network/persistence/installer. Risk Light; Delivery Release when published.

Acceptance: only selected unlocked layers change; absent comp/selection is a safe no-op with understandable feedback; exception closes the Undo group; Undo/Redo restores/reapplies intended names. Run syntax-subset and host smoke/negative/Undo tests against the exact saved JSX. Confirm source/artifact identity, restart/repeat behavior and a short matching user guide. See [JSX record](jsx.json).

Public distribution changes Delivery Gate, without automatically making this command Critical or requiring OS executable signing. Add risks/checks if a helper executable or installer is introduced.

## CEP panel

Target: maintained existing CEP panel in AE 2025+, documented migration/exit plan for the vendor lifecycle. Risk Standard; Delivery Validation for a limited reload/bridge question.

Acceptance: one request triggers one host mutation; malformed/timeout replies give a recoverable error; reload creates no duplicate listeners; stale async response cannot modify a newer host context. Run protocol/state tests with a fake transport, then actual panel/bridge/JSX tests in the selected host. Use correlation IDs, exact component versions and a minimal user validation scenario. See [CEP record](cep.json).

Validation does not require final public packaging, but available internal checks and data safety cannot be delegated to the user. Each example's actual required set is selected by the project owner before execution; the sample record is not a universal exhaustive release policy.
