# Conditional offline reference engineering tools

These helpers import authorized, sanitized observations; they do not install or run Ghidra, Frida, LLDB, Rever, browser automation, extracted binaries, AE or an iPhone. Existing Reference Audit selects this work. Use matched identities and the existing Evidence/check records. All commands return JSON and nonzero on FAIL/BLOCKED. Generated fixtures and diagrams are analysis artifacts, not executed-test Evidence.

Python 3.11+, stdlib:

```sh
python3 starter-kit/scripts/reference_engineering.py compile observations.json --evidence-root /candidate
python3 starter-kit/scripts/reference_engineering.py compare event-traces.json
python3 starter-kit/scripts/reference_engineering.py graph dependency-graph.json
python3 starter-kit/scripts/reference_engineering.py version-diff component-snapshots.json
python3 starter-kit/scripts/reference_engineering.py route /candidate/reference.bin --capabilities tool-inventory.json
python3 starter-kit/scripts/reference_engineering.py metrics actual-call-trace.json
python3 starter-kit/scripts/reference_ui.py tokens observed-controls.json
python3 starter-kit/scripts/reference_ui.py contrast contrast-pair.json
python3 starter-kit/scripts/reference_ui.py compare rgba-captures.json
```

## Data contracts

`compile`: inventory is a list of reviewed behavior IDs; observations contain behavior_id, unique case_id, claim_status PROVEN/OBSERVED, evidence_id, artifact_path/artifact_sha256, preconditions, input, action, expected and environment. Every inventory behavior needs observations. Missing behaviors produce BLOCKED and a gap list. Provenance/hashes are checked; generated fixtures carry execution_status=NOT_RUN. A target-specific runner must interpret the scenario and execute assertions at the right authority. Adapt to existing E2E/parity runners; do not evaluate arbitrary code from imported actions.

`compare`: reference/candidate event arrays plus equal nonempty reference_environment/candidate_environment. Events record state/action/output, cancellation, failure and recovery with stable ordering. Exact comparison reports the first divergent event including missing/extra events. Before importing, approve deterministic normalization of correlation IDs/time noise in the spec; preserve raw traces and normalization identity. This tool does not infer causality or silently ignore fields.

`graph`: nodes `{id, layer, claim_status, evidence_id}` and edges `{from, to, claim_status, evidence_id}`. Layers can map UI → API → process → native symbol/storage; location/address and artifact digests stay in the source observation record. PROVEN/OBSERVED nodes and edges need Evidence. Unknowns remain explicit. The tool rejects dangling/duplicate edges and emits Mermaid using safe IDs, not arbitrary decompiler text. It imports graph facts; obtaining xrefs/callers from Ghidra is a separate authorized capability.

`version-diff`: before/after snapshots each bind artifact_sha256 and components mapping name/address to `{sha256, obligation_ids}`. The tool reports added/removed/changed entries and affected obligations from both snapshots. Bind exports to exact source binary/tool/version in existing Evidence. Declared equal component hashes do not establish identical behavior, ABI or dependencies. Required fresh checks/reuse review follow the existing Evidence lifecycle.

`route`: file magic chooses Mach-O/PE-candidate/ELF static Ghidra operations, ZIP/archive inventory (including IPA), or JSON/HAR offline trace handling. A suffix alone never proves a native format. `capabilities` has tools `{name, version, operations, probe_status}`; missing/versionless/unprobed operations block the plan. Archive routing stops at inventory; manually confirm executable type/signing/architecture after extraction. Tool inventory must come from actual safe help/version/probe calls, not guessed availability. The plan records artifact digest and execution_status=NOT_RUN. Dynamic analysis requires the separate authorization/isolation decision in the playbooks.

`metrics`: actual calls `{tool, operation, input_digest, usable, tokens, cost, retry_reason?}` and optional expected_first_tool/selected_first_tool. It totals explicitly recorded usage, reports unusable calls, unexplained identical retries and first-tool match. Unknown usage must be left unmeasured, not supplied as zero; obtain tokens/cost from the actual provider receipt. This evaluates declared receipts, not the agent's honesty. Stop/replan repeated failures instead of repeating indefinitely.

`tokens`: controls with evidence_id and optional colors (opaque sRGB hex), font_sizes and spacing arrays. It deduplicates observed tokens; it does not infer tokens/typography from a screenshot. Retain observation source and uncertainty for approximate measurements. No foreign fonts/assets are imported automatically.

`contrast`: foreground/background opaque sRGB hex plus the reviewed minimum_ratio. Computes the [WCAG relative luminance contrast formula](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Select applicable text/non-text/large-text threshold in the existing accessibility contract; translucent/HDR/color-managed combinations must be composited in the actual matched environment first. The ratio alone is not accessibility certification.

`reference_ui compare`: reference/candidate captures contain width, height, bit_depth (8/16/32), color_space, alpha_mode, device, viewport, scale, font_identity, render_path and full row-major RGBA arrays. 8/16 channels are unsigned integers; 32 channels are finite floats with extended range allowed. Supply named integer-bound regions and optional reviewed tolerance in native channel units. All pixels, including alpha and differences outside named regions, are compared without resizing or flattening. Capturing/exporting correct buffers is a separate runner capability. Record raw-buffer digest, color/alpha interpretation and approved tolerance in Evidence. AE projects can continue to use the existing render comparator; this adapter does not replace it.

See the [synthetic example](../starter-kit/examples/reference/README.md) and executable negative fixtures in `test_reference_*.py`. Full product coverage requires review of the inventory, graph omissions, trace semantics and source observations; automated consistency is bounded by those inputs.

## Optional REA source-observation producer

For an explicitly authorized shipped-artifact investigation, use the [corrected pinned REA integration](https://github.com/ios3kov/production-engineering/tree/60845687c4d7c8a4ad01d1fbe6ec9aeb55ac1e31/integrations/rea) as an optional producer, not a replacement for this standard. Its rea-agents 6.5.0 profile retains package metadata inventory and focused Ghidra plans subject to actual host/engine checks. The original six-group shortlist is planned scope, not blanket admission. Source review, dates, licensing and verification basis are registered under [SRC-REA-STATIC-INTEGRATION](../SOURCES.md#src-rea-static-integration).

**JS-derived analysis is BLOCKED in this profile.** [Upstream issue 3551](https://github.com/morluto/rea/issues/3551) reports that renamed Webpack factory parameters can silently lose CommonJS exports while 6.5.0 reports exact/complete coverage. The corrected planner blocks JavaScript analysis, feature/semantic traces, application comparisons and mixed-origin retained views/Evidence comparisons even when advertised. Do not admit such export/absence claims from older reports. Reopening requires a corrected exact package and real regression qualification covering renamed and shadowed bindings; neither the earlier simple smoke nor a pending patch proves a fix.

The planner does not execute commands or enforce a sandbox. Raw receipts never become product PASS; preserve and review subject identity, coverage, contradictions and unknowns through existing local-tool admission and requirements/checks/Evidence. No automatic installation, client registration, generic debugger/device commands or runtime capture is authorized. Ordinary source work does not load REA. Historical Linux ZIP/JS/summary smoke establishes only its fixture scope, not Ghidra, macOS DMG/dylib, AE or physical-iPhone validation. Existing Reference Audit, permissions, release gates and accepted baseline remain unchanged.
