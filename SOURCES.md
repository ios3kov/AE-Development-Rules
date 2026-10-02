# Source Registry

Канонический список внешних источников, от которых зависят time-sensitive правила стандарта.

Правило: если источник старше указанного refresh interval, относящееся к нему утверждение нельзя считать актуально подтверждённым до повторной проверки. `starter-kit/scripts/self-test.mjs` проверяет freshness автоматически.

### SRC-ADOBE-EXTENSIBILITY-ROADMAP
- URL: https://blog.developer.adobe.com/en/publish/2026/09/investing-in-the-future-of-creative-cloud-extensibility-uxp-comes-to-our-flagship-applications
- Scope: After Effects UXP public-beta timeline; CEP deprecation/retirement timeline.
- Claim: AE UXP public beta announced by November 2026; CEP removed from new flagship versions starting December 2029; ExtendScript unaffected.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-AE-UXP
- URL: https://developer.adobe.com/after-effects/uxp/
- Scope: After Effects UXP host availability and current platform status.
- Claim: AE-specific UXP documentation exists; target-host availability must be separately established.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-AE-UXP-API
- URL: https://developer.adobe.com/after-effects/uxp/after-effects-api/
- Scope: After Effects UXP host API members and Min Version metadata.
- Claim: Host member Min Version metadata contributes to compatibility analysis.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-UXP-ENTRYPOINTS
- URL: https://developer.adobe.com/uxp/guides/explanation/concepts/entrypoints/
- Scope: UXP lifecycle, async entrypoints and lifecycle timeout constraints.
- Claim: Promise support and lifecycle timeout are bounded; hide/destroy differ by host.
- Last verified: 2026-10-01
- Refresh interval days: 90

### SRC-ADOBE-UXP-PACKAGING
- URL: https://developer.adobe.com/uxp/guides/how-to/distribution/package/
- Scope: UXP supported packaging flow, CCX format, plugin IDs, hybrid layout and channel-specific installation acceptance.
- Claim: Pure CCX has no package-level signature/timestamp requirement; UDT creates packages, IDs distinguish channels, and hybrid native binaries need the target platform/architecture layout. Vendor channel acceptance is distinct from local host loading.
- Last verified: 2026-10-02
- Refresh interval days: 90

### SRC-GITHUB-ACTIONS-SECURE-USE
- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Scope: GitHub Actions supply-chain hardening and full-length commit-SHA pinning.
- Claim: Third-party Actions should be pinned to full-length immutable SHA.
- Last verified: 2026-10-01
- Refresh interval days: 180

### SRC-MICROSOFT-TIMESTAMP
- URL: https://learn.microsoft.com/en-us/windows/win32/seccrypto/time-stamping-authenticode-signatures
- Scope: Authenticode timestamp and certificate expiry.
- Claim: Timestamping preserves signature verifiability after signing-certificate expiry; signature validity alone does not replace a required timestamp check.
- Last verified: 2026-10-01
- Refresh interval days: 90

### SRC-ADOBE-CEP-DISTRIBUTION
- URL: https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Package%20Distribute%20Install/readme.md
- Scope: CEP ZXP packaging, signing and distribution channels.
- Claim: Adobe CEP packaging uses ZXP signing tooling; OS executable signing is a separate concern.
- Last verified: 2026-10-01
- Refresh interval days: 90

## Verification boundary

Self-test verifies registry structure and declared age, not live URL availability or truth of the claim. Review each claim in its actual source before advancing Last verified. Retain a source-check record with scope/date/result for significant technology or release decisions. Apple, Microsoft and CEP distribution requirements refer to the registered IDs above.
