# Update Security Review

Use only if the product checks, downloads or installs updates.

## Trust model

- Update endpoint/origin:
- Transport:
- Artifact signer:
- Metadata signer/source:
- Trust anchors:
- Downloader:
- Installer:

## Checks

- [ ] HTTPS or equivalent protected transport
- [ ] Endpoint/origin validated
- [ ] Metadata treated as untrusted until verified
- [ ] Downloaded artifact signature or authenticity verified before execution
- [ ] Hash is obtained through a protected trust path
- [ ] Path traversal/destination escape blocked
- [ ] Partial download handled safely
- [ ] Version compatibility validated
- [ ] Failed update has recovery/rollback
- [ ] Dangerous downgrade policy defined
- [ ] No permanent secrets embedded in client
- [ ] Update logs do not leak credentials

## Adversarial cases

- modified metadata:
- modified package:
- truncated download:
- stale version:
- downgrade:
- invalid signer:
- unavailable server:
- interrupted install:

## Result

**PASS / FAIL / BLOCKED / NOT RUN / N/A**
