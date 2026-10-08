# Reference Evidence Obligations

Status: implemented conditional adapter for the existing Reference Audit and Evidence lifecycle. Standard verification uses synthetic adversarial fixtures. Actual AE/iPhone observations and deployment of a protected witness producer are separate product adoption work, not prerequisites for merging this standard. Product, market and publication changes are excluded.

## Trigger and existing authority

Use only for an explicitly selected reference/parity target. Keep the existing requirement → task → check → Evidence chain: `requirement_ids` and `check_id` name existing project requirements/checks, not a second registry. The ledger supplements the existing project record; it never replaces its required checks, authorizations or readiness verdict. Without a reference, no ledger is required. Existing routing already selects Reference Audit; no new universal overlay is introduced.

Before investigation, the project reviewer owns the coverage inventory, required case kinds, comparable authority and explicit exclusions. A candidate report cannot turn off the trigger, remove a behavior, change required to optional or lower authority. For local advisory use the reviewer supplies `--policy`; for enforced review policy is embedded in the externally pinned protected witness. An agent-authored policy is advisory only. The same reference decision/spec that owns the existing project check plan owns this projection.

## Schema v1 and execution

Schemas: [policy](../starter-kit/schemas/reference-policy.schema.json), [ledger](../starter-kit/schemas/reference-ledger.schema.json), [witness](../starter-kit/schemas/reference-witness.schema.json). Python 3.11+; standard library only. The CLI implements semantic validation as well as the structural contract. The earlier draft v1 omitted policy and execution metadata: migrate it before use; it now fails closed.

```sh
python3 starter-kit/scripts/check_reference_obligations.py /project/reference-ledger.json \
  --policy /reviewed/reference-policy.json --evidence-root /project \
  --expected-candidate-revision FULL_GIT_SHA
python3 starter-kit/scripts/check_reference_witness.py /project/reference-ledger.json \
  --protected-manifest /protected/witness.json --expected-manifest-sha256 EXTERNAL_PIN \
  --evidence-root /project --expected-candidate-revision FULL_GIT_SHA
```

Policy binds exact 40-character candidate Git SHA and reference SHA-256. `inventory` and obligation IDs must equal reviewed coverage. Each required obligation has one owner `{path, revision, sha256}`, existing requirement/check IDs, required case kinds, required authority, PASS status, original observations, candidate fixtures, verifier, and explicit empty contradictions/residual_unknowns. Owner and all Evidence paths are relative to the candidate root, regular files without symlinks or traversal. SHA-256 verifies actual local bytes. Exclusions require NOT_APPLICABLE, matching reason and decision reference from the reviewed policy.

Each Evidence record contains a globally unique evidence_id, artifact_path/artifact_sha256, status, authority, command, tool_version, UTC observed_at, environment and run_id. Original cases also name the exact reference_sha256 and PROVEN/OBSERVED claim status; candidate fixtures/verifier name the candidate revision. Original observations and verifier must meet the reviewed authority. `host` and `device` are distinct: an AE host observation cannot close an iPhone requirement. The fixture execution authority is recorded separately; generating a fixture never proves running the product.

The verifier artifact is typed JSON containing status, revision, obligation_id, check_id, requirement_ids, authority, environment and `case_results` mapping every reviewed case kind to PASS. A green headline with a failed/missing case, a prose report, a substituted owner or stale subject fails. The checker inspects results and hashes; it does not execute `command` or authenticate a self-authored report.

## Independent witness

The protected witness embeds the reviewed policy, reviewer_id, APPROVED review_status, reviewed_at/expires_at and captures. Each capture binds evidence_id, obligation_id, role (original_cases/fixtures/verifier), SHA-256 of the canonical complete Evidence record, runner_id and APPROVED review_status. This seals scenario, time/run, procedure/version, environment, authority and artifact identity together. Missing, duplicate, extra, expired, future, role-substituted or self-approved captures fail. The reviewer must differ from the capture runner. Real independence, allowed reviewer identities and custody are established outside candidate write permissions; arbitrary names in JSON do not authenticate identities.

Canonical digest: UTF-8 JSON, sorted keys, compact separators, ensure_ascii=False, no non-finite numbers. Duplicate JSON keys are rejected. The expected witness digest comes from protected configuration or an independent reviewer. [Protected provenance](PROTECTED_REFERENCE_PROVENANCE.md) and [setup](SETUP_TRUSTED_REFERENCE_EVIDENCE.md) define operational controls.

## Closure and limits

A required FAIL/BLOCKED/NOT_RUN produces nonzero CLI exit. Success means only the named consistency scope; output explicitly says parity_certified=false. All P0 gaps remain visible; no weighted percentage overrides a failed required case. Review must still establish that inventory is complete, observations happened, the procedure tests the intended behavior and any permitted differences are approved. No tool can discover every hidden behavior in a closed binary from an incomplete inventory.

[Offline helpers](REFERENCE_ENGINEERING_TOOLS.md) generate repeatable scenarios, find missing observed behaviors, compare first divergent events, map dependencies and changed components, and inspect visual buffers/tokens. Imported results join existing Evidence with exact inputs/procedure identity. Historical reuse follows the existing lifecycle: preserve original bytes/subject, record unchanged inputs and reviewer rationale; a component diff alone never transfers PASS to a new candidate.
