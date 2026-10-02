# Validation Build Checklist

Use this checklist for a **limited user validation build**. It is not a Release Checklist.

## Validation question

- What exactly must the user confirm?
- Why can this not be fully verified in the developer environment?
- What outcome counts as success?

## Artifact identity

- [ ] Source state clean; user handoff excludes dirty experimental builds
- [ ] Git commit / source version recorded
- [ ] Build ID or equivalent identity recorded
- [ ] Artifact hash recorded where practical
- [ ] Artifact clearly marked as validation/test build if not release-ready

## Internal checks before handoff

- [ ] Pre-handoff prerequisites identified before execution, including safety checks
- [ ] Every mandatory pre-handoff prerequisite PASS or justified N/A; none BLOCKED / NOT RUN
- [ ] Relevant fast/static checks completed
- [ ] Main validation scenario has no mandatory Test: FAIL
- [ ] No known critical data-loss/security/project-corruption issue
- [ ] Known limitations listed
- [ ] Required user steps are minimal and safe

| Check / acceptance | Phase | Required? | Actual Test Status | Evidence / unresolved condition |
| --- | --- | --- | --- | --- |
| <safety/internal prerequisite> | pre-handoff | yes | <actual status> | <evidence> |
| <specific user-only question> | user-validation | yes | NOT RUN | <user environment / success criterion> |
| <final release check> | release-acceptance | yes | NOT RUN | <applies to final release> |

A pending user-only question does not block this limited handoff after prerequisites pass. Missing mandatory prerequisites or a known mandatory FAIL for the tested scenario still block it. Do not relabel an accessible internal check to bypass the gate.

## Not automatic requirements

The following are **not automatically required** unless they are part of the validation question or affected risk:

- Regression Level 2
- final public installer/package
- public download-channel test
- full compatibility sweep
- deep profiling
- final release documentation

## User instruction

- Build/version:
- Steps:
- Expected result:
- What evidence to return:

## Result

- Evidence Confidence: **PROVEN / USER-REPORTED / OBSERVED / UNVERIFIED**
- Result:
- Remaining internal checks:
- Next action:
