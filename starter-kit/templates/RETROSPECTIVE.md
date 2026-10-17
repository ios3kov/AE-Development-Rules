# Technical Retrospective: <milestone/version>

## Scope

- Product:
- Version/milestone:
- Git commit:
- Build ID:
- AE/SDK/OS scope:

## What is proven to work?

For each item record context, solution/pattern, evidence, scope, limitations and whether it is reusable.

Use **Evidence Confidence** only:

- **PROVEN**
- **USER-REPORTED**
- **OBSERVED**
- **UNVERIFIED**

## What failed or should not be repeated?

Record the experiment outcome separately from Evidence Confidence:

- outcome: `accepted` / `rejected`;
- why;
- evidence;
- safer replacement.

Do not use `FAILED` as an evidence label; `FAIL` belongs to Test Status.

## New AE know-how

Cover relevant host/API behavior, lifecycle/threading, render/MFR/SmartFX, UI/AEGP, coordinates, keyframes/Undo, bit depth/color, packaging/signing and diagnostics/testing.

## Best engineering decisions

- <decision + why + evidence>

## Selected reusable improvement, if warranted

Use [Engineering §25.1](../../core/ENGINEERING.md#251-ретроспектива-и-накопление-ae-know-how); a completed retrospective need not add a rule.

- Observed session issue and supporting Evidence:
- Existing check/rule and why it did not prevent the issue:
- Smallest useful correction, or reason to leave the process unchanged:
- Where it belongs, how to verify it, and limits of the conclusion:
