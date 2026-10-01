# Debugging Record: <issue / symptom>

## Context

- Date/time:
- Risk Profile:
- Delivery Gate:
- Git commit:
- Build ID:
- Artifact / SHA-256:
- After Effects:
- OS / architecture:
- Component / runtime:

## Symptom

- Expected:
- Actual:
- Impact:
- Reproduction steps:
- Reproducible: `yes | no | intermittent`

## Initial Evidence

- Logs:
- Stack trace / error code:
- Host/API result:
- Crash dump / diagnostics:
- User-reported evidence:
- Relevant timing/state:

## Failure layer

- [ ] UI / controller
- [ ] ExtendScript / ScriptUI
- [ ] CEP bridge
- [ ] UXP runtime
- [ ] Host API
- [ ] Helper / IPC
- [ ] Filesystem / network
- [ ] Native callback / render path
- [ ] Packaging / runtime environment
- [ ] Unknown

## Facts

- <directly observed fact>

## Hypotheses

| Hypothesis | Why plausible | Falsifying / confirming observation | Status |
| --- | --- | --- | --- |
| <hypothesis> | <evidence> | <expected experiment result> | open / rejected / supported |

## Diagnostic experiment

- Hypothesis under test:
- Single variable / smallest change:
- Instrumentation added:
- Exact scenario rerun:
- Result:
- New Evidence:
- Conclusion:

## Root cause

- Confirmed cause:
- Evidence Confidence:
- Scope / limitations:

## Fix

- Minimal fix:
- Why this addresses the cause:
- Side effects / risks:

## Regression

- Regression test / fixture:
- Before fix:
- After fix:
- Related existing scenarios rechecked:

## Cleanup

- [ ] Temporary instrumentation removed or intentionally retained
- [ ] Clean artifact rebuilt where applicable
- [ ] Final scenario repeated
- [ ] Evidence belongs to final checked artifact
