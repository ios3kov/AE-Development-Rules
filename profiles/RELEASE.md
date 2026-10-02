# Release / Distribution Profile

Validation/Release gates и platform distribution requirements. Release — Delivery Gate, а не Risk Profile.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 26. Validation Gate и Release Gate
<!-- REQ: GATE-001 -->

Передача тестового artifact пользователю для ограниченной проверки и финальный release — разные события.

### Validation Gate

До передачи определить три отдельных scope проверок: **pre-handoff** (обязательные внутренние/safety prerequisites), **user-validation** (конкретный вопрос после передачи в уникальной пользовательской среде) и **release-acceptance** (финальная приёмка релиза).

Отсутствие результата именно user-validation не блокирует передачу безопасного идентифицированного Validation Build, когда pre-handoff prerequisites выполнены. Недоступная обязательная pre-handoff проверка, известный обязательный FAIL проверяемого сценария или критический safety риск блокируют эту передачу. Не переносить внутреннюю доступную проверку в user-validation ради обхода gate. Release требует полный применимый набор независимо от фаз.

Validation Build можно передать пользователю, когда:

- определён конкретный вопрос, который должен подтвердить пользователь;
- artifact однозначно идентифицирован commit / Build ID / hash или эквивалентом;
- выполнены определённые pre-handoff prerequisites и релевантные автоматические/внутренние проверки, доступные разработчику; недоступный обязательный prerequisite остаётся BLOCKED;
- основной проверяемый сценарий не имеет известного обязательного Test: FAIL;
- нет известных критических рисков потери данных, безопасности или повреждения проекта;
- пользователь получает краткую инструкцию проверки и известные ограничения;
- artifact явно обозначен как validation / test build, если он ещё не прошёл Release Gate.

Для обычного Validation Build не требуются автоматически:

- полный Regression Level 2;
- финальный public installer/package;
- проверка реального публичного download channel;
- полный compatibility sweep;
- deep profiling;
- release documentation в финальном виде.

Эти проверки становятся обязательными, если входят в предмет validation или затронутый риск.

Пользовательский результат фиксировать как Evidence. Если результат существует только в пользовательской среде, использовать `Evidence: USER-REPORTED`. Это не превращает непройденные внутренние проверки в Test: PASS.

### Release Gate

Перед финальной публикацией / передачей Release Candidate выполнить полный применимый цикл.

#### До фиксации Release Candidate

Выполнить необходимое:

- code audit;
- debugging;
- refactoring;
- profiling;
- optimization при доказанном bottleneck;
- обновление tests и documentation.

После этого зафиксировать изменения в Git.

#### Создание Release Candidate

- Проверить clean Git state.
- Выполнить clean build / clean package.
- Выполнить применимые signing / post-processing steps.
- Зафиксировать Build ID.
- Рассчитать финальный SHA-256.
- Сохранить artifact и manifest.

#### Проверка Release Candidate

- Подготовить безопасное контролируемое окружение.
- Исключить конфликт старых активных версий.
- Выполнить чистую установку, где она применима.
- Подтвердить runtime Build ID.
- Выполнить smoke / integration tests.
- Пройти Regression Level 2.
- Проверить логи и ошибки.
- Выполнить необходимый profiling.
- Выполнить deep performance audit, если требуется.
- Проверить Undo Safety, где применимо.
- Проверить permissions / sandbox, где применимо.
- Проверить non-interactive render / `aerender`, где применимо.
- Проверить bit depth / color management, где применимо.
- Проверить upgrade / migration, где применимо.
- Проверить согласованный scope совместимости.
- Выполнить реальные проверки внутри After Effects.
- Выполнить §28 / §30 только для тех публичных distributables, к которым соответствующий platform gate применим.

#### Решение о release

Убедиться, что:

- все обязательные Test Status имеют PASS;
- все N/A обоснованы;
- нет обязательных BLOCKED / NOT RUN;
- нет известных критических ошибок;
- документация соответствует кандидату;
- Evidence относится к этому кандидату;
- передаваемый файл имеет зафиксированный SHA-256;
- установленная и реально загруженная версия идентифицированы;
- ограничения сформулированы честно.

Во время Release Gate artifact не изменять.

Если потребовалась правка, создать нового Release Candidate и повторить необходимый цикл проверки.

Пользователю как финальный release передаётся именно проверенный файл или пакет, а не заново собранный «такой же».

---

## 28. macOS-дистрибутив: целостность, установка и загрузка
<!-- REQ: MAC-001 -->

Этот gate применяется к распространяемому macOS artifact: native `.plugin`, app/helper, installer/package и применимым panel/UXP компонентам. Приёмка зависит от формата и заявленного способа установки.

### Политика проекта

Для разработки и выпуска не требуются платный Apple developer account, сертификат Apple для распространения, отправка artifact во внешнюю службу проверки или прикрепление её ticket. Отсутствие этих ресурсов само по себе не создаёт Test: BLOCKED и не запрещает Release.

Допускается artifact без подписи либо с локальной ad-hoc подписью, если он проходит применимые install/runtime checks. Если локальная подпись нужна выбранному runtime, её создавать до фиксации финального hash; наличие подписи не доказывает совместимость с After Effects.

Не запускать операции с Apple account/credentials и не запрашивать их как prerequisite. Внешние каналы могут иметь собственные условия приёма пакета: выбирать канал, соответствующий согласованному способу доставки, и подтверждать его фактическую работоспособность. Локальный install не доказывает принятие пакета сторонним магазином.

### Обязательные проверки

Для заявленного способа распространения:

1. Зафиксировать точный commit, Build ID, целевые macOS/архитектуры и финальный hash/manifest.
2. Проверить структуру package/bundle, native architectures, resources и dependencies по scope.
3. Получить тот же пакет через выбранный канал доставки и записать фактические условия установки, включая системные предупреждения и quarantine metadata, если они появились.
4. В безопасном owned test environment выполнить установку по подготовленной пользовательской инструкции.
5. Запустить целевой host, подтвердить реально загруженный Build ID и выполнить smoke/integration checks.
6. Проверить update/uninstall, когда они входят в продукт; сохранять пользовательские данные.
7. Зафиксировать ограничения и минимальные действия пользователя в руководстве для этого artifact.

Не обещать установку без предупреждений или поддержку непроверенного канала. Системное предупреждение не равнозначно runtime failure; невозможность установить или загрузить пакет по заявленному пути остаётся FAIL/BLOCKED по фактической причине. Недоступная обязательная runtime-проверка остаётся BLOCKED/NOT RUN.

Нельзя автоматически ослаблять общесистемные настройки безопасности или удалять quarantine metadata ради зелёного отчёта. Любое действие с пользовательской системой должно оставаться в пределах разрешённого scope; реально выполненные действия фиксировать честно. Это не вводит отдельного требования к Apple-сервисам.

### Финальный artifact

Передавать именно проверенные bytes. После изменений bundle/package, локальной подписи или другого post-processing создавать новую artifact identity, пересчитывать SHA-256 и повторять затронутые проверки. Source-only `.jsx`, pure `.ccx` и другие форматы проверяются по своему install/runtime scope; сертификат не заменяет такую проверку.

`macos-bundle-verify.sh` собирает artifact identity и проверяет соответствие текущим bytes. Его PASS относится только к целостности записанного artifact; actual download/install/host load остаются отдельными проверками. Он не требует account, certificate или удалённых сервисов.

---

## 29. Cross-platform architecture и перенос macOS ↔ Windows

Если продукт планируется для macOS и Windows, по умолчанию использовать **одну общую кодовую базу**, а не две постоянно расходящиеся ветки разработки.

Предпочтительная структура:

- общий platform-independent core;
- минимальные platform adapters для macOS и Windows;
- отдельные build configurations;
- отдельные packaging / installer steps;
- отдельные platform-specific tests;
- единая shared test suite для общего поведения;
- CI matrix по поддерживаемым платформам, где это технически возможно.

Постоянные ветки вида `mac` и `windows` не использовать как основную архитектуру продукта, если нет доказанной необходимости.

Допустимы временные feature / porting branches, но завершённые изменения должны возвращаться в общую основную ветку, чтобы исправления и функциональность не расходились между платформами.

### Обязательный porting audit

Перед переносом существующего продукта с одной платформы на другую определить:

- platform-specific source files и build settings;
- зависимости от macOS frameworks / Windows APIs;
- filesystem paths и path semantics;
- permissions и sandbox / security assumptions;
- process launching / IPC;
- dynamic libraries и runtime dependencies;
- compiler / linker assumptions;
- endian / integer / pointer-size assumptions, если применимо;
- UI scaling / HiDPI;
- Unicode / locale;
- installer / update / uninstall;
- code signing;
- crash reporting / diagnostics;
- GPU APIs и platform-specific acceleration;
- Adobe SDK / host differences, реально влияющие на продукт.

Результат porting audit должен разделять:

- **portable as-is** — код не зависит от платформы;
- **platform adapter required** — нужен тонкий platform-specific слой;
- **rewrite required** — механизм принципиально зависит от платформы;
- **undetermined** — данных недостаточно.

### Перенос native AE plugin

Для native plugins / effects по применимости отдельно проверить:

- macOS `.plugin` ↔ Windows `.aex`;
- Xcode / clang ↔ MSVC toolchain;
- bundle / resources / PiPL packaging;
- exported entry points;
- architecture scope;
- linked frameworks ↔ DLL / import libraries;
- deployment target / supported Windows version;
- runtime libraries;
- filesystem and Unicode behavior;
- crash / exception boundaries;
- CPU/GPU implementation parity;
- MFR / SmartFX / aerender behavior в каждой платформе.

Успешная сборка на второй платформе не считается доказательством совместимости.

Для каждой платформы необходимы отдельные runtime Evidence и compatibility status.

### Общий функциональный контракт

Platform-specific реализации одного и того же пользовательского поведения должны иметь общий набор acceptance tests, где это возможно.

Если macOS и Windows версии сознательно отличаются по функциональности:

- различие должно быть документировано;
- compatibility / feature matrix должна показывать его явно;
- пользовательская документация должна описывать различие;
- нельзя выдавать одну платформу за эквивалент другой без Evidence.

---

## 30. Windows-дистрибутив: целостность, установка и загрузка
<!-- REQ: WIN-001 -->

Этот gate применяется к распространяемому Windows artifact: native `.aex`/DLL, helper/app, installer/package и применимым script/panel компонентам. Объём проверки определяется форматом и заявленным способом установки.

### Политика проекта

Для разработки и выпуска не требуются code-signing certificate, платный аккаунт поставщика сертификата, подпись распространяемого кода или доступ к внешнему сервису заверения времени. Их отсутствие само по себе не создаёт Test: BLOCKED и не запрещает Release.

Допускается неподписанный artifact, если он проходит применимые integrity/install/runtime checks. Не требовать от пользователя сертификат или доступ к сервису подписания как prerequisite и не обращаться к таким сервисам автоматически. Если проект отдельно выбрал локальную подпись, выполнить её до фиксации hash; она не заменяет реальные проверки продукта.

Сторонний магазин/канал может иметь собственные условия приёма. Проверять согласованный путь распространения и не объявлять любой канал поддерживаемым только по успешной локальной сборке.

### Обязательные проверки

1. Зафиксировать точный commit, Build ID, целевую Windows/архитектуру и финальный hash/manifest.
2. Проверить PE architecture, runtime dependencies и структуру package по применимости; исходный `.jsx`/pure package не нуждается в PE-проверке.
3. Получить именно финальные bytes через выбранный канал доставки; записать фактические предупреждения и Zone.Identifier, если они появились.
4. В безопасном owned test environment установить продукт по подготовленной пользовательской инструкции.
5. Запустить целевой After Effects, подтвердить реально загруженный Build ID и выполнить smoke/integration checks.
6. Проверить update/uninstall и сохранение пользовательских данных, когда они входят в продукт.
7. Записать ограничения, системные предупреждения и минимальные действия пользователя в руководстве для этого artifact.

Предупреждение системы не равнозначно runtime failure. Не обещать отсутствие предупреждений без фактической проверки. Невозможность установить/загрузить artifact по заявленному пути остаётся FAIL/BLOCKED по наблюдаемой причине; недоступная обязательная runtime-проверка остаётся BLOCKED/NOT RUN.

Нельзя автоматически отключать общесистемные средства защиты или менять настройки пользовательской системы ради зелёного отчёта. Все действия сохраняют ownership/permission scope; результаты и фактически выполненные шаги фиксируются честно. Это не вводит отдельного сертификатного prerequisite.

### Финальный artifact

Передавать тот же artifact, который прошёл identity/integrity, применимые architecture/dependency, install и actual host-load/smoke checks. После изменений package, кода, выбранной локальной подписи или другого post-processing создавать новую identity/hash и повторять затронутые проверки.

`windows-release-verify.ps1` записывает и проверяет artifact bytes/types/modes в своём scope без сервисов подписания. Integrity PASS не является install/AE-load PASS. PE/dependency collector также не подтверждает runtime compatibility.

---

## Source and tooling boundary

Time-sensitive format/platform claims: [SRC-ADOBE-UXP-PACKAGING / SRC-ADOBE-CEP-DISTRIBUTION](../SOURCES.md). `macos-bundle-verify.sh` records and verifies artifact integrity without Apple distribution services. `windows-release-verify.ps1` records/verifies artifact integrity without certificate/timestamp prerequisites. A structural native-bundle PASS does not verify PiPL contents, arbitrary custom entry contracts, dependency policy or AE registration. Project-specific gates remain responsible for these checks.
