# AE Development Starter Kit

Практический набор для быстрого внедрения требований `DEVELOPMENT_RULES.md` в новый After Effects проект.

Основа — реально использованные паттерны наших AE-проектов: Build Identity, Git state, SHA-256, ExtendScript sanity-check, runtime diagnostics, test records и compatibility evidence. Проектно-специфичная логика удалена.

## Self-test

Перед использованием или release самого стандарта:

```sh
node starter-kit/scripts/self-test.mjs --dry-run
```

Self-test не меняет repository files. Он проверяет:

- local Markdown links и обязательные paths/modules;
- уникальность глобальных §§1–41;
- синхронизацию `rules-manifest.yaml` → applicability map;
- freshness `SOURCES.md`;
- shell/Node/PowerShell syntax;
- executable bits на POSIX;
- опасные destructive patterns;
- legacy terminology;
- immutable SHA pinning GitHub Actions;
- behavioural smoke tests starter-kit scripts в изолированном temp workspace.

CI запускает тот же self-test на Linux, macOS и Windows через `.github/workflows/starter-kit-self-test.yml`.

## Scripts

- `scripts/self-test.mjs` — structural / freshness / supply-chain / behavioural audit стандарта.
- `scripts/generate-applicability.mjs` — генерирует/проверяет applicability map из `rules-manifest.yaml`.
- `tests/behavioral-smoke.mjs` — безопасно запускает core starter-kit scripts на временных fixtures.
- `scripts/collect-dependency-evidence.sh` — hashes dependency manifests/lockfiles и фиксирует доступные audit/SBOM tools на macOS/Linux.
- `scripts/collect-dependency-evidence.ps1` — Windows PowerShell эквивалент.

- `scripts/preflight.sh` — единая macOS/local entry point для быстрых проверок; вызывает project-specific hook при наличии.
- `scripts/preflight.ps1` — Windows PowerShell preflight с тем же назначением.

- `scripts/record-artifact.sh` — commit, dirty state, environment и SHA-256 artifact.
- `scripts/check-extendscript.mjs` — быстрый parser sanity-check JSX/ExtendScript.
- `scripts/scan-adobe-api.sh` — inventory PF/AEGP/SmartFX identifiers для compatibility audit.
- `scripts/macos-binary-audit.sh` — evidence collector для Mach-O architectures, deployment target, linked libraries, symbols и signing; exit 0 не означает compatibility PASS.
- `scripts/macos-bundle-verify.sh` — codesign, stapling, Gatekeeper и quarantine evidence.
- `scripts/windows-binary-audit.ps1` — evidence collector для PE/dependencies/AuthentiCode; report содержит collection status, а exit 0 не означает compatibility PASS.
- `scripts/windows-release-verify.ps1` — SHA-256/AuthentiCode/Zone.Identifier release evidence.
- `scripts/create-owned-test-workspace.sh` — создаёт уникальный fail-closed workspace для AE runtime tests.
- `scripts/verify-native-effect-bundle-macos.sh` — проверяет структуру native effect bundle, AE exports, PiPL/resources, dependencies и подпись.

## Templates

- `templates/REFERENCE_SPECIFICATION_TEMPLATE.md`
- `templates/PRODUCT_DISCOVERY_TEMPLATE.md`
- `templates/STANDARD_ADOPTION.md`
- `templates/DEPENDENCY_SECURITY_AUDIT.md`
- `templates/RELEASE_VERSIONING.md`
- `templates/UPDATE_SECURITY.md`
- `templates/CRASH_DIAGNOSTICS.md`
- `templates/ACCESSIBILITY_CHECKLIST.md`

- `templates/DEBUGGING_RECORD.md`
- `templates/TEST_RECORD.md`
- `templates/COMPATIBILITY_MATRIX.md`
- `templates/API_COMPATIBILITY_AUDIT.md`
- `templates/VALIDATION_CHECKLIST.md`
- `templates/RELEASE_CHECKLIST.md`
- `templates/RETROSPECTIVE.md`
- `templates/USER_GUIDE.md`
- `templates/AE_RUNTIME_TEST_SAFETY.md`
- `templates/BUILD_IDENTITY.md`
- `templates/TEST_CASE.md`
- `templates/QUALITY_METRICS.md`
- `templates/SECURITY_CHECKLIST.md`
- `templates/LOCALIZATION_CHECKLIST.md`
- `templates/DOCS_STRUCTURE.md`
- `templates/CROSS_PLATFORM_PORTING.md`
- `templates/MICRO_HELPER_PROFILE.md`
- `templates/UXP_ENGINEERING.md`
- `templates/HOST_INDEPENDENT_CORE_TESTING.md`

## Внедрение

При AI-assisted работе сначала использовать корневой `AI_ENTRYPOINT.md`: ИИ сам определяет нужный процесс по обычной формулировке пользователя.

1. Если пользователь явно выбрал конкретный внешний продукт/artifact как референс/основу/аналог — пройти `REFERENCE_SPECIFICATION_TEMPLATE.md` по [Reference Audit](../REFERENCE_AUDIT.md).
2. Для нового продукта / крупной функции, когда Smart Entry определил product-level неопределённость, пройти Stage 0 через `PRODUCT_DISCOVERY_TEMPLATE.md`.
3. Скопировать нужные scripts/templates в AE-проект.
4. Подключить релевантные scripts к build/test pipeline или CI.
5. Инженерно зафиксировать выбранный ИИ/разработчиком **Risk Profile**: Light / Standard / Critical.
6. Инженерно зафиксировать **Delivery Gate**: Development / Validation / Release. Не перекладывать этот выбор на нетехнического пользователя.
7. Validation Build: использовать `VALIDATION_CHECKLIST.md`.
8. Release Candidate: пройти полный применимый Release Gate из `profiles/RELEASE.md`.
9. Не повышать Risk Profile только из-за факта release и не включать Release Gate только из-за Critical risk.

## Ограничение

Автоматизация помогает собрать Evidence, но не превращает статический результат в runtime PASS. Статический API/binary audit не равен VERIFIED, а локальная signing-проверка не заменяет реальный quarantined download → install → launch.


## CI example

- `examples/github-actions/ae-preflight.yml` — минимальный GitHub Actions пример, который запускает ту же preflight-команду, что и локальная разработка.

CI не заменяет runtime AE verification, если runner не имеет целевого After Effects/runtime.


## Cross-platform CI

- `examples/github-actions/cross-platform-preflight.yml` — минимальная macOS + Windows preflight matrix.

Обе CI-ветки проверяют только то, что доступно runner. Runtime After Effects verification остаётся отдельным Evidence на каждой платформе.
