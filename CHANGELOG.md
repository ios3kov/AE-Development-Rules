# Changelog

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
