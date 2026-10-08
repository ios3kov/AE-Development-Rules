# Verifier protection — read-only audit and prepared changes

Checked 2026-10-08 via authenticated GitHub connector, against main `a43c75aba8c714658822277835909c4726d5a523`:

| Query | Actual result |
| --- | --- |
| GET branches/main | `protected: false`; protection enabled false; status-check enforcement off; contexts/checks empty |
| GET rulesets | Empty list `[]` |
| GET branches/main/protection | 403 `Resource not accessible by integration`; administration details unavailable to connector |

The branch endpoint explicitly reports no main protection; no rulesets are visible. Detailed administrative bypass/reviewer/environment settings remain NOT_VERIFIED, not inferred from CODEOWNERS or workflow text. No GitHub settings were changed. This is an operational enforcement gap, not a failing offline standard contract.

## Prepared owner actions — require separate authorization

1. Protect main and the immutable verifier/policy source: require PR review by independent owners, dismiss stale approvals, require last-push approval, restrict bypass/force-push/deletion as applicable. Do not permit a candidate author to weaken the checker or protected policy as part of their approval.
2. Require the actual observed check names: `self-test (ubuntu-latest)`, `self-test (macos-latest)`, `self-test (windows-latest)` and `reference-obligation-tests`, bound to the intended GitHub Actions app. Reconfirm names/identity before applying; synthetic success does not approve a skill/product.
3. On the existing `reference-evidence` environment, set independent required reviewers, prevent self-review/bypass as supported, restrict dispatch to main, and protect policy/witness pins. Reuse that custody boundary for skills; do not place policy approval/exception editing in candidate permissions.
4. Grant one owner to the new verifier, §43, schemas, evaluation observer and workflow; review checker/policy changes independently. CODEOWNERS is only routing until enforced review is actually enabled.
5. Store `TRUSTED_SKILL_POLICY_JSON` and independent `TRUSTED_SKILL_POLICY_SHA256` pin under the same protected custody; scope valid package/source/candidate and expire admissions. Preserve original witness settings for reference mode. Never run candidate scripts while exposing these values.
6. After authorized setup, retrieve actual protections/rulesets/check identities/environment reviewer controls and exercise a rejected tampered candidate. Record exact policy/verifier/candidate and independent result through the existing Evidence lifecycle. Do not label protection PASS from configuration intent.

Operational protection setup and authentic scanner/reviewer custody are BLOCKED for enforced use until independently established. Local tooling and synthetic CI remain useful for bounded consistency review.
