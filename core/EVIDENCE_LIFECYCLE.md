# Evidence lifecycle

This guidance implements the existing identity/privacy/history requirements of Process Core §§7, 10 and 12. It adds no universal retention duration or mandatory new service.

Before a milestone, the project SHOULD record an owner, canonical storage, retention/revisit date and restore/check procedure for final artifacts, test reports, fixtures, logs and symbols. Retention depends on supported release lifetime and the sensitivity of user materials.

Evidence records SHOULD bind candidate commit, Build ID, final artifact hash, check/procedure version, UTC time, environment and test scope. Significant records reference stable IDs from [REQUIREMENTS.json](../REQUIREMENTS.json). Project requirements may extend the registry.

Store records outside sealed payload. Create a new record for each run; never rewrite historical results to match a later build. Failed/incomplete collection remains visible and cannot become PASS. Hashes establish integrity against a trusted expected value; they do not establish authorship if the record and data come from the same untrusted source.

At retention checkpoints, verify referenced files and hashes, check backup recovery in an owned workspace and identify broken links. Keep final release payload and matching dSYM/PDB for the declared support period. Record deliberate disposal and its impact; do not promise reproducibility after the necessary inputs have been discarded.

Publish a redacted summary where useful. Keep private logs, symbols, dumps and user projects in restricted storage. User materials and credentials do not belong in public test fixtures. Do not automatically upload diagnostics or change retention without the product's applicable consent/privacy contract.

The optional [project record schema](../starter-kit/schemas/project-record.schema.json) checks declared identity/status and Evidence file hashes. Required-check selection and approval are trusted project decisions; an untrusted report must not remove a required check. The validator does not run AE, establish a test oracle or authenticate reviewer approval.
