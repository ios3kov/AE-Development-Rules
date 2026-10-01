# Release / Distribution Profile

Validation/Release gates и platform distribution requirements. Release — Delivery Gate, а не Risk Profile.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 26. Validation Gate и Release Gate
<!-- REQ: GATE-001 -->

Передача тестового artifact пользователю для ограниченной проверки и финальный release — разные события.

### Validation Gate

Validation Build можно передать пользователю, когда:

- определён конкретный вопрос, который должен подтвердить пользователь;
- artifact однозначно идентифицирован commit / Build ID / hash или эквивалентом;
- выполнены релевантные автоматические и внутренние проверки, доступные разработчику;
- основной проверяемый сценарий не имеет известного обязательного Test: FAIL;
- нет известных критических рисков потери данных, безопасности или повреждения проекта;
- пользователь получает краткую инструкцию проверки и известные ограничения;
- artifact явно обозначен как validation / test build, если он ещё не прошёл Release Gate.

Для обычного Validation Build не требуются автоматически:

- полный Regression Level 2;
- финальный public installer/package;
- Developer ID notarization или Authenticode;
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

## 28. Публичный macOS-дистрибутив без предупреждений Gatekeeper
<!-- REQ: MAC-001 -->

Этот gate применяется не «ко всему, что работает на macOS», а к **публичному distributable, содержащему исполняемый native code, app/helper, installer или другой artifact, для которого macOS code signing / notarization реально являются частью штатной доставки**.

Примеры, где gate обычно применим:

- native `.plugin` / executable bundle;
- helper / companion app;
- installer / package с исполняемым кодом;
- hybrid UXP plugin с macOS `.uxpaddon` native binary;
- другой executable component, который macOS проверяет как код.

Сам по себе source-only `.jsx`, HTML/JS/CSS panel или pure UXP `.ccx` без native binary **не делает Developer ID/notarization обязательными**. Для CEP / UXP package использовать требования Adobe к соответствующему формату распространения отдельно от OS code signing.

По текущей документации Adobe UXP pure `.ccx` package не требует package-level digital signature или timestamp. Для hybrid UXP Adobe отдельно требует signing/notarization macOS `.uxpaddon` binaries.

Если gate применим, финальный этап включает создание нормального пользовательского дистрибутива без небезопасных обходов Gatekeeper.

Тестовый artifact с ad-hoc подписью может использоваться во время разработки, но **не считается финальным публичным macOS-release для executable artifact в scope этого gate**.

### Обязательные требования

Перед публичным macOS release **для artifact в scope этого gate**:

- подписать финальный bundle и применимый исполняемый вложенный код действительным **Apple Developer ID** сертификатом;
- использовать корректную и минимально необходимую signing configuration / entitlements;
- отправить финальный distributable в **Apple Notary Service** и получить статус `Accepted`;
- выполнить stapling notarization ticket для форматов, где Apple это поддерживает;
- проверить финальную подпись через `codesign --verify --strict` с подходящими параметрами;
- выполнить применимую Gatekeeper / `spctl` проверку;
- сохранить signing authority, Team ID, notarization submission ID, результат notarization и hashes финальных файлов;
- убедиться, что signing / notarization / stapling не были выполнены после зафиксированной проверки без создания нового идентифицированного кандидата.

### Обязательная реальная проверка распространения

Проверять не только локальный файл из build directory.

Необходимо проверить **тот же способ доставки, который получит пользователь**:

1. Опубликовать или поместить финальный пакет в эквивалентный реальному каналу загрузки.
2. Скачать его обычным способом так, чтобы macOS установил quarantine metadata.
3. Проверить на чистом Mac или чистом пользовательском окружении.
4. Установить стандартным пользовательским способом.
5. Запустить целевой host / приложение и убедиться, что продукт загружается и работает.
6. Убедиться, что macOS не требует отключать Gatekeeper, удалять quarantine attribute или использовать исключения безопасности.

Запрещено считать публичный macOS gate пройденным, если для установки или первого запуска требуется:

- `xattr -d` / `xattr -dr com.apple.quarantine`;
- `spctl --master-disable`;
- отключение Gatekeeper;
- ручное разрешение через `Open Anyway` как обязательная инструкция;
- правый клик → Open как штатный способ обхода предупреждения;
- удаление или обход подписи;
- любые другие действия, снижающие системную защиту пользователя.

### Финальный artifact

Для artifact в scope этого gate публично передаваемый файл должен быть именно тем artifact, который прошёл:

- Developer ID signing;
- notarization;
- применимый stapling;
- Gatekeeper validation;
- реальную установку из quarantined download;
- финальный smoke test.

Для source-only / pure package artifact вне scope этого gate применяются его format-specific install/package checks, а не искусственное требование Apple code signing.

После любого изменения байтов bundle / installer / archive необходимо заново:

- зафиксировать artifact identity;
- пересчитать SHA-256;
- повторить необходимые signing / notarization проверки;
- повторить затронутые smoke / integration проверки.

Если artifact находится в scope этого gate, а обязательные Developer ID, notarization или реальная Gatekeeper-проверка недоступны, соответствующий Test Status — **BLOCKED**, а не PASS.

Executable macOS distributable в scope этого gate не считается release-ready, пока его нельзя штатно установить и запустить без инструкций по отключению или обходу системной защиты.


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

## 30. Публичный Windows-дистрибутив и release gate
<!-- REQ: WIN-001 -->

Этот gate применяется к публичному Windows distributable, когда продукт содержит **PE/native executable code, helper/app, installer или иной компонент, для которого Authenticode / Windows security checks реально относятся к штатной доставке**.

Source-only JSX, HTML/JS/CSS panel или pure UXP `.ccx` без native executable не требуют Authenticode только потому, что используются на Windows. CEP ZXP signing и UXP CCX packaging являются отдельными format-specific требованиями Adobe.

Если gate применим, финальный release должен устанавливаться и запускаться стандартным пользовательским способом без необходимости отключать системные механизмы безопасности.

### Обязательные требования

Перед публичным Windows release для artifact в scope этого gate:

- собрать production artifact для заявленной архитектуры;
- проверить PE / binary architecture и runtime dependencies;
- подписать применимый исполняемый код и installer действительным code-signing certificate;
- использовать timestamping, чтобы подпись оставалась проверяемой после истечения сертификата;
- проверить Authenticode signature стандартными Windows средствами, например SignTool / PowerShell;
- проверить installer / package integrity;
- зафиксировать signing identity, timestamp result и SHA-256 финального distributable;
- убедиться, что signing / packaging не изменялись после финальной проверки без создания нового кандидата.

### Реальная проверка распространения

Проверять именно тот файл и канал, который получит пользователь.

Необходимо:

1. Получить финальный distributable через реальный или эквивалентный публичному канал доставки.
2. Проверить его на чистом Windows test environment.
3. Выполнить стандартную установку без ручного копирования скрытых dependencies.
4. Запустить целевой After Effects и убедиться, что продукт загружается.
5. Выполнить финальный smoke test.
6. Проверить uninstall / update сценарий, если они входят в заявленный продукт.
7. Убедиться, что нормальная установка не требует отключения Defender, SmartScreen, UAC или других системных защит.

Нельзя считать Windows release gate пройденным, если штатная инструкция требует:

- отключить Windows Defender;
- отключить SmartScreen;
- запускать систему с ослабленными security settings;
- вручную копировать случайные runtime DLL из неизвестных источников;
- отключать UAC;
- игнорировать повреждённую / недействительную подпись;
- использовать другие небезопасные обходы как нормальный installation path.

SmartScreen reputation и предупреждения, зависящие от внешней репутационной системы, следует фиксировать отдельно от криптографической валидности подписи. Нельзя заявлять отсутствие таких предупреждений без реальной проверки на целевом канале распространения.

### Финальный Windows artifact

Для artifact в scope этого gate пользователю передаётся именно тот package / installer / archive, который прошёл:

- identity / hash фиксацию;
- применимое signing;
- signature verification;
- dependency / architecture audit;
- чистую установку;
- runtime загрузку в целевом After Effects;
- финальный smoke test.

Для source-only / pure package artifact вне scope этого gate использовать format-specific package/install verification без искусственного Authenticode requirement.

Если artifact находится в scope этого gate, а обязательная подпись, целевая Windows-среда или реальная runtime-проверка недоступны, соответствующий Test Status — **BLOCKED**, а не PASS.


---


## Source and tooling boundary

Time-sensitive platform claims: [SRC-APPLE-NOTARIZATION / SRC-MICROSOFT-TIMESTAMP / SRC-ADOBE-CEP-DISTRIBUTION](../SOURCES.md). `macos-bundle-verify.sh` selects local/public scope and explicit required/N/A stapling policy. `windows-release-verify.ps1` requires timestamp evidence by default; LocalCheck is limited local verification. A structural native-bundle PASS does not verify PiPL contents, arbitrary custom entry contracts, dependency policy or AE registration. Project-specific gates remain responsible for these checks.
