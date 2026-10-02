# Remote AE compatibility check packet

Use with [Engineering §21](../../core/ENGINEERING.md#21-совместимость-и-применимость-технологий) and the existing [test record](TEST_RECORD.md). This is a template, not a run result. Embed it in existing records when appropriate. Preparing a packet does not authorize sending it, installation, restarting AE or modifying someone else's project/system.

## Packet prepared before execution

- Product/component / agreed acceptance scope:
- Candidate commit / Build ID / final artifact SHA-256 / package manifest:
- Target full AE version/build / OS / architecture; GPU/driver/render path where relevant:
- Reason this target is selected / static audit link / unresolved risks:
- Owned disposable fixture path + hash, or deterministic creation instructions:
- Fixture format compatibility with target AE / creation dependencies:
- Documented install/update/load steps and rollback preserving existing plugin/user data:
- Expected loaded identity and procedure to observe it:
- Scenario steps and expected outputs/tolerances; applicable core workflow, error, save/reopen, Undo and render/depth cases:
- Expected output locations / logs to retain / sanitization / stop conditions:
- Execution authorization / owned test environment / responsible operator:

Use synthetic data. Do not request private production projects or secrets where a fixture suffices. Do not assume a newer project file opens in older AE. Do not bypass installation permissions or global system security settings. Keep artifact bytes fixed; a repair creates a new candidate and needs its own relevant checks.

## Operator run record — fill only after actual execution

- Timestamp / operator / environment:
- Observed complete AE version and build:
- Observed OS/version, architecture, GPU/driver where applicable:
- Received artifact SHA-256 / manifest verification result:
- Installed path / observed loaded Build ID (for scripts, hash + path of executed file):
- Identity match / mismatch and evidence:
- Actual fixture identity / initial state:

| Check ID / scenario / scope | Expected outcome | Actual observation | Test Status | Evidence path/hash / limitation |
| --- | --- | --- | --- | --- |
| <actual check> | <agreed expectation> | <none until run> | NOT RUN | <reason/condition> |

Use PASS / FAIL / BLOCKED / NOT RUN / justified N/A as Test Status. Record output files, relevant logs and a reproducible observation; a screenshot or “works for me” alone cannot establish all criteria. Report interrupted/missing cases separately. Redact personal data without dropping the identity or failure facts required for verification.

## Reviewer decision

- Observed candidate matches packet / actually loaded identity:
- Completed checks and untested paths / known issues:
- Compatibility Status: VERIFIED / STATIC-COMPATIBLE / LIMITED / UNKNOWN / UNSUPPORTED:
- Exact scope/configuration covered and Evidence links:
- Required remaining tests / next action and condition for execution:

VERIFIED requires real target AE execution, matching identity and sufficient evidence for the stated scope. One load smoke is not evidence for all rendering, GPU/MFR, save/reopen or other builds. Missing identity/observations cannot establish VERIFIED. A runtime FAIL determines compatibility only after reviewing its cause; do not automatically classify every environment/test failure as UNSUPPORTED. Remote testing does not certify untested versions or future hosts.
