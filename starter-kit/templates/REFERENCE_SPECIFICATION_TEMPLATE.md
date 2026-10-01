# Reference Specification

## 1. Reference identity

| Field | Value |
| --- | --- |
| Product / reference | |
| Version / build | |
| Platform / architecture | |
| After Effects / host version | |
| Source / URL | |
| File / package | |
| SHA-256 | |
| Observed on | |
| Analysis authorization / license note | |

## 2. Reference scope

- Reference mode: **whole-product / feature / UI / behavior-render / multi-reference**
- Target scope:
- Explicit non-scope:
- User goal:
- Reference priority / precedence if multiple references:

## 3. Evidence sources

| Evidence ID | Type | Source / fixture | What it can prove | Limitation |
| --- | --- | --- | --- | --- |
| REF-E001 | runtime / static / docs / measurement | | | |

## 4. UI / control inventory

| ID | Group / order | Control | Type | Default | Min / max / step | Units | Enabled / visible rules | Animatable / expressions | Dependencies | Reference Claim Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UI-001 | | | | | | | | | | OBSERVED | |

Also record where applicable:

- group collapse/expand behavior;
- panel/effect resize;
- HiDPI/scaling;
- modifier keys/gestures;
- context menus/dialogs;
- focus/keyboard behavior;
- tooltips/help/error states;
- dynamic UI changes.

## 5. Functional behavior matrix

| Behavior ID | Feature/control | Input / precondition | Action / parameter state | Expected reference result | Boundary / interaction notes | Reference Claim Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BH-001 | | | | | | OBSERVED | |

## 6. Parameter sweep matrix

For continuous controls include minimum, near-minimum, default, representative low/mid/high, near-maximum, maximum and allowed extreme/out-of-range cases.

| Control | Case | Value | Relevant paired state | Reference output / behavior | Status | Evidence |
| --- | --- | ---: | --- | --- | --- | --- |
| | default | | | | OBSERVED | |

For discrete controls enumerate every reasonable option.

## 7. Preset inventory

| Preset ID | Name / category | Changed parameters | Unchanged parameters | Observable exact values | Output / behavior | Save/load/version notes | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRE-001 | | | | | | | OBSERVED | |

Also determine where applicable:

- preset order/categories;
- default/reset interaction;
- custom preset save/load;
- portability;
- behavior across versions.

## 8. State / persistence contract

| Scenario | Reference behavior | Status | Evidence |
| --- | --- | --- | --- |
| Initial defaults | | OBSERVED | |
| Reset | | OBSERVED | |
| Duplicate | | | |
| Copy / paste | | | |
| Undo / redo | | | |
| Project save / reopen | | | |
| AE restart | | | |
| Remove / re-add | | | |
| Preset save / load | | | |
| Version migration | | | |
| Missing / corrupted state | | | |

## 9. Animation / keyframes / expressions

| Scenario | Reference behavior | Status | Evidence |
| --- | --- | --- | --- |
| Keyframe interpolation | | | |
| Animated parameters | | | |
| Expressions | | | |
| Time-varying input | | | |
| Duplicate / copy animated state | | | |

## 10. Render / output contract

Record exact fixture identity for every comparison.

| Case | Fixture | Resolution / bpc / color | Parameter state | Render path | Reference result | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REN-001 | | | | preview / queue / aerender | | OBSERVED | |

Cover where applicable:

- alpha / transparency;
- premultiplied/unpremultiplied behavior;
- 8/16/32 bpc;
- HDR/extended values;
- color management / working space;
- ROI / frame bounds;
- pixel aspect / downsample;
- temporal behavior;
- CPU/GPU;
- MFR / Smart Render;
- repeatability.

## 11. Edge cases / errors

| Case | Input/state | Reference behavior | User-visible error | Recovery | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| EDGE-001 | | | | | | |

## 12. Performance baseline

| Case | Fixture | Resolution / bpc | Parameters | Hardware / host | Method | Reference result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PERF-001 | | | | | | | |

Document known performance cliffs or expensive parameters.

## 13. Packaging / integration

| Area | Observation | Status | Evidence |
| --- | --- | --- | --- |
| Install location | | | |
| AE discovery / menu category | | | |
| IDs / names | | | |
| Bundle/package structure | | | |
| Helpers/processes | | | |
| Permissions | | | |
| Dependencies | | | |
| Update / uninstall | | | |
| Observable licensing/activation behavior | | | |

Do not bypass access controls or treat observable activation behavior as permission to defeat it.

## 14. Static/internal claim ledger

Use this only for claims that go beyond directly visible runtime behavior.

| Claim ID | Claim | Status: PROVEN / OBSERVED / INFERRED / UNKNOWN | Evidence | Alternative explanation | Does Product Spec depend on this claim? |
| --- | --- | --- | --- | --- | --- |
| CLM-001 | | UNKNOWN | | | no |

No INFERRED claim may silently become a requirement for our internal architecture.

## 15. Reference Coverage Map

| Area | Scope | Coverage: COMPLETE / PARTIAL / BLOCKED / N/A | Key claim status | Evidence | Gap / impact |
| --- | --- | --- | --- | --- | --- |
| Identity / package | | | | | |
| UI / interaction | | | | | |
| Parameters / functionality | | | | | |
| Presets | | | | | |
| State / persistence | | | | | |
| Animation / keyframes / expressions | | | | | |
| Render / output | | | | | |
| Alpha / color / bit depth | | | | | |
| Edge cases / errors | | | | | |
| Performance | | | | | |
| Compatibility / host behavior | | | | | |
| Packaging / integration | | | | | |
| Internal implementation claims | | | | | |

## 16. Multi-reference mapping

If more than one reference exists:

| Target area | Reference used | Why | Conflict with another reference? | Resolution |
| --- | --- | --- | --- | --- |
| | | | | |

## 17. Target contract for our product

Translate reference evidence into the intended product behavior.

| Target ID | Desired behavior | Source reference / evidence | Exact parity required? | Allowed difference | Acceptance test |
| --- | --- | --- | --- | --- | --- |
| TGT-001 | | | yes / no | | |

The user’s product goals override blind copying. Explicitly record intentional differences.

## 18. Parity acceptance tests

| Test ID | Fixture / scenario | Reference expected | Our expected | Comparison method / tolerance | Gate |
| --- | --- | --- | --- | --- | --- |
| PAR-001 | | | | | |

## 19. Known gaps / unknowns

| Gap | Why unresolved | Status | Product impact | Next action |
| --- | --- | --- | --- | --- |
| | | INFERRED / UNKNOWN / BLOCKED | | |

## 20. Exit check

- [ ] Reference identity is fixed.
- [ ] Reference scope and non-scope are explicit.
- [ ] All material controls/features in scope are inventoried.
- [ ] Whole-product presets/state/render/edge/performance/package areas are covered or justified N/A.
- [ ] Reference Coverage Map is complete.
- [ ] Material claims have explicit Reference Claim Status.
- [ ] No critical UNKNOWN is disguised as a requirement.
- [ ] Target contract records intentional differences from the reference.
- [ ] Parity acceptance tests exist.
- [ ] Remaining gaps do not make Product Spec / Technical Design ambiguous.

## 21. Handoff

Reference Audit result:

- **COMPLETE / PARTIAL / BLOCKED**
- Reference Specification baseline date:
- Reference artifact/version:
- Critical gaps:
- Next step: **Product Discovery / Product Spec / Technical Design / more Reference Audit**
