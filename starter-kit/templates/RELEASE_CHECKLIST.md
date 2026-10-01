# Release Checklist

## Candidate identity

- [ ] Git state clean
- [ ] Commit fixed
- [ ] Build ID fixed
- [ ] Clean build/package completed
- [ ] Final SHA-256 recorded
- [ ] Candidate bytes frozen during validation

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

- [ ] Install/update/uninstall checked
- [ ] User guide matches this exact release
- [ ] Supported AE versions come from compatibility evidence
- [ ] Known limitations documented

## Public macOS release where applicable

- [ ] Developer ID
- [ ] Notarization Accepted
- [ ] Stapling validated
- [ ] codesign PASS
- [ ] Gatekeeper PASS
- [ ] Real quarantined download
- [ ] Standard install
- [ ] Host launch/load smoke PASS
- [ ] No security bypass required

## Final decision

- [ ] No mandatory FAIL
- [ ] No mandatory BLOCKED/NOT RUN
- [ ] Every N/A has a reason
- [ ] Evidence belongs to this exact candidate
