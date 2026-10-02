# Changelog

## 6.1.0 — 2026-10-02

- Adds REL-DOC-001: applicable user instructions must be ready before publication; the final release reply and subsequent “what next?” explicitly direct the user to the version-matching guide and identify concrete additional documentation gaps. Smart Entry, Workflow and the release checklist share this contract. No published 6.0.0 artifact/tag is changed.

## 6.0.0 — 2026-10-02

Changes the macOS/Windows distribution policy at the user's request: certificate/signing-service access is no longer a release prerequisite. MAC-001/WIN-001 now require artifact identity, documented installation and actual host loading. This is a major release: mandatory gate meaning and a public checker interface change; adopted 5.x records/tools retain their original semantics. [Migration and verification](docs/releases/6.0.0.md).

- Removes macOS/Windows certificate/remote-service gates from canonical rules, UXP/porting guidance and validation/release templates. Unsigned or locally ad-hoc-signed artifacts can qualify after actual install/runtime checks. No claim of warning-free installation or universal external-channel acceptance.
- Replaces macos-bundle-verify.sh with artifact record/verification using a fresh evidence directory. Legacy policy arguments fail with migration guidance; integrity PASS is separate from install/host-load status.
- Native structural and Mach-O/PE collectors no longer require signature probes. Required structural/architecture/dependency collection failures still fail. Windows release wrapper also records/verifies artifact integrity; its legacy Output/LocalCheck interface rejects with migration guidance.
- Preserves historical release/audit records; they describe their original baselines, not current macOS/Windows policy. The obsolete Apple and Microsoft timestamp source entries are removed; the UXP packaging source was actually rechecked on 2026-10-02.

## 5.1.0 — 2026-10-02

Minor release. Repairs D01–D10 and implements optional I01–I04 from the five-pass 5.0.0 deep audit. No new universal MUST/gate contract is introduced. Existing project baselines remain frozen until explicit adoption. [Remediation](docs/DEEP_AUDIT_REMEDIATION_5_1.md), [errata](docs/ERRATA.md), [migration](docs/releases/5.1.0.md).

- Reading map now covers all canonical §§1–41: component/runtime and Critical code-safety minima, scoped state/completion/automation guidance and optional typed feature overlays. Undefined selected IDs, deleted/misbound task overlays and linked canonical sources/ancestors reject.
- Fixture snapshot v2 records types, modes and empty directories; artifact/manifest v2 includes POSIX special mode bits. Windows mode scope remains Node-emulated. Legacy records are preserved with their original tools; new verifiers reject them rather than silently asserting stronger Evidence.
- Direct record validation rejects sparse/inherited array items. JSON uniqueness ignores object member order while retaining array order, with bounded comparisons.
- Whitespace-only stapling N/A explanations reject. API inventory uses strict UTF-8 decoding and original byte hashes, accepting literal U+FFFD/BOM. Version checks compare one authoritative full README field and current CHANGELOG with normal SemVer VERSION.
- Unknown IPC outcome guidance recommends scoped reconciliation/deduplication without inferring rollback from timeout. Versioned errata preserve affected baseline, temporary controls and candidate availability.
- Adds five AE behavior scenarios and five held-out variants: 25 scenarios / 31 starting states. Fixture preparation and illustrative pure/mock acceptance checks do not run/certify a model or AE. Adds three source-linked decision examples.
- New focused regressions preserve the existing routing/product/delivery contracts. Local checks do not imply Windows/AE/model/remote CI execution or release readiness.

## 5.0.0 — 2026-10-02

Major AI/process release. Adds mandatory trust, resume-state and scoped-autonomy contracts for AI-assisted work, plus target-source verification when adding/changing host API use. Includes the unreleased 4.1.0 audit remediation below; no separate 4.1.0 release is implied. 5.0.0 is the first GitHub Release/tag for this repository; earlier version sections record the standard's development history. The previous 4.0.0 project baseline is retained until consciously migrated. See [release notes](docs/releases/5.0.0.md).

- Smart Entry defines user-decision precedence, adopted-rule boundaries and untrusted reference/tool content. External instructions cannot grant scope or approval.
- Continuing repository tasks restore actual Git/environment state, confirmed decisions, permission sources, Evidence and the next step; update the existing canonical checkpoint rather than duplicate documents.
- Autonomous continuation retains scoped authorization, distinguishes edit/push/merge/publication rights and continues independent work around a blocker.
- Reference BLOCKED no longer reads as permission to start dependent Technical Design.
- Routing distinguishes contract existence, current-scope coverage and product-level changes, even when a change is called a bugfix. Already confirmed scope does not require a repeated interview.
- Newly used/changed host APIs need exact target header/doc/signature/revision applicability records; unknown API contracts cannot be fabricated.
- Adds 20 agent-behavior scenarios with 21 controlled fixtures (two Validation variants), preparation/file-inspection tools and a reusable task-state template. Automated helper tests and actual model evaluation remain separate Evidence.
- Follow-up F01–F12: bugfix/API and minimal Light reading coverage; no-progress handling; blocking-assumption exit criteria; compact product traceability; pre-handoff/user-question/final-acceptance distinction; PKG/payload checklist alignment; adopted-baseline instructions. Reject reversed/unbounded section ranges, sparse components/pixels, nonfinite derived render metrics and blank N/A reasons.
- Release packaging review: fixture preparation requires the standard's own Git checkout and rejects a source archive nested in another repository before creating a run, preserving accurate source identity.

### Migration to 5.0

Adopt the new standard version and exact commit consciously; do not upgrade a frozen project baseline automatically.

For AI-assisted continuing tasks, use an existing canonical status/spec record to retain the goal, confirmed decisions, actual authorization sources, current Git/artifact/Evidence identity, scoped blockers and next step. Recheck current state on resume; do not treat the record itself as user consent. Review the precedence and autonomy contracts in AI_ENTRYPOINT.md.

Routing callers must now supply all three boolean fields: `product_contract`, `contract_covers_scope`, `changes_product_contract`. The former boolean alone is rejected. Determine scope coverage from the current confirmed requirements and applicable Stage 0 exit criteria; never migrate by blindly assigning `contract_covers_scope: true`. A missing contract cannot cover scope. Output keys and manifest schema 3 are unchanged.

For new/changed host API use, record the selected SDK/host sources and precise contract in the project's existing API inventory/research record. Existing unchanged calls do not require repeated inventory work without a new reason.

Before repeating a failed approach, record a meaningful changed condition/new Evidence or a justified bounded transient retry. Recording a critical assumption alone cannot close a design dependency. Keep product requirement/task/acceptance/check links in existing project records where useful; the traceability template is optional.

Project-record schema 1 adds optional check `phase`: `pre-handoff`, `user-validation`, `release-acceptance`. Upgrade the complete schema and validator together; older strict validators reject the new field. Records without phase retain the previous all-required-checks gate. Validation can defer only explicitly classified user/final questions; required pre-handoff prerequisites and dirty-source restrictions remain. Record selection, safety applicability and actual approval are trusted project policy, not certified by the helper. Release still evaluates all required checks. The output adds `deferred_checks`.

Light route selection now exposes applicable minimal Git/identity/regression/Evidence sections; their scope remains proportional, not full product/AE certification for every edit. Bugfix adds DEBUGGING and implementation/research adds API-SOURCES. Route keys and manifest schema 3 remain unchanged. Invalid direct-library arrays/ranges and nonfinite derived render metrics now throw; valid very large finite samples use stable RMSE arithmetic.

AI behavior runs are configuration-specific and separate from starter-kit self-test. No live model or AE runtime result is claimed by the scenario catalogue. See [original update](docs/AI_PROTOCOL_UPDATE.md), [follow-up remediation](docs/AI_PROTOCOL_REMEDIATION.md) and [fixture procedure](starter-kit/fixtures/ai/README.md).

## 4.1.0 — Unreleased work incorporated into 5.0.0

Audit remediation A01–A13; enforcement of existing safety/Evidence requirements and corrections to contradictory milestone/micro-helper routing. No new universal MUST is introduced. Previously compliant projects keep their requirements; tooling integration needs the migration below.

- Exclusive immutable artifact records bind types, relative paths, modes, safe internal symlinks and payload hashes; verifier detects changes.
- Missing tools/input and incomplete probes fail closed; API collector preserves explicit inventory coverage.
- Dependency report history survives identical clock stamps; zsh hashing preserves PATH and traversal errors propagate.
- Native helper states structural scope and refuses empty resources; PiPL semantics and AE load remain separate.
- Explicit macOS stapling/applicability and Windows timestamp gates.
- Strict manifest schema 3, routing scenario tests and stable requirement IDs.
- Optional project-record validator, filled adoption examples and numeric RGBA fixtures/comparator.
- Evidence lifecycle, deviation ownership, source claim registry and contribution/release governance.
- CI declares required platform subsets and disables retained checkout credentials.
- Follow-up audit R01–R06: dirty Validation handoff blocks; macOS signatures use format-specific verification and DMG assessment context; JSX preprocessing preserves regex/comment/literal boundaries; API inventory includes uppercase extensions; strict schemas reject prototype-named unknown keys; internal milestones select Level 2 by risk and acceptance criteria.

### Tooling migration

Copy scripts with their lib directory. Node 22+ is required. `rules-manifest.yaml` uses JSON notation (valid YAML 1.2); schema 3 replaces free-form rule lists with structured inheritance/rules. Existing artifact/binary evidence output directories/files cannot be reused. Dependency reports may share a history directory, with fresh UUID names and exclusive files. Binary collectors return 2 for incomplete collection. Configure macOS local/public and required/na stapling policy explicitly; a documented N/A requires AE_STAPLING_NA_REASON. Windows timestamp is required by default; LocalCheck intentionally excludes that public-release gate. Never upgrade a baseline in a frozen release cycle automatically.

The JSX checker now includes pinned js-tokens 10.0.0 under scripts/lib/vendor, with its MIT license and provenance. Copy that complete directory when upgrading. Dirty Validation records now return BLOCKED/nonzero, enforcing the existing internal-only dirty-build rule. PKG signature Evidence is named pkgutil rather than codesign. That follow-up introduced no mandatory process requirement or record schema version changes; its unreleased 4.1.0 work is retained in 5.0.0.

## 4.0.0 — 2026-10-01

Breaking process release: для задач, где пользователь явно выбирает конкретный внешний продукт/artifact как **референс, основу, аналог или parity target**, введён обязательный conditional **Reference Audit** до Technical Design соответствующего scope.

- Добавлен [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) как нормативный §R0.
- Trigger строго ограничен explicit external reference: присланный reference artifact, ссылка на конкретный продукт, named product/analogue или явно обозначенный UI/behavior/preset/render reference.
- Общие запросы вида «хочу glow» и случайные упоминания продукта Reference Audit автоматически не включают.
- Для whole-product analogue требуется систематическая декомпозиция UI/controls, functionality, presets, state/persistence, animation/keyframes, render/output, alpha/color/bit depth, edge cases, performance и packaging/integration.
- Введён отдельный **Reference Claim Status**: PROVEN / OBSERVED / INFERRED / UNKNOWN. Он не заменяет Test Status, Compatibility Status или Evidence Confidence.
- Недоказанная внутренняя реализация запрещена как факт: hypotheses остаются INFERRED/UNKNOWN до достаточного Evidence.
- Добавлен обязательный Reference Coverage Map: COMPLETE / PARTIAL / BLOCKED / N/A по ключевым областям.
- Добавлена фиксация reference identity: version/build/platform/host/source/file/hash/date и boundary разрешённого анализа.
- Разрешён максимально глубокий безопасный/допустимый анализ, включая black-box runtime и static artifact inspection; decompilation/disassembly используется только при наличии соответствующих прав/разрешения и без обхода DRM/licensing/activation/access controls.
- Для нескольких референсов требуется отдельная identity/Evidence boundary и явное разрешение конфликтов между products.
- Добавлен [REFERENCE_SPECIFICATION_TEMPLATE.md](starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md) с UI inventory, parameter sweeps, preset matrix, state/render/performance contracts, claim ledger, Coverage Map и parity acceptance tests.
- После реализации reference-driven scope MUST проходить parity testing на одинаковых/эквивалентных fixtures для reference и нашего implementation.
- Reference Audit встроен в AI Smart Entry, Product Discovery, Workflow, Process Core, DEVELOPMENT_RULES index, starter-kit и STANDARD_ADOPTION.
- `rules-manifest.yaml` обновлён до schema 2 и содержит conditional Rule Group `REFERENCE-AUDIT` с trigger `explicit_external_reference`.
- Self-test блокирует release стандарта при потере trigger semantics, Reference Claim Status, Coverage Map, parity contract или Reference Specification template.

#Dependency collectors also preserve history on identical clock stamps; the POSIX collector no longer changes PATH via zsh’s special path variable and propagates directory traversal errors.

## Migration from 3.x

Проект, переходящий на 4.0, должен:

1. определить, использует ли текущий product scope конкретный внешний продукт/artifact как заявленный reference/analogue/parity target;
2. если нет — зафиксировать Reference Audit как N/A и продолжить существующий процесс;
3. если да — зафиксировать reference identity и scope, создать Reference Specification и Coverage Map;
4. отделить OBSERVED/PROVEN факты от INFERRED/UNKNOWN внутренних выводов;
5. до новых parity claims / значимого reference-driven Technical Design определить acceptance tests и закрыть critical gaps либо явно зафиксировать BLOCKED;
6. сохранить Reference Audit status/baseline в project STANDARD_ADOPTION record.

## 3.1.1 — 2026-10-01

Maintenance / optimization cleanup без изменения process contract.

- Исправлен legacy-термин `API-COMPATIBLE` в `scan-adobe-api.sh`; актуальный static status — `STATIC-COMPATIBLE`.
- Self-test теперь проверяет legacy terminology не только в Markdown, но и в scripts/manifests.
- macOS/Windows binary audit helpers явно разделяют **evidence collection** и **audit verdict**: exit code 0 больше нельзя ошибочно трактовать как Compatibility PASS/VERIFIED.
- Windows binary audit отмечает неполный сбор PE/dependency evidence как `collection_status=PARTIAL`.
- AI Smart Entry сокращён без изменения маршрутизации и обязательной семантики.
- Удалён двойной section separator из `DEVELOPMENT_RULES.md`.
- Full Linux/macOS/Windows self-test matrix теперь запускается на PR, `main` и вручную; промежуточные branch pushes не создают лишние полные runs.
- Добавлен `concurrency / cancel-in-progress`, чтобы новый commit отменял устаревший run того же PR/ref.
- Self-test защищает audit semantics и оптимизированную CI policy от случайной регрессии.

## 3.1.0 — 2026-10-01

Backward-compatible usability update: добавлен **AI Smart Entry** — пользователь больше не должен знать или выбирать внутренние инженерные режимы стандарта.

- Добавлен [AI_ENTRYPOINT.md](AI_ENTRYPOINT.md) как основной вход для AI-assisted работы.
- Пользователь может формулировать задачу обычным языком; ИИ сам определяет Stage 0, Risk Profile, Delivery Gate и применимые Rule Groups.
- Запрещено перекладывать на пользователя выбор внутренних терминов, если намерение можно определить из контекста.
- Перед вопросами ИИ должен использовать уже известный conversation/repository/product context и не спрашивать повторно известное.
- Добавлена внутренняя маршрутизация типовых запросов: новый продукт, крупная функция, bug/regression, небольшое улучшение, validation, release и research.
- Уточнения задаются только когда ответ materially меняет product/scope/UX/architecture/compatibility/security/distribution/acceptance criteria.
- Рекомендуется задавать 1–3 связанных человеческих вопроса за один заход вместо большой технической анкеты.
- Добавлены human-language examples вместо вопросов вроде «какой Delivery Gate выбрать?».
- После маршрутизации ИИ должен читать только минимальный применимый набор canonical rules, а не весь repository.
- WORKFLOW, Product Discovery, Process Core, DEVELOPMENT_RULES и starter-kit обновлены так, чтобы внутренние режимы оставались внутренней инженерной классификацией.
- Self-test блокирует release стандарта, если Smart Entry contract исчезнет или потеряет ключевые правила.

## 3.0.0 — 2026-10-01

Breaking process release: для нового продукта, крупной новой функции или существенного изменения product direction введён обязательный **Stage 0 — Product Discovery и Product Vision** до Product Spec / Technical Design / Production Plan.

- Добавлен [PRODUCT_DISCOVERY.md](PRODUCT_DISCOVERY.md) как нормативный §0.
- Введён профессиональный discovery flow: known context → focused interview → Product Vision → Product Scope → Core User Flows → Success Criteria.
- Требования разделяются на **Confirmed Requirement / Derived Requirement / Assumption / Open Question / Idea / Non-goal**.
- Assumption больше нельзя незаметно превращать в requirement.
- Введены explicit Core / Important / Later / Out of scope и обязательные non-goals.
- Определены Stage 0 exit criteria: пользователь, проблема, desired outcome, core flow, scope, constraints, critical assumptions и testable Success Criteria.
- Для существующего продукта Stage 0 не повторяется для каждого bugfix/refactor, если уже существует актуальный product contract и работа его не меняет.
- Добавлен reusable [PRODUCT_DISCOVERY_TEMPLATE.md](starter-kit/templates/PRODUCT_DISCOVERY_TEMPLATE.md) с итеративным interview, requirement ledger, Product Vision, flows и exit check.
- Stage 0 подключён к Process Core, WORKFLOW, DEVELOPMENT_RULES index, README, starter-kit и STANDARD_ADOPTION baseline.
- Добавлен Rule Group `PRODUCT-DISCOVERY` в `rules-manifest.yaml`.
- Self-test теперь блокирует release стандарта, если Stage 0 contract/template исчезли или потеряли ключевые разделы.

### Migration from 2.x

Проект, переходящий на 3.0, должен определить:

1. существует ли подтверждённый Product Vision / requirements contract;
2. если нет и проект/крупная функция ещё проектируются — пройти Stage 0;
3. сохранить ссылку на Product Discovery / Product Vision в project baseline;
4. не требовать повторного discovery для локальных изменений, которые не меняют product contract.

## 2.1.0 — 2026-10-01

Backward-compatible workflow/debugging update.

- Добавлен **Controlled initiative**: сохранять запрошенный scope, но кратко сообщать о критической архитектурной/security/data-loss проблеме и предлагать альтернативу без молчаливого rewrite.
- Добавлено правило представления ручных изменений: при реальном доступе редактировать repository и показывать настоящий Git diff; при ручной передаче пользователю предпочитать `File → Find → Replace → Verify` вместо псевдо-diff и нестабильных line numbers.
- Добавлен evidence-driven **Debugging Protocol** в Engineering Core: symptom → identity → reproduction → Evidence → failure layer → facts/hypotheses → one-variable diagnostic experiment → minimal fix → regression → cleanup.
- Добавлены runtime-specific debugging рекомендации для ExtendScript/ScriptUI, CEP, UXP и Helper/IPC.
- Добавлен reusable `starter-kit/templates/DEBUGGING_RECORD.md`.
- Добавлен Rule Group `DEBUGGING` для §16 в `rules-manifest.yaml`.
- Self-test теперь гарантирует наличие Controlled initiative, manual patch guidance и Debugging Protocol.
- `TEST/manifest/source/supply-chain/behavioural` checks остаются без изменения обязательной gate semantics.

## 2.0.0 — 2026-10-01

Breaking process release: Risk Profile и Delivery Gate теперь независимы.

- Разделены оси **Risk Profile: Light / Standard / Critical** и **Delivery Gate: Development / Validation / Release**.
- Удалено смешанное понятие `Release / Critical`: Critical больше не означает release, а Release Gate применяется независимо от риска изменения.
- `DEVELOPMENT_RULES.md` превращён из большого монолита в компактный нормативный индекс; canonical rules разнесены по `core/` и `profiles/`.
- Добавлены стабильные Rule Group IDs и machine-readable `rules-manifest.yaml`; applicability map генерируется и проверяется автоматически.
- Добавлен отдельный **Technology Lifecycle Status**: PREVIEW / BETA / GA / DEPRECATED / RETIRED.
- Зафиксирован текущий Adobe transition context: AE UXP — PREVIEW до фактического public beta; CEP — DEPRECATED для новой долгоживущей архитектуры с migration/exit plan.
- Добавлен `SOURCES.md` с last-verified date и refresh interval; stale time-sensitive source блокирует self-test.
- Добавлен нормативный словарь MUST / MUST NOT / SHOULD / MAY / APPLICABLE WHEN.
- Regression Level 1 отвязан от каждого commit и привязан к integration checkpoint / merge-ready commit.
- Starter-kit self-test теперь проверяет структуру §§1–41, manifest sync, source freshness, links, syntax, executable bits, terminology, SHA-pinning Actions и запускает behavioural smoke tests.
- Добавлены behavioural fixtures для ExtendScript check, API scan, artifact evidence, owned workspace, preflight, dependency evidence и fail-closed negative paths platform tools.
- GitHub Actions и примеры pinned на immutable full commit SHA и обновлены до v6.
- Добавлена MIT license.
- Уточнён versioning contract стандарта: изменение обязательной process/gate semantics, делающее прежний compliant project non-compliant, требует major version.

### Migration from 1.2

Проект, переходящий на 2.0, должен:

1. заменить старый `Release-Critical` выбор на два независимых значения: Risk Profile + Delivery Gate;
2. обновить ссылки на canonical modules / Rule Group IDs;
3. для UXP/CEP зафиксировать Technology Lifecycle decision и актуальный source baseline;
4. обновить project templates из starter-kit при следующем подходящем checkpoint.

## 1.2.0 — 2026-10-01

- Разделены **Validation Build / Validation Gate** и **Release Candidate / Release Gate**: пользовательская проверка больше не требует автоматически полного release ceremony.
- Добавлена быстрая матрица применимости: Native / JSX / CEP / UXP / Helper × Light / Standard / Release-Critical.
- Унифицированы независимые namespace статусов: **Test Status**, **Compatibility Status**, **Evidence Confidence**.
- macOS/Windows signing gates привязаны к фактическому типу distributable; source-only artifacts не получают искусственных OS signing требований.
- Рабочий ритм, статусы этапов и правила общения вынесены в отдельный [WORKFLOW.md](WORKFLOW.md).
- UXP rules актуализированы по текущей документации Adobe: Min Version, async/lifecycle ограничения, pure CCX vs hybrid UXP packaging и native addon signing.
- Добавлен отдельный Validation Build checklist; обновлены release, compatibility, retrospective и UXP templates.
- Добавлен read-only starter-kit self-test: paths, local links, syntax, executable bits, status taxonomy и safety checks.
- Добавлен cross-platform GitHub Actions self-test для Linux / macOS / Windows.
- Проведены deduplication, reference audit и consistency cleanup основного стандарта и starter-kit.


## 1.1.0 — 2026-10-01

- Добавлен явный минимальный профиль для micro-helper scripts.
- Добавлены UXP-specific engineering rules: host API/Min Version, async state, manifest permissions, storage/network, lifecycle и runtime tests.
- Добавлен host-independent core / testing pyramid для ExtendScript, CEP/UXP и native plugins.
- Добавлены reusable templates для UXP, testing pyramid и micro-helper profile.
- Исправлено форматирование starter-kit README.


## 1.0.1 — 2026-10-01

- Добавлены прямые ссылки из стандарта на dependency-evidence scripts.
- Раздел versioning стандарта напрямую связывает VERSION и CHANGELOG.
- Семантика обязательных требований v1.0.0 не изменена.


## 1.0.0 — 2026-10-01

Первый стабильный baseline общего стандарта разработки Adobe After Effects продуктов.

Включает:

- risk-based Light / Standard / Release-Critical процесс;
- Git / Build Identity / SHA-256 / Evidence;
- controlled testing и Regression Level 1/2;
- native effects, scripts, ScriptUI, CEP/UXP и helpers;
- MFR / SmartFX / aerender / bit depth / color management;
- performance / profiling;
- static API compatibility audit и runtime compatibility matrix;
- macOS и Windows release gates;
- cross-platform porting policy;
- user protection / untrusted input;
- Unicode / localization;
- documentation structure и user guide;
- test-case methodology;
- quality metrics;
- dependency/license/vulnerability/SBOM requirements;
- product versioning / changelog / migration contract;
- update security;
- crash diagnostics / symbols;
- accessibility;
- reusable starter-kit, preflight и CI examples.
