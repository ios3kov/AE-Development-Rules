# Dependency / License / Vulnerability Audit

## Identity

- Product:
- Git commit:
- Build ID:
- Artifact:
- Date:

## Dependency inventory

| Dependency | Version | Source | Production? | License | Pinned/locked? | Notice obligations |
| --- | --- | --- | --- | --- | --- | --- |
| <name> | <version> | <source> | yes/no | <license> | yes/no | <notes> |

Attach local manifest/lockfile evidence from:

- macOS/Linux: `starter-kit/scripts/collect-dependency-evidence.sh`
- Windows: `starter-kit/scripts/collect-dependency-evidence.ps1`

## Vulnerability audit

| Scanner / source | Scope | Result | Blocking findings | Evidence |
| --- | --- | --- | --- | --- |
| <tool> | <scope> | **PASS / FAIL / BLOCKED / NOT RUN / N/A** | <findings> | <file/link> |

## SBOM

- Generated: yes/no/N/A
- Format: SPDX / CycloneDX / other
- Artifact:
- Hash:

## License review

- [ ] Production dependencies have compatible licenses
- [ ] Required attribution / NOTICE included
- [ ] Source-offer obligations handled if applicable
- [ ] Unknown licenses resolved before release

## Decision

- Release-blocking dependency/security issues:
- Accepted non-blocking risks:
- Follow-up:
