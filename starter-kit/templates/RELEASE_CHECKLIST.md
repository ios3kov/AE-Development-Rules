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
- [ ] Supported AE versions come from compatibility evidence
- [ ] Known limitations documented
- [ ] Artifact type identified before applying signing gates
- [ ] Format-specific Adobe packaging requirements checked

## Public macOS executable release where applicable

- [ ] Gate applicability documented
- [ ] Developer ID
- [ ] Notarization Accepted
- [ ] Stapling validated where applicable
- [ ] codesign PASS
- [ ] Gatekeeper PASS
- [ ] Real quarantined download
- [ ] Standard install
- [ ] Host launch/load smoke PASS
- [ ] No security bypass required

## Public Windows executable release where applicable

- [ ] Gate applicability documented
- [ ] Authenticode/code signing where required
- [ ] Timestamp/signature verification
- [ ] Architecture/dependency audit
- [ ] Standard install
- [ ] Host launch/load smoke PASS
- [ ] No Defender/SmartScreen/UAC bypass required

## Final decision

- [ ] No mandatory Test: FAIL
- [ ] No mandatory Test: BLOCKED / NOT RUN
- [ ] Every Test: N/A has a reason
- [ ] Evidence belongs to this exact candidate
