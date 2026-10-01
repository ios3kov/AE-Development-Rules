# Source Registry

Канонический список внешних источников, от которых зависят time-sensitive правила стандарта.

Правило: если источник старше указанного refresh interval, относящееся к нему утверждение нельзя считать актуально подтверждённым до повторной проверки. `starter-kit/scripts/self-test.mjs` проверяет freshness автоматически.

### SRC-ADOBE-EXTENSIBILITY-ROADMAP
- URL: https://blog.developer.adobe.com/en/publish/2026/09/investing-in-the-future-of-creative-cloud-extensibility-uxp-comes-to-our-flagship-applications
- Scope: After Effects UXP public-beta timeline; CEP deprecation/retirement timeline.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-AE-UXP
- URL: https://developer.adobe.com/after-effects/uxp/
- Scope: After Effects UXP host availability and current platform status.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-AE-UXP-API
- URL: https://developer.adobe.com/after-effects/uxp/after-effects-api/
- Scope: After Effects UXP host API members and Min Version metadata.
- Last verified: 2026-10-01
- Refresh interval days: 30

### SRC-ADOBE-UXP-ENTRYPOINTS
- URL: https://developer.adobe.com/uxp/guides/explanation/concepts/entrypoints/
- Scope: UXP lifecycle, async entrypoints and lifecycle timeout constraints.
- Last verified: 2026-10-01
- Refresh interval days: 90

### SRC-ADOBE-UXP-PACKAGING
- URL: https://developer.adobe.com/uxp/guides/how-to/distribution/package/
- Scope: UXP packaging/distribution, CCX and hybrid/native add-on requirements.
- Last verified: 2026-10-01
- Refresh interval days: 90

### SRC-GITHUB-ACTIONS-SECURE-USE
- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Scope: GitHub Actions supply-chain hardening and full-length commit-SHA pinning.
- Last verified: 2026-10-01
- Refresh interval days: 180
