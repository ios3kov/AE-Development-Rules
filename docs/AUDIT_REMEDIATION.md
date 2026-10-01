# Audit remediation

Baseline: v4.0.0 / 58d14aa12375757f4e52396d951f1557ae4f453c.
Scope: A01–A13 and the adoption, routing, Evidence and governance improvements from the 2026-10-01 audit. No merge or public release is part of this change.

## Acceptance

- R1: artifact records bind file types, paths, executable modes and safe internal symlinks; historical records cannot be overwritten.
- R2: missing required tools, unreadable candidate input and failed required probes cannot report successful completion.
- R3: bundle checks state their exact scope; required stapling/timestamp checks fail closed.
- R4: applicability data is strictly validated and routing scenarios preserve independent risk/delivery axes.
- R5: directives/includes work within a documented JSX syntax subset; unresolved includes fail.
- R6: workspace creation resolves ownership safely and rejects symlinked configured ancestors.
- R7: milestone and micro-helper requirements agree across canonical text and templates.
- R8: stable requirement IDs, project records, adoption examples, visual fixtures, Evidence lifecycle and change governance are documented and tested.

## Verification ledger

| Scope | Status | Evidence |
| --- | --- | --- |
| A01–A13 regression and adjacent behavior | NOT RUN | Pending implementation |
| Manifest/routing/project-record/visual tests | NOT RUN | Pending implementation |
| Linux/macOS/Windows CI | NOT RUN | Pending candidate commit |
| Actual AE load, notarization, Windows signing | N/A | No product or release candidate is being certified; wrapper contracts use isolated fixtures |

Test stubs establish wrapper behavior only. Source freshness is verified from primary documentation. This record is updated before handoff.
