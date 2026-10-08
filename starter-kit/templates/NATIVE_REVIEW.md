# Optional scoped native review (unreleased)

[Native §23](../../profiles/NATIVE.md#23-дополнительные-проверки-native-effects--render-plugins), [Engineering §14 / §41](../../core/ENGINEERING.md) retain existing host/render obligations.

- Exact candidate and preselected affected source paths/functions:
- SDK version/header path/digest and applicable Adobe source for actual API claims:
- Actual compiler/analyzer/sanitizer versions and commands/results:
- Coverage inventory (REVIEWED / UNREVIEWED / BLOCKED) and skipped scope impact:

| File/function / source digest | Memory bounds/lifetime | Numeric boundaries | Ownership/error/cancel | Concurrency/thread affinity | Units/scales | Basis/Evidence / gap |
| --- | --- | --- | --- | --- | --- | --- |
| <scope> | <status> | <status> | <status> | <status> | <status> | <actual inspection/check or gap> |

Each area: PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE with basis; NOT_APPLICABLE is an applicability decision, never a successful test. Pure single-thread fixture cannot certify AE checkout/checkin or MFR.

| Quantity | Input → output unit | Conversion / rounding / range / tolerance | Invariant / check | Current Evidence |
| --- | --- | --- | --- | --- |
| time | frames → seconds | <selected fps> | <inverse/boundary> | <actual> |
| geometry | image pixels → comp coordinates | <render scale/pixel aspect/ROI> | <declared spatial contract> | <actual or NOT_RUN> |
| color | selected integer channel scale → float/HDR | <chosen SDK maximum/bpc, no implicit HDR clipping> | <range/alpha/color-space contract> | <actual or NOT_RUN> |

Property/fuzz: same source, deterministic seed/corpus, iteration/time limits, independent invariant/oracle, counterexample/minimization record. Regression: same assertion fails original defect at intended marker and passes corrected bytes; setup/compile failure is not detection. No deletion of working code for TDD formality.

Optional schema `../schemas/native-review.schema.json`, Python 3.11+:

```sh
python3 starter-kit/scripts/check_native_review.py --record REVIEW.json --evidence-root PROJECT --expected-candidate FULL_SHA --required-path src/affected.cpp
```

Repeat `--required-path` for the trusted preselected scope. Actual source and Evidence digests are checked; declared review consistency is the only PASS claim. The tool does not independently discover missing functions/paths, run SDK callbacks, validate reviewers or certify Adobe SDK/runtime. Owners select the truthful scope and protected checker. Existing Evidence and render comparators remain authoritative for their recorded scopes.

Additive opt-in v1; no migration of existing Markdown required. Adopters preserve old record/checker versions and populate fresh current-candidate bytes, never rewrite historical Evidence.

The Evidence root is selected by the trusted caller and resolved to its actual directory identity (including OS aliases). It is not taken from the record; verify its ownership before invocation. Symlinks in source/Evidence paths below that root are rejected. The checker does not reject OS root aliases or replace filesystem sandbox/lease enforcement. Copy schema and both Python validator dependencies together; unknown fields/types fail closed in the v1 shapes, with additional candidate/scope/byte semantics checked separately.
