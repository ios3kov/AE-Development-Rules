# Protected reference observation provenance

Implemented: fail-closed policy, local artifact and pinned witness comparison. Not claimed: cryptographic runner authentication, configured repository protection, real AE/iPhone observations or end-to-end product parity.

The implementation agent MUST NOT be the sole authority for its own Evidence. The existing project spec/check plan owns required coverage; an independent reviewer or capture runner owns observations. Candidate PRs may propose records, but cannot approve or overwrite the protected baseline. Content digests prove integrity relative to an externally approved manifest, not truth of execution.

For every capture retain exact artifact/version, scenario/case and matched environment, command/tool version, UTC time, raw output digest, runner/run identity and reviewer decision. Redact private inputs without discarding the relationship to the raw restricted record. A witness binds the complete record to its obligation and role; every referenced regular file is checked locally. The combined CLI always runs ledger validation before witness acceptance. See the [format and command](REFERENCE_EVIDENCE_OBLIGATIONS_PROPOSAL.md).

The independently supplied pin seals policy and allowed captures together. The manifest records approval and expiry; replay against a different candidate or subject fails. Timestamp/reviewer strings are declarations until the protected capture producer/reviewer authenticates them. Verify identity, independence, authorization and custody outside candidate control. Without those controls, call the result advisory consistency, never trusted execution or product PASS.

Manual workflow runs only from main and pins verifier to its dispatch revision, checks out the exact candidate separately, compares checkout SHA to the requested SHA and reads candidate files as data. It never executes candidate scripts or commands from the ledger. Ledger/Evidence paths cannot escape the candidate root or use symlinks. Missing protected inputs fail. It emits only a safe verdict/error count and removes the temporary witness.

Standard CI runs synthetic fixtures and negative tests without witness secrets. Product adoption requires a separately authorized actual host/device capture, protected configuration, independent approval and current-candidate results. Those operational tasks do not block validation/merge of the standard itself. Synthetic fixtures are labelled and cannot certify real AE/iPhone behavior.
