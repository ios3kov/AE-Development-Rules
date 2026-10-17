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

### SRC-ADOBE-CEP-DISTRIBUTION
- URL: https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Package%20Distribute%20Install/readme.md
- Scope: CEP ZXP packaging, signing and distribution channels.
- Claim: Adobe CEP packaging uses ZXP signing tooling; OS executable signing is a separate concern.
- Last verified: 2026-10-01
- Refresh interval days: 90

## Verification boundary

### SRC-AGENT-SKILLS-FORMAT
- URL: https://github.com/agentskills/agentskills/blob/69ef37e9424c0a7ea9dd2293b559e43ec8176379/docs/specification.mdx
- Scope: Pinned standard SKILL.md format and progressive disclosure.
- Claim: Standard name/description YAML frontmatter with optional license/compatibility/metadata/allowed-tools; resources load on demand; format does not certify tool availability or safety.
- Last verified: 2026-10-08
- Refresh interval days: 180

### SRC-GITHUB-PROTECTED-VERIFIER
- URL: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Scope: Actual branch protection, independent reviews and app-bound required status checks.
- Claim: Protection must be configured and verified; status source can be restricted to an app, approvals can be invalidated after changes and administrator bypass requires explicit control.
- Last verified: 2026-10-08
- Refresh interval days: 90

### SRC-GITHUB-ENVIRONMENT-REVIEW
- URL: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- Scope: Environment required-reviewer and secret custody capabilities.
- Claim: Environment protection and availability depend on actual settings/plan; naming an environment in workflow YAML does not establish configured controls.
- Last verified: 2026-10-08
- Refresh interval days: 90

Self-test verifies registry structure and declared age, not live URL availability or truth of the claim. Review each claim in its actual source before advancing Last verified. Retain a source-check record with scope/date/result for significant technology or release decisions. Apple, Microsoft and CEP distribution requirements refer to the registered IDs above.

### SRC-REA-STATIC-INTEGRATION
- URL: https://github.com/ios3kov/production-engineering/tree/60845687c4d7c8a4ad01d1fbe6ec9aeb55ac1e31/integrations/rea
- Scope: Optional static producer/planner described in docs/REFERENCE_ENGINEERING_TOOLS.md; package selection and current exclusions, not automatic admission.
- Claim: Exact rea-agents 6.5.0 profile with JS-derived operations quarantined due to missing CommonJS exports; metadata inventory and Ghidra plans require their own host checks. Raw receipts and a smoke PASS are not product-readiness evidence.
- Last verified: 2026-10-17
- Refresh interval days: 30
- Source identity: reviewed upstream main f85a932d71279415dd95cc30083137d1161f83b8; release commit 3b79af28e80785afce9f5998d8f03289402a1847; runtime npm/dependency/image identities recorded separately.
- License: REA core MIT, Copyright (c) 2026 morluto; checked https://github.com/morluto/rea/blob/3b79af28e80785afce9f5998d8f03289402a1847/LICENSE . Third-party component notices remain separate; no upstream code/text is copied into this standard.
- Supporting files: integration README.md, profile.json, adapter.py, smoke.mjs and scripts/tests/test_rea_adapter.py in the pinned Production Engineering source.
- Verification basis: https://github.com/ios3kov/production-engineering/actions/runs/39022130467 — real published CLI on synthetic ZIP/JS/summary only; inspected logs and output hashes, no native/AE/iPhone qualification. The simple JS fixture does not cover the known export-binding failure.
- Known issue: https://github.com/morluto/rea/issues/3551 — source report/reproduction reviewed; no new reproduction claimed here. Quarantine may be lifted only after a corrected exact package and real renamed/shadowed-export regression verification.

### SRC-REA-CORRECTED-RUNTIME
- URL: https://github.com/ios3kov/production-engineering/tree/77bfb0224ce482ccc6df6448d330cc81964d3c93/integrations/rea
- Scope: Optional corrected static runtime for docs/REFERENCE_ENGINEERING_TOOLS.md; supersedes only the blanket JS block for this exact separate payload, not the stock-package quarantine above.
- Claim: Source-built rea-6.5.0-patch3552.1 has a full hash-pinned inventory and five-operation entrypoint. Baseline defect, ten corrected export cases, traces/comparison/summary and archived-runner replay were executed. Ghidra and macOS artifact fixtures were separately tested. These are bounded tool checks, not application/client readiness.
- Last verified: 2026-10-17
- Refresh interval days: 30
- Source identity: release source 3b79af28e80785afce9f5998d8f03289402a1847 plus only src/domain/javascript/javascriptAstFingerprint.ts from dakjdakd/rea@20643d4a47b0562aa794f0a15903630c62912c80, inspected through https://github.com/dakjdakd/rea/blob/20643d4a47b0562aa794f0a15903630c62912c80/src/domain/javascript/javascriptAstFingerprint.ts ; old/new blobs 1dee83fa054b881409f9c321e74830e3b75239a2 / cf3f9aca413a00ebf5a5b8e4a5c94999776506ce. This is not an official upstream release.
- Runtime identity: Linux x64 Node 22.19.0; manifest SHA-256 b3ba3f9f4806d7decaa8df1187b8c519d2ae1f37d29d7c652b60429aa6789c11; tarball and container pins in profile.json.
- License: upstream MIT and third-party notices retained in the runtime; original release license source recorded above. No upstream implementation is copied into this standard.
- Supporting files: integration README.md, profile.json, qualified.py, qualify-bindings.mjs, qualify-native.mjs, three qualification workflows and scripts/tests/test_rea_qualified.py. Actual diff and downloaded reports/hashes reviewed.
- Verification basis: https://github.com/ios3kov/production-engineering/actions/runs/39031000276 (corrected real CLI), https://github.com/ios3kov/production-engineering/actions/runs/39031646765 (archived runner replay), https://github.com/ios3kov/production-engineering/actions/runs/39030583850 (three Ghidra 12.1.4/Java 21 ELF checks and three macOS arm64 app/dylib/DMG checks on unaffected stock 6.5.0 lanes).
- Limits: no AE/iPhone/Windows/client acceptance or automatic installation. Only fresh corrected-runtime Evidence may be used. Remote archive retention ends 2026-11-16; preserve verified bytes locally or requalify a changed build. Older Adobe/platform source dates above are unchanged.
