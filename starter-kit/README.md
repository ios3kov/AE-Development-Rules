# AE Development Starter Kit

Практический набор для быстрого внедрения требований `DEVELOPMENT_RULES.md` в новый After Effects проект.

Основа — реально использованные паттерны наших AE-проектов: Build Identity, Git state, SHA-256, ExtendScript sanity-check, runtime diagnostics, test records и compatibility evidence. Проектно-специфичная логика удалена.

## Scripts

- `scripts/preflight.sh` — единая локальная entry point для быстрых проверок; вызывает project-specific hook при наличии.

- `scripts/record-artifact.sh` — commit, dirty state, environment и SHA-256 artifact.
- `scripts/check-extendscript.mjs` — быстрый parser sanity-check JSX/ExtendScript.
- `scripts/scan-adobe-api.sh` — inventory PF/AEGP/SmartFX identifiers для compatibility audit.
- `scripts/macos-binary-audit.sh` — Mach-O architectures, deployment target, linked libraries, symbols и signing.
- `scripts/macos-bundle-verify.sh` — codesign, stapling, Gatekeeper и quarantine evidence.\n- `scripts/create-owned-test-workspace.sh` — создаёт уникальный fail-closed workspace для AE runtime tests.\n- `scripts/verify-native-effect-bundle-macos.sh` — проверяет структуру native effect bundle, AE exports, PiPL/resources, dependencies и подпись.

## Templates

- `templates/TEST_RECORD.md`
- `templates/COMPATIBILITY_MATRIX.md`
- `templates/API_COMPATIBILITY_AUDIT.md`
- `templates/RELEASE_CHECKLIST.md`
- `templates/RETROSPECTIVE.md`
- `templates/USER_GUIDE.md`\n- `templates/AE_RUNTIME_TEST_SAFETY.md`\n- `templates/BUILD_IDENTITY.md`
- `templates/TEST_CASE.md`
- `templates/QUALITY_METRICS.md`
- `templates/SECURITY_CHECKLIST.md`
- `templates/LOCALIZATION_CHECKLIST.md`
- `templates/DOCS_STRUCTURE.md`

## Внедрение

1. Скопировать нужные scripts/templates в AE-проект.
2. Подключить релевантные scripts к build/test pipeline или CI.
3. Light: запускать только проверки затронутого scope.
4. Standard: добавить runtime AE evidence.
5. Release / Critical: пройти полный применимый gate из `DEVELOPMENT_RULES.md`.

## Ограничение

Автоматизация помогает собрать Evidence, но не превращает статический результат в runtime PASS. Статический API/binary audit не равен VERIFIED, а локальная signing-проверка не заменяет реальный quarantined download → install → launch.


## CI example

- `examples/github-actions/ae-preflight.yml` — минимальный GitHub Actions пример, который запускает ту же preflight-команду, что и локальная разработка.

CI не заменяет runtime AE verification, если runner не имеет целевого After Effects/runtime.
