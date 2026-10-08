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
- conditional Reference Audit trigger / Coverage / parity contract;
- freshness `SOURCES.md`;
- shell/Node/PowerShell syntax;
- executable bits на POSIX;
- опасные destructive patterns;
- legacy terminology;
- immutable SHA pinning GitHub Actions;
- behavioural smoke tests и negative regressions A01–A13 в изолированном temp workspace;
- строгие manifest/project-record schemas, routing scenarios, requirement markers и численные render fixtures.

Self-test не запускает модель ИИ. [Сценарии поведения ИИ](../docs/AI_BEHAVIOR_SCENARIOS.md) проверяются по фактическим действиям конкретной конфигурации отдельно; наличие сценариев и PASS routing helper не доказывают поведение модели.

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
- `scripts/macos-binary-audit.sh` — evidence collector для Mach-O architectures, deployment target, linked libraries и symbols; exit 0 не означает compatibility PASS.
- `scripts/macos-bundle-verify.sh` — artifact identity/manifest и проверка целостности без Apple account/certificate/service prerequisites.
- `scripts/windows-binary-audit.ps1` — evidence collector для PE/dependencies; report содержит collection status, а exit 0 не означает compatibility PASS.
- `scripts/windows-release-verify.ps1` — artifact identity/manifest и проверка целостности без сертификата/сервиса подписания.
- `scripts/create-owned-test-workspace.sh` — создаёт уникальный fail-closed workspace для AE runtime tests.
- `scripts/verify-native-effect-bundle-macos.sh` — проверяет ограниченный structural scope native effect bundle, ожидаемые exports, наличие непустых resources; PiPL semantics, dependency policy и реальная AE load требуют отдельных checks.

## Templates

- `templates/FEATURE_SET_CHANGE.md` — delta/impact/tasks/checks для новых функций в текущем проекте
- `templates/AI_TASK_STATE.md` — встраивается в существующий canonical status для продолжающейся задачи; отдельный файл не обязателен.
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
- `templates/REMOTE_COMPATIBILITY_CHECK.md` — packet и actual run record для AE на другой тестовой машине
- `templates/VALIDATION_CHECKLIST.md`
- `templates/RELEASE_CHECKLIST.md`
- `templates/REPOSITORY_CLEANUP.md` — scoped cleanup plan, preservation и actual execution/verification report
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

Для продолжающейся repository-задачи сохранять решения, границы действий и актуальное состояние в существующей документации по [Smart Entry §2.2](../AI_ENTRYPOINT.md#22-восстановление-и-сохранение-состояния-задачи). При новом/изменённом host API проверять точный контракт по выбранным SDK headers / официальным docs; [API audit template](templates/API_COMPATIBILITY_AUDIT.md) хранит ссылки и ограничения.

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

## Audit hardening tools

Node.js 22+ is required. Copy complete scripts/lib dependencies, including the vendored tokenizer and its license, schemas and REQUIREMENTS.json when using record validation. [Tokenizer provenance](scripts/lib/vendor/README.md) records the pinned source; no package installation is required.

- `record-artifact.mjs` and wrapper: exclusive new Evidence directory, canonical manifest with types/modes/safe internal symlinks. `SHA256.txt` hashes the canonical manifest; final package bytes have a separate file hash in the manifest.
- `verify-artifact.mjs ARTIFACT artifact-record.json`: compare sealed payload; does not prove record authenticity. Never trust an attacker-controlled record as policy.
- `validate-project-record.mjs RECORD.json`: validate the optional [schema](schemas/project-record.schema.json), check Evidence hashes/revision and required results. Dirty candidates are permitted only for Development and block Validation/Release handoff. Record selection/approval remains trusted project policy; successful evaluation does not certify release.
- Optional check `phase` separates Validation pre-handoff prerequisites from `user-validation` and `release-acceptance` questions. No phase retains the previous all-required gate. Required failed user validation blocks the candidate; Release evaluates every required check. At least one required current-gate prerequisite must exist. Upgrade schema and validator together; choosing safe applicability remains project policy.
- [Filled adoption examples](examples/adoption/README.md), [render fixtures](examples/render/README.md), [requirement registry](../REQUIREMENTS.json).
- `compare-render.mjs REFERENCE.json ACTUAL.json MAX_ABS_ERROR [NEW_DIFF.json]`: explicit tolerance, same dimensions/color/alpha/bpc; no implicit conversion.
- `check-extendscript.mjs`: Node syntax subset plus target/targetengine/script/strict directives and literal relative includes. Tokenization distinguishes regex/division, comments, strings and templates so literal directive text is preserved. Unsupported directives, E4X and true ES3 checks need project-specific tooling; no JSX is executed.
- `macos-bundle-verify.sh target NEW_EVIDENCE_DIR`: creates a fresh artifact record/manifest and verifies its bytes/types/modes; no certificate/service access or signature gate. Runs in the product Git checkout. Actual channel download, install and target-host load remain separate checks. Legacy local/public and required/na arguments are rejected; do not reuse old report files.
- `windows-release-verify.ps1 -Target ARTIFACT -EvidenceDirectory NEW_EVIDENCE_DIR`: creates a fresh artifact record and verifies bytes/types/modes from the product Git checkout. No signature/service probes. Legacy `-Output`/`-LocalCheck` arguments reject; retain old tools/records together. Install and host load remain separate checks.
- `preflight`: unstaged/staged checks and optional AE_PREFLIGHT_BASE_REF diff; missing Node/npm with package.json or non-executable present hooks block. A project check list must be selected before running.
- Evidence collectors never reuse output paths. A binary collector exit 2 means incomplete collection; signing errors also remain visible as individual probe outcomes.

Self-test coverage is printed. CI requires POSIX on Linux/macOS and PowerShell on Windows. A skipped platform check is NOT RUN; structural keyword checks only protect document structure. Semantic routing and A01–A13 negative fixtures run separately.

### AI follow-up evaluation

[Controlled fixtures](fixtures/ai/README.md) cover 25 scenarios with 31 starting states, including five held-out AE variants. `prepare-ai-scenario.mjs ID NEW_DIRECTORY` creates an isolated synthetic repository and observer inputs; `inspect-ai-scenario.mjs DIRECTORY` observes file scope and illustrative outcomes. An external runner must enforce permissions and capture actual traces; these tools do not run/certify a model or provide an OS sandbox. Follow-up regressions cover F01/F05/F06/F08/F09/F10/F12. Actual agent behavior remains a separate recorded evaluation.

Use [REQUIREMENT_TRACEABILITY.md](templates/REQUIREMENT_TRACEABILITY.md) as a compact section of the existing product plan or use an equivalent record; a separate template file is optional; do not confuse product requirement IDs with the standard's REQUIREMENTS.json IDs.

### Routing context migration (5.0)

`scripts/lib/applicability.mjs` exports `route(manifest, context)`. Callers classify the user's request before calling it; the helper does not interpret free text, verify exit criteria or authorize actions.

```json
{
  "task": "major-feature",
  "components": ["jsx"],
  "risk": "standard",
  "delivery": "development",
  "reference": "none",
  "product_contract": true,
  "contract_covers_scope": false,
  "changes_product_contract": true
}
```

Here an older confirmed product contract exists, but does not cover the new scope: discovery is required. All three product flags are required booleans; do not infer coverage from file existence. If applicable Stage 0 is already complete and the current approved contract covers the requested new scope, set `contract_covers_scope: true`; no repeat interview is needed. A missing contract cannot cover scope. Audit/research/documentation do not become implementation merely because a product change is discussed. Manifest schema 3 and route output keys remain unchanged.

Bugfix adds DEBUGGING; implementation/research adds API-SOURCES. Light profiles expose the applicable minimum Git, candidate identity, regression and Evidence sections even for JSX; apply their existing scope exceptions proportionally. The helper validates typed context and selects reading, not permissions, applicability approval or Stage 0 completion. Components must be a dense own list of known unique IDs.

CI требует POSIX runtime на Linux/macOS и PowerShell на Windows. В отчёте явно указаны RUN/NOT RUN и platform skips; платформенная проверка не считается выполненной на другом runner. Примеры CI передают базовый commit PR в preflight; локально тот же scope задаётся через `AE_PREFLIGHT_BASE_REF`.

### Deep-audit migration (5.1.0)

См. [полную миграцию](../docs/releases/5.1.0.md) и [errata 5.0.0](../docs/ERRATA.md). Точный исходник и release Evidence доступны в [v5.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.1.0). D01–D10 проверяются отдельной `tests/deep-audit.mjs`; self-test запускает её вместе с прежними suites.

Optional `context.features` добавляет применимые reading overlays, например `['ipc']`, `['ui']`, `['updater']` или `['testing']`. Полный список генерируется в DEVELOPMENT_RULES.md. Поле можно опустить для прежнего caller shape; список должен быть dense/unique/known. Наличие feature не разрешает mutation/publication и не делает audit implementation-задачей. Все §§1–41 представлены в карте; JSX/helper получают runtime минимум, Critical CEP/UXP — code safety. Требования внутри разделов остаются соразмерными scope.

Artifact record/manifest v2 учитывает POSIX `07777`, включая special bits; Windows отмечает Node-emulated mode scope. ACLs/xattrs/ownership/timestamps не аттестуются. Fixture run snapshot v2 учитывает types/modes/empty directories и platform; observer не подтверждает поведение ИИ. Старые snapshots/records новым verifier отвергаются: сохранить их с исходными tools или собрать новую v2 observation, не переписывая исторические Evidence.

Project-record schema остаётся 1: direct sparse/inherited arrays и reordered duplicate Evidence отвергаются. JSON comparisons ограничены depth 64 / 100000 nodes; object key order несущественен, array order сохраняется. UTF-8 collector проверяет исходные bytes строгим decoder, принимает literal U+FFFD/BOM и сохраняет original byte hash.

[Примеры решений ИИ](../docs/AI_DECISION_EXAMPLES.md) и [IPC recovery guidance](../profiles/TOOLS.md#неизвестный-результат-ipc-mutation) не подменяют actual model/AE tests. Даты исходных vendor checks остаются неизменными до реальной перепроверки.

### macOS/Windows distribution policy migration (6.0.0)

[§28](../profiles/RELEASE.md#28-macos-дистрибутив-целостность-установка-и-загрузка) uses exact artifact identity, documented installation and actual host loading. Apple distribution services and Windows certificate/signing-service access are excluded from project prerequisites. See [migration](../docs/releases/6.0.0.md). The native structural checker and Mach-O/PE collectors no longer require certificate/signature probes. [Windows §30](../profiles/RELEASE.md#30-windows-дистрибутив-целостность-установка-и-загрузка) uses the same integrity/install/host-load acceptance. Neither structural nor integrity PASS establishes runtime compatibility.

## Compatibility without installing every AE locally

Follow [Engineering §21](../core/ENGINEERING.md#21-совместимость-и-применимость-технологий): source/API availability and exact artifact audit, scoped baseline SDK build probes and missing-capability adapter tests, then selected real host runs locally or through a [remote packet](templates/REMOTE_COMPATIBILITY_CHECK.md). Keep exact version/build, platform, artifact and loaded identity in the [matrix](templates/COMPATIBILITY_MATRIX.md). Lexical scanner/compilation/mock PASS do not establish runtime compatibility; unknown material coverage stays UNKNOWN. Endpoint tests do not verify all intermediate hosts.

## Safe cleanup after development

Use [Process §6](../core/PROCESS.md#безопасная-уборка-репозитория-после-разработки) and the [cleanup plan/report](templates/REPOSITORY_CLEANUP.md). Review actual state and parallel ownership, preserve ignored/untracked data and verify recovery before any scoped removal. Recheck state at action time; leave unknown/changed items in place. Moving is not inherently safe. Archive managed worktrees through their supported lifecycle. Keep frozen/released artifacts and historical Evidence unchanged; backup retention/purge needs its own permission. A plan or clean Git status does not establish that cleanup was executed or correct.

## End-to-end task control and new feature sets

For significant work, [Process §11](../core/PROCESS.md#контроль-прохождения-задачи-и-финальная-сверка) requires applicable work/check mapping, block updates and final reconciliation against actual scope/candidate/Evidence. Use the existing task checkpoint and traceability, without duplicate documents. [Smart Entry §2.4](../AI_ENTRYPOINT.md#24-новый-набор-функций-в-текущей-разработке) and [feature delta template](templates/FEATURE_SET_CHANGE.md) preserve existing commitments while adding functions. Reuse covered Stage 0 decisions; investigate only uncovered scope. Neither a checklist nor static tests certify model behavior or AE runtime.

## Conditional reference evidence obligations (experimental)

For a concrete reference/parity target, see [Reference Evidence Obligations](../docs/REFERENCE_EVIDENCE_OBLIGATIONS_PROPOSAL.md). Validate a project-owned JSON ledger with:

```sh
python3 starter-kit/scripts/check_reference_obligations.py /path/to/reference-ledger.json --evidence-root /path/to/observations
python3 -m unittest discover -s starter-kit/tests -p test_reference_obligations.py -v
```

The CLI exits nonzero on missing required cases, stale verifier revision, inadequate execution authority, duplicate obligation IDs or unresolved contradictions. A non-triggered ledger can be marked `reference_triggered: false`. This is an additive experimental validator, **not yet wired to the canonical release gate or the project's protected trust baseline**. Passing a self-authored ledger alone does not establish evidence authenticity or product parity. No production or publication action is implied.
