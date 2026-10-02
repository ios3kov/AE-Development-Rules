# Release Checklist

This checklist is for a **Release Candidate**, not a normal Validation Build. For user validation use `VALIDATION_CHECKLIST.md`.

## Candidate identity

- [ ] Git state clean
- [ ] Commit fixed
- [ ] Build ID fixed
- [ ] Clean build/package completed
- [ ] Final SHA-256 recorded
- [ ] Candidate bytes frozen during Release Gate

## Regression

- [ ] Regression Level 1 PASS
- [ ] Regression Level 2 PASS
- [ ] Real AE smoke/integration PASS
- [ ] Restart/repeat PASS
- [ ] Relevant edge/error cases checked
- [ ] Compatibility matrix updated
- [ ] Each officially supported AE version has scoped actual runtime evidence (local or remote); exact artifact/loaded identity and AE build recorded, no inferred intermediate-version PASS

## Native/render where applicable

- [ ] Render Queue
- [ ] aerender/non-interactive path
- [ ] RAM Preview
- [ ] MFR/SmartFX
- [ ] 8/16/32 bpc
- [ ] alpha/HDR/color management
- [ ] cancellation/repeated render
- [ ] performance evidence

## Distribution

- [ ] Install/update/uninstall checked where applicable
- [ ] User guide matches this exact release
- [ ] Applicable install/update, first run/core workflow, supported versions and known limitations are covered; mandatory gaps are resolved before publication
- [ ] Supported AE versions come from compatibility evidence
- [ ] Known limitations documented
- [ ] Artifact type identified before applying signing gates
- [ ] Format-specific Adobe packaging requirements checked

## macOS distribution where applicable

- [ ] Agreed artifact format, target architecture and installation path recorded
- [ ] Final bytes/hash/manifest verified
- [ ] Package structure, resources and dependencies checked by scope
- [ ] Actual download through the selected channel observed
- [ ] System prompts/quarantine state and required user actions recorded honestly
- [ ] Installation succeeds using the documented steps in an owned test environment
- [ ] Runtime Build ID and host launch/load smoke PASS
- [ ] Update/uninstall and user-data preservation checked where applicable
- [ ] Known install limitations documented; no unsupported warning-free claim
- [ ] No unapproved changes to user/system security settings

Apple account/certificate/service access is not a prerequisite. Integrity-tool PASS does not establish install or host-load PASS.

## Windows distribution where applicable

- [ ] Agreed artifact format, target architecture and installation path recorded
- [ ] Final bytes/hash/manifest verified
- [ ] PE architecture/dependencies checked where applicable
- [ ] Actual download through the selected channel observed
- [ ] System prompts/Zone.Identifier and required user actions recorded honestly
- [ ] Installation succeeds using documented steps in an owned test environment
- [ ] Runtime Build ID and host launch/load smoke PASS
- [ ] Update/uninstall and user-data preservation checked where applicable
- [ ] Known install limitations documented; no unsupported warning-free claim
- [ ] No unapproved changes to user/system security settings

Certificate/signing-service access is not a prerequisite. Integrity-tool PASS does not establish install or host-load PASS.

## Final decision

- [ ] No mandatory Test: FAIL
- [ ] No mandatory Test: BLOCKED / NOT RUN
- [ ] Every Test: N/A has a reason
- [ ] Evidence belongs to this exact candidate

## After confirmed publication

Follow [Release §26](../../profiles/RELEASE.md#пользовательская-документация-и-передача-после-релиза).

- [ ] Final reply contains verified release and version-matching user-guide links/accessible paths
- [ ] User is explicitly invited to open the install/getting-started instructions
- [ ] Additional documentation gaps have a concrete proposed next scope; when none exist, direct the user to the existing guide
- [ ] A subsequent “what next?” first checks documentation and points to the guide or identifies the actual gap

These are handoff actions after publication, not results to mark complete in advance. A missing mandatory guide is not an optional follow-up; report a late discovery honestly without silently rewriting released artifacts/tags. Additional documentation does not authorize product changes or a new publication.
