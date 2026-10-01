# Changelog

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
