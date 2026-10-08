# Verifier protection — active branch controls and remaining custody gates

## Active owner configuration — 2026-10-08

After explicit owner authorization, branch protection was enabled and independently read back through the owner API against release commit `f276b9507a4fbccd239d2f32fafe40b87efac4a0` (`v10.0.1`).

| Control | Actual result |
| --- | --- |
| Required pull request | Enabled; direct update rejected with GH006 |
| Required status checks | Strict/up-to-date; all four names below bound to GitHub Actions app ID `15368` |
| Admin enforcement | Enabled |
| Force push / branch deletion | Both disabled |
| Conversation resolution | Required |
| Stale review dismissal | Enabled |
| Required approving reviews / code owner review / last-push approval | `0` / false / false; independent reviewer custody remains BLOCKED |

Required check names: `self-test (ubuntu-latest)`, `self-test (macos-latest)`, `self-test (windows-latest)`, `reference-obligation-tests`. The actual GitHub Actions app identity was observed on the final correction PR before applying the controls.

Enforcement probe: commit `680e18bb24c3d09c3bf582ffb26affced6d24caf` was an ordinary fast-forward child of release commit `f276b9507a4fbccd239d2f32fafe40b87efac4a0` with the identical tree `e77f800478cbff3050f267900393f52a7d0ce495` and zero changed files. A direct push to main was rejected: `Changes must be made through a pull request` and `4 of 4 required status checks are expected`. No force push or deletion was attempted; main remained unchanged. This proves that direct unchecked updates are blocked for the current owner's credentials. It does not prove independent review of a checker/policy change whose synthetic checks pass.

The owner selected themselves as the human reviewer. Chat authorization permits this release but is not an independent GitHub approval event; no approval was impersonated. Requiring another GitHub approver without an identified eligible person would prevent the sole owner from maintaining the repository. The current configuration therefore enforces PR/CI while leaving independent verifier/policy approval explicitly BLOCKED.

The existing `reference-evidence` environment was read without changing its controls: reviewer `ios3kov`, admin bypass false, self-review prevention false, custom branch policies enabled. Its independent reviewer and protected witness/policy custody are not established by branch CI. No witness, skill policy or digest was invented, read from secrets, or replaced. An authenticated tampered-candidate witness/admission test remains NOT_RUN.

The release tag, archives and release-evidence.json remain frozen at the exact release commit. They describe the publisher's source/CI scope and preserve its BLOCKED custody result. This later operational record supplies the actual branch controls; it does not upgrade that historical result to a general security certificate.

## Historical read-only audit before setup

Checked 2026-10-08 via authenticated GitHub connector, against released main `d65baf37d76cc7c25981250d64a8d93c55c4bff2` for the 10.0.1 correction review:

| Query | Actual result |
| --- | --- |
| GET branches/main | `protected: false`; protection enabled false; status-check enforcement off; contexts/checks empty |
| GET rulesets | Empty list `[]` |
| GET branches/main/protection | NOT_RUN for this review; previous audit received 403 `Resource not accessible by integration`; current administration details remain NOT_VERIFIED |

The branch endpoint explicitly reports no main protection; no rulesets are visible. Detailed administrative bypass/reviewer/environment settings remain NOT_VERIFIED, not inferred from CODEOWNERS or workflow text. No GitHub settings were changed. This is an operational enforcement gap, not a failing offline standard contract.

## Remaining custody actions

1. Protect main and the immutable verifier/policy source: require PR review by independent owners, dismiss stale approvals, require last-push approval, restrict bypass/force-push/deletion as applicable. Do not permit a candidate author to weaken the checker or protected policy as part of their approval.
2. Require the actual observed check names: `self-test (ubuntu-latest)`, `self-test (macos-latest)`, `self-test (windows-latest)` and `reference-obligation-tests`, bound to the intended GitHub Actions app. Reconfirm names/identity before applying; synthetic success does not approve a skill/product.
3. On the existing `reference-evidence` environment, set independent required reviewers, prevent self-review/bypass as supported, restrict dispatch to main, and protect policy/witness pins. Reuse that custody boundary for skills; do not place policy approval/exception editing in candidate permissions.
4. Grant one owner to the new verifier, §43, schemas, evaluation observer and workflow; review checker/policy changes independently. CODEOWNERS is only routing until enforced review is actually enabled.
5. Store `TRUSTED_SKILL_POLICY_JSON` and independent `TRUSTED_SKILL_POLICY_SHA256` pin under the same protected custody; scope valid package/source/candidate and expire admissions. Preserve original witness settings for reference mode. Never run candidate scripts while exposing these values.
6. After authorized setup, retrieve actual protections/rulesets/check identities/environment reviewer controls and exercise a rejected tampered candidate. Record exact policy/verifier/candidate and independent result through the existing Evidence lifecycle. Do not label protection PASS from configuration intent.

Independent verifier/policy and authentic scanner/reviewer custody remain BLOCKED for enforced use until independently established. The branch PR/CI controls above are enabled and their direct-push rejection is PASS. Local tooling and synthetic CI remain useful for bounded consistency review.
