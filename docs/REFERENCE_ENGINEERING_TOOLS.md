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
