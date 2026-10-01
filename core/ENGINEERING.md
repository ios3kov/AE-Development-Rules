# Engineering Core

Общие инженерные требования: safety, diagnostics, performance, reproducibility, compatibility/maturity, documentation, quality, dependencies, updates, crash diagnostics, accessibility и testability.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 14. Качество и безопасность кода

Код должен быть:

- понятным;
- простым;
- минимально достаточным;
- безопасным;
- тестируемым;
- диагностируемым;
- достаточно быстрым для требований;
- без dead code;
- без ненужных dependencies.

Предпочитать простое рабочее решение сложной архитектуре без доказанной пользы.

Обязательно учитывать:

- проверку входных данных;
- ограничения host API;
- владение ресурсами;
- корректное освобождение памяти и handles;
- исключения и error codes;
- thread safety;
- ограничения main thread;
- корректную отмену операций;
- безопасное восстановление после ошибки.

Для helpers / IPC / file operations дополнительно проверять:

- валидацию сообщений;
- ограничения доступа;
- безопасную обработку путей;
- недопустимость исполнения непроверенных команд;
- отсутствие секретов в исходниках и логах.

Сторонние компоненты должны быть необходимыми, лицензируемыми и поддерживаемыми.

### Защита пользователя и недоверенные входные данные

Любые данные вне полного контроля инструмента считать потенциально недоверенными по применимости:

- пути и имена файлов;
- содержимое проектов и metadata;
- импортируемые presets / configs / JSON / text;
- drag-and-drop input;
- network responses;
- IPC / bridge messages;
- environment variables;
- данные helper-процессов.

Необходимо:

- валидировать тип, размер, диапазон и структуру входных данных;
- нормализовать и проверять filesystem paths до чтения, записи, удаления или запуска;
- защищаться от path traversal и записи вне разрешённой области;
- не строить shell-команды конкатенацией недоверенных строк;
- не выполнять полученный извне код, scripts или команды без явно предусмотренного доверенного механизма;
- ограничивать размеры, количество элементов, retries и timeouts, чтобы malformed input не создавал runaway CPU/RAM/I/O;
- применять least privilege к filesystem, network, helpers и permissions;
- fail closed для опасных или неоднозначных операций;
- требовать явного пользовательского действия перед необратимым destructive operation, если такое действие является частью продукта;
- проверять update/download mechanism и целостность полученных artifacts, если продукт умеет обновляться или загружать executable content.

UI не должен маскировать destructive действие под безобидную операцию. Название, scope и последствия должны быть понятны до выполнения.

---

## 15. Workarounds и технический долг

Не использовать временные, хрупкие или «магические» решения без обоснования.

Если workaround необходим:

- объяснить причину;
- указать ограничение API или воспроизводимую проблему;
- описать область действия;
- добавить проверку его поведения;
- зафиксировать риски;
- указать условие удаления или пересмотра;
- создать запись технического долга, если применимо.

Если долгосрочное решение неизвестно, прямо это указать.

Workaround не должен незаметно превращаться в постоянную архитектуру.

Не удалять защитный workaround без проверки, что исходная проблема действительно устранена в поддерживаемых конфигурациях.

---

## 16. Диагностируемость и non-interactive safety

Инструмент должен позволять определить:

- какая версия запущена;
- какой Build ID используется;
- на каком этапе произошёл сбой;
- что вернул host API;
- какие входные условия привели к ошибке;
- можно ли безопасно повторить операцию.

Где применимо, нужны:

- структурированные логи;
- понятные ошибки;
- Diagnostics;
- timings;
- crash information;
- feature-specific debug information;
- operation / correlation IDs.

Для scripts / panels особенно важны:

- exceptions;
- host API failures;
- отсутствующие comps / layers / files;
- permissions;
- bridge errors;
- lifecycle events;
- timers;
- asynchronous operations.

Логи не должны без необходимости раскрывать:

- секреты;
- содержимое пользовательских проектов;
- персональные данные;
- полные чувствительные пути.

### Non-interactive Render Safety

Во время:

- `PF_Cmd_RENDER`;
- Smart Render callbacks;
- background rendering;
- `aerender`;
- render farm execution;
- других non-interactive операций

нельзя выполнять действия, требующие ответа пользователя:

- `alert`;
- `prompt`;
- modal dialogs;
- confirmation dialogs;
- interactive error windows.

Render path не должен зависеть от наличия UI.

Ошибка должна:

- возвращаться через подходящий API;
- фиксироваться доступным безопасным способом;
- приводить к документированному результату;
- не блокировать процесс ожиданием ввода.

Нельзя молча выдавать неправильный кадр как успешный результат. Пропуск или fallback допустимы только при определённой и проверенной семантике.

Диагностический UI разрешён только в интерактивном UI-контексте.

Logging должен быть thread-safe, ограниченным по объёму и не создавать существенной production-нагрузки.

---

## 17. Производительность и корректность результата

Производительность оценивать по типу инструмента и реальному пользовательскому сценарию.

Корректность результата имеет приоритет над ускорением, если иной компромисс явно не предусмотрен требованиями.

### Native render / effect plugins

Особое внимание:

- Render и RAM Preview;
- CPU / GPU;
- MFR;
- память;
- кэширование;
- копирование кадров;
- allocations;
- threading;
- Smart Render;
- ROI;
- CPU ↔ GPU transfers;
- pixel-format conversions.

### Color / Bit Depth Correctness

Корректно поддерживать все заявленные режимы:

- 8 bpc;
- 16 bpc;
- 32 bpc float.

Учитывать реальные представления пикселей и диапазоны значений в Adobe SDK. Не считать любой 16-bit buffer автоматически эквивалентом диапазона обычного `uint16`.

Для 32 bpc:

- сохранять предусмотренную алгоритмом precision;
- не предполагать диапазон исключительно `0.0–1.0`;
- не выполнять непреднамеренный clamp;
- не создавать unintended clipping отрицательных и extended-range значений;
- корректно обрабатывать HDR;
- определить поведение для нечисловых и бесконечных значений, если они возможны.

Проверять применимые:

- Working Space;
- Linear Working Space;
- OCIO workflows;
- color-space conversions;
- alpha interpretation;
- CPU/GPU consistency.

Переход между bit depths не должен вызывать необъяснимых изменений результата, кроме предусмотренных различий диапазона, precision и документированных особенностей алгоритма.

### Scripts / panels / extensions

Особое внимание:

- startup time;
- UI latency;
- main-thread blocking;
- host calls;
- batching;
- file I/O;
- parsing / serialization;
- память;
- listeners;
- timers / polling;
- IPC / bridge calls;
- большие проекты;
- большое число layers / items.

Инструмент не должен создавать ненужную постоянную нагрузку в idle-состоянии.

---

## 18. Оптимизация только по измерениям

Если оптимизация усложняет код, её польза должна подтверждаться измерениями.

Не оптимизировать по принципу:

> Кажется, так быстрее.

Для существенного performance-изменения фиксировать:

**Before → Change → After.**

Сравнение должно использовать сопоставимые:

- проекты;
- параметры;
- оборудование;
- версии After Effects;
- render paths;
- bit depths;
- cache states;
- условия нагрузки.

Замеры должны учитывать:

- прогрев;
- несколько повторений;
- разброс результатов;
- cold / warm сценарии;
- накладные расходы измерения.

Не заявлять ускорение, если отличие находится в пределах шума измерений.

После оптимизации проверять не только скорость, но и:

- корректность output;
- память;
- стабильность;
- responsiveness;
- отсутствие переноса затрат в другой критичный этап.

Оптимизация без подтверждённой пользы не должна усложнять production-код без отдельного обоснования.

---

## 19. Profiling — два уровня

### Level 1 — во время разработки

После performance-sensitive изменений:

- быстрый benchmark;
- проверка очевидного ухудшения;
- сравнение с baseline;
- проверка релевантных ресурсов.

### Level 2 — для Critical Risk Profile, milestone и Release Candidate

Проводить profiling реального сценария внутри After Effects в объёме, определённом рисками и требованиями.

Для native effects исследовать применимые:

- CPU / GPU;
- RAM;
- Render / RAM Preview;
- allocations;
- threading;
- MFR;
- transfers;
- Smart Render;
- ROI;
- pixel-format conversions.

Для scripts / panels исследовать применимые:

- startup;
- execution time;
- UI stalls;
- host calls;
- file I/O;
- память;
- listeners / timers;
- repeated operations;
- большие проекты;
- idle-нагрузку.

Полный deep profiling обязателен для performance-critical инструмента, существенной оптимизации или обнаруженной деградации.

Для изменений, не затрагивающих performance, допускается актуальный baseline и ограниченная sanity-проверка с обоснованием.

Performance-critical вывод должен подтверждаться реальным profiling или benchmark, а не только теоретическим анализом.

---

## 20. Воспроизводимые сборки и неизменность artifact

Production artifact должен собираться из зафиксированных исходников в документированном чистом окружении.

Не допускать скрытой зависимости от:

- старых локальных файлов;
- случайного SDK;
- глобальных packages;
- устаревших dependencies;
- кэшей;
- предыдущих builds;
- недокументированных environment variables;
- ручных production-правок.

Фиксировать:

- toolchain;
- SDK;
- зависимости;
- lockfiles, где применимо;
- build configuration;
- значимые environment variables;
- команды build / package;
- signing process без раскрытия секретов.

### Уровни воспроизводимости

Различать:

- **функционально воспроизводимую сборку** — те же исходники и окружение создают эквивалентный по поведению artifact;
- **битово воспроизводимую сборку** — результат совпадает побайтно.

Не обещать одинаковый SHA-256, если artifact содержит изменяющиеся timestamps, Build IDs или подписи.

Недетерминированные части должны быть известны и документированы.

### Неизменность кандидата на выпуск

После создания финального кандидата нельзя менять его production-файлы без создания нового кандидата.

Любое изменение кода, dependencies, build settings или package contents:

- создаёт новый artifact identity;
- требует нового hash;
- требует повторной проверки затронутых сценариев;
- требует повторного прохождения обязательного финального gate для нового кандидата.

Evidence старой версии можно использовать как историческое сравнение, но не выдавать за проверку нового artifact.

---

## 21. Совместимость и применимость технологий

### Technology Lifecycle Status

Compatibility и maturity — разные вещи. Технология может работать в конкретной конфигурации, но оставаться beta/deprecated как platform choice.

Использовать отдельный **Technology Lifecycle Status**:

- **PREVIEW** — prerelease/experimental/not-yet-public-beta capability; production baseline требует явного project decision и documented fallback/exit plan.
- **BETA** — публичная beta; допустима для controlled production только с явным acceptance риска, pin целевой host version и расширенными runtime tests.
- **GA** — general availability / обычный поддерживаемый production path.
- **DEPRECATED** — технология ещё может работать и поддерживаться в переходный период, но vendor объявил её замену/вывод; новые долгоживущие архитектуры требуют documented justification и migration plan.
- **RETIRED** — vendor support/runtime distribution завершены; новый production baseline запрещён, кроме явно изолированного legacy maintenance scope.

На baseline 2026-10-01 согласно Adobe extensibility roadmap:

- After Effects UXP ещё не public beta; Adobe объявила public beta к ноябрю 2026. До фактического выхода public beta считать AE UXP **PREVIEW** для production-решений.
- CEP находится в объявленном переходе к retirement и считается **DEPRECATED** для новой долгоживущей архитектуры; Adobe планирует завершить CEP transition к концу 2029.
- ExtendScript этим CEP→UXP transition не затрагивается.

Эти статусы time-sensitive и не должны жить как вечный hardcode: authoritative source и дата проверки находятся в [SOURCES.md](../SOURCES.md). Перед новым technology decision проверять актуальное состояние источника.

Для PREVIEW/BETA/DEPRECATED технологии MUST:

- зафиксировать причину выбора;
- определить целевой host/version scope;
- иметь fallback, migration или exit plan, если технология недоступна/меняется;
- не обещать пользователю GA-level stability без соответствующего vendor/runtime Evidence.

Вести матрицу реально проверенной совместимости.

Учитывать по применимости:

- версии After Effects;
- macOS / Windows;
- Apple Silicon / Intel;
- процессорную архитектуру;
- GPU и драйвер;
- CPU / GPU render path;
- ExtendScript;
- ScriptUI;
- CEP;
- UXP;
- helper runtimes;
- permissions;
- paths;
- Unicode;
- локализацию;
- HiDPI;
- 8 / 16 / 32 bpc;
- Linear Color;
- OCIO.

Матрица должна содержать:

- конфигурацию;
- проверенный Build ID;
- объём проверки;
- дату;
- результат;
- известные ограничения.

Использовать только **Compatibility Status** из §10: VERIFIED / STATIC-COMPATIBLE / LIMITED / UNSUPPORTED / UNKNOWN.

Не считать всю платформу VERIFIED по одному запуску одного smoke test. Указывать фактический scope.

### Статический compatibility audit по API

Если нет возможности установить или запустить все старые целевые версии After Effects, выполнять статический compatibility audit, чтобы определить вероятный минимальный совместимый диапазон без подмены реального runtime-теста.

Для native plugins / effects по применимости необходимо:

- собрать полный список используемых Adobe API, включая PF, AEGP, SmartFX, Custom UI и связанные suites;
- для каждого используемого API / suite определить минимальную версию After Effects / SDK, в которой он доступен;
- проверить используемые версии suites и зависимости от конкретных suite revisions;
- проверить PiPL, Effect Spec Version, flags, capabilities и compile-time guards;
- проверить SDK- и toolchain-зависимости, способные ограничивать совместимость;
- для macOS проверить deployment target, архитектуры Mach-O, linked frameworks / dylibs, weak / strong linking и внешние symbols;
- для Windows проверить минимальную поддерживаемую версию ОС, архитектуру, runtime dependencies и импортируемые symbols / libraries;
- найти места, где код зависит не только от наличия API, но и от version-specific поведения After Effects;
- отдельно учитывать MFR, SmartFX, render lifecycle, Custom UI и другие host-механизмы, поведение которых могло меняться между версиями;
- задокументировать найденные blockers, риски и допущения.

Результат статического compatibility audit записывать через **Compatibility Status** из §10:

- **VERIFIED** — версия реально запущена и проверена в After Effects в заявленном scope;
- **STATIC-COMPATIBLE** — статический аудит не выявил известных API / binary / platform препятствий, но runtime-проверка этой версии не выполнена;
- **LIMITED** — подтверждён только ограниченный scope;
- **UNKNOWN** — есть version-specific поведение, неполные данные или иная неопределённость;
- **UNSUPPORTED** — найдено конкретное несовместимое API, binary, platform или host requirement.

`STATIC-COMPATIBLE` не является эквивалентом `VERIFIED`.

Статический аудит может использоваться для определения **минимальной вероятно совместимой версии After Effects**, но без реального runtime-теста такую версию нельзя называть VERIFIED.

Если в пользовательской документации версия обозначается как официально поддерживаемая, для неё должен существовать реальный runtime Evidence в соответствии с матрицей совместимости.
### Unicode, локализация и региональные настройки

Если инструмент работает с пользовательскими именами, файлами, путями или текстом, проверять по применимости:

- Unicode и не-ASCII имена файлов, folders, comps, layers и project items;
- кириллицу и другие не-Latin символы;
- пробелы и специальные символы;
- различия path separators и filesystem semantics между macOS / Windows;
- locale-dependent decimal / thousands separators;
- форматирование чисел, дат и времени;
- локализованный интерфейс After Effects, если код зависит от UI names / menu text;
- длину строк, clipping и resize локализованного UI;
- encoding старых Adobe API / legacy buffers, где UTF-8 не гарантирован.

Не парсить локализованный UI-текст, если существует стабильный ID / host API.

Если продукт заявляет несколько языков интерфейса, для каждого заявленного языка проверить ключевые пользовательские сценарии и отсутствие сломанных строк / layout.

Поддержка Unicode paths и пользовательских имён должна проверяться даже для продукта только с английским UI, если такие данные входят в заявленный scope.

### UXP host support

Для UXP в этом разделе фиксируется только Compatibility Status целевой версии AE. Полный runtime / sandbox / permissions / lifecycle / packaging contract находится в §40 и намеренно не дублируется здесь.

Общая документация UXP или проверка в другом Adobe host не являются Evidence поддержки конкретной версии After Effects.

---

## 24. Документация после каждого этапа

После законченного значимого этапа обновлять:

- статус;
- реализованное поведение;
- ограничения;
- затронутые тесты;
- Evidence;
- принятые решения;
- известные проблемы;
- следующие шаги.

Архитектуру, инструкции сборки и другие разделы обновлять, если они действительно изменились.

Не переписывать всю документацию после каждой небольшой правки.

В milestone / release record фиксировать:

- Git commit;
- Build ID;
- artifact;
- SHA-256;
- результаты обязательных проверок;
- совместимость;
- известные ограничения.

Документация должна отделять:

- реализовано;
- проверено;
- предполагается;
- запланировано;
- не поддерживается.

Секреты, персональные данные и чувствительные пользовательские материалы в документацию и публичное Evidence не включать.

### Рекомендуемая структура документации

Для проектов среднего и большого размера предпочтительно хранить canonical engineering documentation в Git рядом с кодом в Markdown или другом текстовом diff-friendly формате.

Рекомендуемая структура:

- `docs/ARCHITECTURE.md` — архитектура и ключевые границы;
- `docs/STATUS.md` или milestone status records — текущее подтверждённое состояние;
- `docs/COMPATIBILITY.md` — compatibility matrix;
- `docs/TEST_RECORDS/` — test records и ссылки на Evidence;
- `docs/RELEASES/` или release records — финальные кандидаты и release gates;
- `docs/RETROSPECTIVE-<version>.md` — техническая ретроспектива;
- `docs/USER_GUIDE.md` — пользовательское руководство;
- `docs/AE_ENGINEERING_KNOWHOW.md` — reusable AE know-how, если проект является источником общих выводов.

Sphinx, MkDocs, Wiki, сайт или другая система публикации могут использоваться дополнительно, но должен быть определён один canonical source of truth. Генерируемая публичная документация не должна расходиться с ним.

Внутренние Evidence, crash dumps, чувствительные пути и данные пользователей не публиковать только ради единой структуры.

---

## 25. Итоговая техническая документация

Проект должен оставлять инженерную базу знаний.

После завершения проекта или значимого milestone сохранить применимые сведения:

- устройство и архитектуру;
- используемые Adobe API;
- сторонние API и dependencies;
- выбранные решения и причины;
- отвергнутые решения и причины;
- ограничения After Effects;
- ограничения SDK / runtime;
- известные ошибки;
- performance-паттерны;
- способы диагностики;
- compatibility matrix;
- build / package process;
- Build Identity process;
- signing / release process;
- контролируемое и чистое тестирование;
- automated AE testing;
- test fixtures и ожидаемые результаты;
- Undo behaviour;
- permissions / sandbox;
- render / background execution;
- bit depth / color management;
- installation / update / uninstall;
- migration и rollback;
- известный технический долг.

Документация должна позволять другому разработчику воспроизвести сборку, проверить artifact и продолжить работу без восстановления скрытых знаний.

### 25.1. Ретроспектива и накопление AE know-how

После успешного завершения проекта, крупного milestone или существенного цикла разработки **обязательно выполнить техническую ретроспективу**.

Цель ретроспективы — не пересказать changelog, а сохранить фактически полученные знания об After Effects, Adobe SDK и выбранной архитектуре, чтобы следующий проект не повторял уже пройденные исследования и ошибки.

Ретроспектива должна быть основана на фактическом Evidence текущего проекта и отдельно фиксировать:

- **что реально работает в After Effects** в проверенном scope;
- **что не работает, работает ненадёжно или имеет ограничения**;
- какие возможности AE / SDK первоначально предполагались возможными, но на практике оказались недоступными или непригодными;
- какие Adobe API, suites, callbacks, lifecycle-паттерны и host-механизмы оказались пригодными;
- какие архитектурные и инженерные решения дали хороший результат и почему;
- какие решения, обходы и экспериментальные подходы были отвергнуты и почему;
- какие ошибки проектирования, интеграции, сборки, упаковки или тестирования были обнаружены;
- какие специфические особенности, неочевидное поведение и «грабли» After Effects были выявлены;
- какие приёмы диагностики позволили доказать причину проблемы;
- какие подходы к Undo, keyframes, render lifecycle, MFR / SmartFX, UI, AEGP, coordinate systems, bit depth, color management, packaging, signing и другим применимым областям подтвердили свою пригодность;
- какие performance-паттерны оказались полезными или бесполезными;
- какие решения безопасны только в конкретном scope и не должны обобщаться;
- какие технические приёмы и **know-how можно переиспользовать в следующих AE-плагинах**;
- какие выводы следует перенести в общие правила, шаблоны, тестовые инструменты или инженерную базу знаний.

Для каждого значимого вывода по возможности фиксировать:

- контекст и проблему;
- проверенный способ решения;
- доказательство / Evidence;
- версии AE / SDK / ОС и применимый scope;
- ограничения и противопоказания;
- ссылку на commit, issue, PR, test fixture или диагностический материал.

Нельзя превращать ретроспективу в список неподтверждённых предположений. Для уверенности вывода использовать **Evidence Confidence** из §10:

- **PROVEN** — подтверждено воспроизводимыми tests или реальным host evidence;
- **USER-REPORTED** — подтверждено пользователем в целевой среде, но не воспроизведено независимо;
- **OBSERVED** — наблюдение или исследовательский вывод с ограниченным scope;
- **UNVERIFIED** — вопрос остаётся открытым.

Отдельно от Evidence Confidence фиксировать outcome эксперимента, например `accepted` / `rejected`. Не использовать `FAILED` как evidence label, чтобы не путать его с Test Status FAIL.

Особенно ценны отрицательные результаты. Если подход потребовал много исследования и оказался тупиковым, это знание нужно сохранить вместе с причиной, чтобы его не повторяли в следующем проекте.

Ретроспектива должна отдельно отвечать минимум на пять вопросов:

1. Что теперь мы точно знаем, что **можно и работает** в After Effects?
2. Что теперь мы точно знаем, что **нельзя, ненадёжно или не стоит делать**?
3. Какие **новые know-how / паттерны** были получены?
4. Какие решения дали лучший результат и почему?
5. Что из этого необходимо **переиспользовать или добавить в общую инженерную базу** следующих проектов?

Рекомендуемый отдельный документ проекта: `docs/retrospective-<milestone-or-version>.md` либо эквивалентный явно обозначенный retrospective record.

Общая переиспользуемая AE-база знаний: `docs/AE_ENGINEERING_KNOWHOW.md`. Проверенные выводы, применимые шире одного продукта, переносить туда в обобщённом виде.

Если вывод применим не только к текущему продукту, его нельзя оставлять только внутри истории одного репозитория: после проверки он должен быть обобщён и перенесён в общую AE-инженерную документацию / правила / reusable tooling без привязки к случайным деталям конкретного проекта.

Ретроспектива является частью критерия завершения значимого цикла разработки. **Проект может быть функционально принят, но инженерный цикл не считается полностью закрытым, пока накопленный AE know-how не зафиксирован.**


### 25.2. Пользовательское руководство

После завершения разработки проекта или значимого пользовательского релиза **обязательно подготовить и актуализировать руководство для конечного пользователя**.

Руководство должно соответствовать именно финальной передаваемой версии продукта и объяснять простым человеческим языком:

- с какими конкретными версиями After Effects совместим продукт;
- какие операционные системы и архитектуры поддерживаются, если это существенно для установки или работы;
- как установить продукт;
- где найти и как запустить его в After Effects;
- как пользоваться основными функциями;
- типовые пользовательские сценарии пошагово;
- назначение основных настроек, кнопок и элементов интерфейса;
- известные ограничения, которые важны пользователю;
- что делать при типичных проблемах;
- как обновить продукт;
- как удалить продукт.

Поддерживаемыми в пользовательском руководстве разрешено называть только версии After Effects и конфигурации, для которых есть соответствующее подтверждение по §21. Непроверенные версии должны быть явно обозначены как непроверенные, а не как совместимые.

Главное требование: руководство пишется **для пользователя, а не для разработчика**.

Поэтому необходимо:

- использовать минимум технического жаргона;
- объяснять действия конкретно и последовательно;
- использовать понятные названия элементов интерфейса;
- добавлять примеры там, где они помогают быстрее понять работу продукта;
- не заставлять пользователя разбираться во внутренней архитектуре, SDK, Build ID, логах или других инженерных деталях, если они не нужны для обычной работы;
- при необходимости использовать скриншоты, схемы или короткие визуальные примеры;
- проверять, что инструкция не описывает устаревший интерфейс или поведение.

Пользовательское руководство является частью финальной документации и release readiness.

**Разработка пользовательского продукта не считается полностью завершённой, пока для финальной версии нет актуального и понятного пользовательского руководства.**

---

## 31. Контроль качества и инженерные метрики

Метрики использовать для обнаружения деградаций и улучшения процесса, а не как самоцель и не для оценки отдельных людей.

Не использовать строки кода, количество commits или число тестов как самостоятельную меру качества.

Для активного продукта по применимости отслеживать:

- escaped defects — ошибки, дошедшие до пользователя после release;
- regression failures по milestone / release;
- flaky tests и долю нестабильных проверок;
- crash / hang incidents;
- performance regressions относительно зафиксированного baseline;
- открытые critical / high-severity defects;
- повторно открытые bugs;
- время от воспроизведения дефекта до подтверждённого fix;
- количество обязательных ручных release-шагов, которые разумно автоматизировать.

Метрика должна иметь:

- чёткое определение;
- источник данных;
- период измерения;
- сравнимый baseline;
- объяснение, какое решение она помогает принимать.

Не вводить numeric quality gate без заранее обоснованного threshold.

Если метрика ухудшилась, исследовать причину. Нельзя улучшать показатель формально, например скрывая FAIL, удаляя сложные тесты или переклассифицируя реальные defects.

---

## 32. Методика составления test cases

Каждый значимый риск или acceptance criterion должен иметь явную проверку либо документированную причину отсутствия проверки.

Минимальный test case содержит:

- Test Case ID;
- требование / риск, который он проверяет;
- тип проверки: static / unit / integration / runtime AE / performance / release;
- применимый Build ID / artifact;
- preconditions и начальное состояние;
- fixture и доказательство ownership, если тест меняет AE/project/files;
- шаги или ссылку на versioned test runner;
- ожидаемый результат;
- допустимую погрешность, где применимо;
- фактический результат;
- статус PASS / FAIL / BLOCKED / NOT RUN / N/A;
- Evidence;
- cleanup / recovery;
- известные ограничения проверки.

### Native effect / render plugin

По применимости включать cases для:

- effect application и default state;
- parameter boundaries;
- interactive render / RAM Preview / Render Queue / aerender;
- SmartFX / MFR;
- 8 / 16 / 32 bpc;
- alpha / transparency / extended range;
- ROI / downsample / pixel aspect;
- cancellation / repeated render;
- CPU/GPU parity;
- save/reopen и cache invalidation;
- malformed / extreme parameters.

### Scripts / ScriptUI panels

По применимости включать:

- no project / no comp / no selection;
- wrong selection type;
- locked / deleted / changed items;
- first run / repeat run / restart;
- exception / early return;
- Undo / Redo;
- cancel;
- saved / corrupted state;
- Unicode paths / names;
- missing files / permissions.

### CEP / UXP

По применимости включать:

- panel open / close / reload / restart;
- bridge request / response validation;
- malformed / empty / delayed response;
- timeout;
- duplicate requests / retries;
- host context changed during async operation;
- permissions / sandbox;
- stale state;
- helper disconnect / recovery;
- loaded Build Identity.

### Helpers / background processes

По применимости включать:

- startup / shutdown / crash recovery;
- IPC validation;
- malformed / oversized messages;
- permissions;
- path validation;
- duplicate instance;
- timeout / cancellation;
- cleanup orphaned processes/files;
- version mismatch between helper and host component.

Test case должен проверять наблюдаемое требование, а не внутреннюю реализацию без необходимости.

Для повторяемых сценариев предпочтителен автоматический runner. Ручной case допустим, если UI/host limitation не позволяет надёжную автоматизацию.

---

## 33. Внедрение стандарта без лишней ручной работы

Общий стандарт должен сопровождаться reusable automation и templates.

Центральный [starter kit](../starter-kit/README.md) рекомендуется использовать как исходную точку.

### Прямые ссылки на scripts

- [macOS/local preflight](../starter-kit/scripts/preflight.sh)
- [Windows preflight](../starter-kit/scripts/preflight.ps1)
- [Artifact identity + SHA-256](../starter-kit/scripts/record-artifact.sh)
- [Starter-kit self-test / consistency audit](../starter-kit/scripts/self-test.mjs)
- [Applicability map generator/check](../starter-kit/scripts/generate-applicability.mjs)
- [Starter-kit behavioural smoke tests](../starter-kit/tests/behavioral-smoke.mjs)
- [ExtendScript sanity-check](../starter-kit/scripts/check-extendscript.mjs)
- [Adobe API inventory для compatibility audit](../starter-kit/scripts/scan-adobe-api.sh)
- [macOS binary audit](../starter-kit/scripts/macos-binary-audit.sh)
- [macOS bundle / signing / Gatekeeper verification](../starter-kit/scripts/macos-bundle-verify.sh)
- [Native AE effect bundle verification on macOS](../starter-kit/scripts/verify-native-effect-bundle-macos.sh)
- [Owned fail-closed AE test workspace](../starter-kit/scripts/create-owned-test-workspace.sh)
- [Windows binary / dependency / Authenticode audit](../starter-kit/scripts/windows-binary-audit.ps1)
- [Windows release signature/hash verification](../starter-kit/scripts/windows-release-verify.ps1)
- [Dependency evidence on macOS/Linux](../starter-kit/scripts/collect-dependency-evidence.sh)
- [Dependency evidence on Windows](../starter-kit/scripts/collect-dependency-evidence.ps1)

### Прямые ссылки на templates

- [Test Record](../starter-kit/templates/TEST_RECORD.md)
- [Test Case](../starter-kit/templates/TEST_CASE.md)
- [Compatibility Matrix](../starter-kit/templates/COMPATIBILITY_MATRIX.md)
- [Static API Compatibility Audit](../starter-kit/templates/API_COMPATIBILITY_AUDIT.md)
- [Build Identity contract](../starter-kit/templates/BUILD_IDENTITY.md)
- [AE Runtime Test Safety](../starter-kit/templates/AE_RUNTIME_TEST_SAFETY.md)
- [Validation Build Checklist](../starter-kit/templates/VALIDATION_CHECKLIST.md)
- [Release Checklist](../starter-kit/templates/RELEASE_CHECKLIST.md)
- [Cross-platform Porting Audit](../starter-kit/templates/CROSS_PLATFORM_PORTING.md)
- [Security Checklist](../starter-kit/templates/SECURITY_CHECKLIST.md)
- [Localization Checklist](../starter-kit/templates/LOCALIZATION_CHECKLIST.md)
- [Quality Metrics](../starter-kit/templates/QUALITY_METRICS.md)
- [Documentation Structure](../starter-kit/templates/DOCS_STRUCTURE.md)
- [Retrospective](../starter-kit/templates/RETROSPECTIVE.md)
- [User Guide](../starter-kit/templates/USER_GUIDE.md)
- [Micro-helper Profile](../starter-kit/templates/MICRO_HELPER_PROFILE.md)
- [UXP Engineering Checklist](../starter-kit/templates/UXP_ENGINEERING.md)
- [Host-independent Core / Testing Pyramid](../starter-kit/templates/HOST_INDEPENDENT_CORE_TESTING.md)
- [Standard Adoption / Baseline](../starter-kit/templates/STANDARD_ADOPTION.md)
- [Dependency / Security / SBOM Audit](../starter-kit/templates/DEPENDENCY_SECURITY_AUDIT.md)
- [Release Versioning / Changelog](../starter-kit/templates/RELEASE_VERSIONING.md)
- [Update Security](../starter-kit/templates/UPDATE_SECURITY.md)
- [Crash Diagnostics / Symbols](../starter-kit/templates/CRASH_DIAGNOSTICS.md)
- [Accessibility Checklist](../starter-kit/templates/ACCESSIBILITY_CHECKLIST.md)

### CI examples

- [GitHub Actions: starter-kit self-test](../.github/workflows/starter-kit-self-test.yml)
- [GitHub Actions: AE preflight](../starter-kit/examples/github-actions/ae-preflight.yml)
- [GitHub Actions: cross-platform macOS + Windows preflight](../starter-kit/examples/github-actions/cross-platform-preflight.yml)

Проект может использовать другие инструменты, если они обеспечивают эквивалентный или более сильный контроль.

При появлении в реальном AE-проекте удачного reusable script / test harness / release check необходимо после подтверждения рассмотреть его перенос в общий starter kit, чтобы следующие проекты не строили тот же механизм заново.

---

## 34. Версия стандарта и фиксация baseline

### Freshness внешних источников

Time-sensitive требования стандарта MUST ссылаться на канонический источник из [SOURCES.md](../SOURCES.md).

Для каждого такого источника фиксируются:

- URL;
- что именно он подтверждает;
- дата последней проверки;
- максимальный refresh interval.

Перед release самого стандарта stale source MUST быть перепроверен. Self-test стандарта должен блокировать release, если источник вышел за свой refresh interval.

Не переносить факт из старой версии Adobe/GitHub документации в текущий стандарт без повторной проверки, если он влияет на technology choice, compatibility, security или distribution.

Сам стандарт `AE-Development-Rules` должен иметь явную версию. Текущая версия хранится в [VERSION](../VERSION), история — в [CHANGELOG.md](../CHANGELOG.md).

Для значимого milestone / release AE-проекта фиксировать:

- версию стандарта;
- конкретный Git commit `AE-Development-Rules`;
- дату принятия baseline;
- проектные дополнения или отклонения, если они существуют.

Проект не обязан автоматически переходить на каждое изменение общего стандарта посреди release cycle.

Обновление baseline стандарта выполнять осознанно:

1. посмотреть изменения правил;
2. определить, какие новые требования применимы;
3. обновить проектную автоматизацию / документацию;
4. зафиксировать новый commit стандарта.

Для нового проекта использовать актуальную стабильную версию стандарта, если нет документированной причины выбрать другую.

Изменения самого стандарта версионировать по принципу:

- **major** — изменение MUST/MUST NOT, gate/status semantics или process contract, из-за которого ранее соответствующий проект может стать несоответствующим без изменения своего процесса;
- **minor** — новая backward-compatible capability, новый профиль для нового типа технологии, новый SHOULD/MAY или automation, не делающие ранее соответствующий проект несоответствующим;
- **patch** — уточнение, исправление формулировки/template/script/source metadata без изменения обязательного смысла.

Если есть сомнение между major и minor, выполнить compatibility analysis самого стандарта: «может ли существующий compliant project остаться compliant без изменений?». Если нет — major.

Версия стандарта не заменяет commit SHA: для воспроизводимости milestone хранить оба.

---

## 35. Dependencies, licenses, vulnerability audit и SBOM

Все сторонние зависимости, попадающие в production artifact или необходимые для его выполнения, должны быть известны.

Для release по применимости фиксировать:

- название и точную версию зависимости;
- источник;
- лицензию;
- способ pinning / lockfile;
- входит ли зависимость в distributable;
- известные обязательства по NOTICE / attribution / source offer;
- известные security advisories, относящиеся к используемой версии.

Не использовать dependency с несовместимой лицензией или известной критической уязвимостью без документированного решения.

Для package ecosystems использовать применимый vulnerability scanner, например ecosystem-native audit или эквивалент, но конкретный scanner не является частью обязательного стандарта.

Результат security audit должен различать:

- **PASS** — известных blocking advisories в проверенном scope нет;
- **FAIL** — найден blocking security issue;
- **BLOCKED** — audit source / scanner недоступен;
- **NOT RUN** — audit не выполнялся;
- **N/A** — внешних production dependencies нет или audit неприменим с объяснением.

Для dependency-heavy, multi-component или публично распространяемых продуктов рекомендуется формировать SBOM в стандартном машинно-читаемом формате, например CycloneDX или SPDX.

SBOM не заменяет vulnerability audit и license review.

Dependency update считать обычным production change: после обновления выполнить затронутые regression / compatibility / performance проверки.

---

## 36. Product versioning, changelog и migration contract

У продукта должен быть один authoritative source версии, из которого по возможности генерируются:

- bundle / executable metadata;
- About / Diagnostics;
- package / installer version;
- release record;
- user-visible version.

Не поддерживать несколько вручную редактируемых несвязанных version strings.

Для публичного продукта использовать предсказуемую versioning policy. SemVer рекомендуется, если его смысл соответствует продукту:

- **major** — пользовательски или project-data несовместимое изменение;
- **minor** — обратно совместимая новая функциональность;
- **patch** — обратно совместимое исправление.

Если используется другая схема, её смысл должен быть документирован.

Отдельно учитывать совместимость:

- parameter IDs / order / types;
- serialized project data;
- presets;
- saved settings;
- helper protocol;
- installer/update state.

Breaking project-file / preset / protocol change требует migration plan либо явного unsupported transition.

Для каждого публичного release вести changelog или release notes с минимумом:

- версия;
- дата;
- основные изменения;
- исправления;
- compatibility changes;
- migration notes;
- известные ограничения.

Changelog не является Evidence и не должен заявлять больше, чем подтверждено release record.

---

## 37. Безопасность обновления продукта

Если продукт умеет автоматически или полуавтоматически проверять, скачивать или устанавливать обновления, update path считается security-critical.

По применимости требуется:

- HTTPS или эквивалентный защищённый transport;
- проверка origin / endpoint;
- проверка подписи или криптографической целостности update artifact;
- защита от path traversal и подмены destination;
- запрет исполнения недоверенного downloaded content до успешной verification;
- version / compatibility validation;
- безопасное поведение при partial download;
- rollback / recovery plan при failed update;
- защита от downgrade, если downgrade создаёт известный security risk;
- отсутствие secrets / permanent credentials в client artifact.

Update metadata считать недоверенным входом до проверки.

Нельзя считать hash, полученный из того же недоверенного канала рядом с artifact, полноценным доказательством подлинности без защищённого trust mechanism.

Если обновление выполняется внешним installer / marketplace / package manager, документировать boundary ответственности и проверять собственную часть процесса.

---

## 38. Crash diagnostics, symbols и post-release debugging

Для native plugins, helpers и других crash-capable компонентов заранее определить, как диагностировать production crash.

По применимости сохранять для каждого release:

- точный Build ID;
- финальный binary hash;
- macOS dSYM;
- Windows PDB;
- map files или другие symbols, если используются;
- toolchain / optimization profile;
- связь symbols с конкретным artifact.

Symbols должны храниться так, чтобы их нельзя было перепутать между builds.

Не публиковать private symbols пользователю без необходимости.

Crash report / dump должен быть сопоставим с Build ID или другим однозначным identity.

При сборе crash diagnostics соблюдать privacy:

- не собирать содержимое пользовательского проекта без необходимости;
- не отправлять пользовательские файлы автоматически;
- удалять / редактировать secrets и чувствительные пути;
- явно описывать telemetry / crash upload, если он существует.

Исправление production crash должно по возможности включать:

1. symbolication;
2. воспроизводимый или минимальный failing case;
3. regression test;
4. проверку fix на идентифицированном artifact.

---

## 39. Accessibility и базовая доступность UI

Для инструментов с собственным UI учитывать доступность пропорционально типу интерфейса и возможностям используемой AE UI-технологии.

По применимости проверять:

- keyboard navigation;
- логичный focus order;
- видимый focus state;
- возможность выполнить основные действия без точного mouse-only interaction;
- достаточный contrast и различимость состояний;
- отсутствие передачи критического смысла только цветом;
- читаемость при HiDPI / scaling;
- resize без потери основных controls;
- понятные labels / tooltips для неоднозначных controls;
- достаточный hit target для интерактивных элементов;
- поведение при системных accessibility settings, если runtime позволяет их учитывать.

Не обещать screen-reader или другую accessibility support, которую конкретная AE UI-технология фактически не предоставляет или которая не была проверена.

Accessibility limitation должна быть честно указана, если она существенно влияет на использование продукта.

---

## 41. Host-independent core и testing pyramid

По возможности отделять чистую бизнес-логику от Adobe host boundary.

К host-independent core обычно относятся:

- математика / geometry;
- parsing / serialization;
- validation;
- deterministic state transitions;
- command planning;
- protocol schema;
- packing / layout algorithms;
- pure transformations данных;
- compatibility decision logic, не требующая реального host.

К host boundary относятся:

- After Effects DOM / AEGP / PF API;
- ExtendScript / CEP bridge;
- UXP host module;
- filesystem permissions;
- render buffers;
- panel lifecycle;
- native OS APIs.

### Основной принцип

Большинство быстрых тестов должны выполняться без запуска After Effects, а минимально необходимое число тестов должно подтверждать интеграцию с реальным host.

Рекомендуемая testing pyramid:

1. **Pure unit tests** — быстрые, детерминированные, без AE.
2. **Contract / adapter tests** — fake/mock host только для проверки собственного protocol / error handling.
3. **Integration tests** — packaging / bridge / serialization / filesystem boundaries.
4. **Runtime After Effects tests** — реальные host semantics.
5. **Release / compatibility tests** — финальный artifact и заявленные platform/version scenarios.

Mock / fake host не доказывает реальную семантику After Effects.

### ExtendScript

Для ExtendScript особенно полезно выносить чистую логику из JSX host calls.

Если pure logic тестируется в Node/Jest/Vitest/`node:test` или другой внешней среде:

- тестировать тот же source/сгенерированный artifact, а не вручную переписанную копию алгоритма;
- учитывать, что ExtendScript имеет более старую JavaScript semantics;
- если используется transpilation, отдельно проверять полученный ExtendScript artifact;
- реальные host calls, Undo, selection, project mutation и serialization всё равно проверять внутри AE.

### UXP / CEP

Для UXP / CEP UI/controller code отделять:

- pure state / validation / protocol;
- transport / bridge;
- host adapter;
- view.

Async state machine по возможности тестировать вне AE с controlled fake transport, а затем закрывать реальным host integration test.

### Native plugins

Для C/C++/Rust native effects отделять:

- pure math / sampling / geometry;
- pixel algorithms;
- serialization;
- host adapter / SDK callbacks;
- GPU backend.

Pure algorithms должны иметь unit/property/fuzz tests, если риск это оправдывает.

Host-specific correctness — buffer ownership, suites, MFR, SmartFX, color management, render lifecycle — подтверждать отдельными AE tests.

### Требование к архитектуре

Не создавать abstraction layer только ради тестов, если она сложнее самой задачи.

Для micro-helper допустим прямой host script без отдельного core, если логика тривиальна и покрыта минимальным профилем.

Цель separation — сделать сложную логику дешёвой для тестирования, а не искусственно увеличить количество файлов и классов.

---

# Главное правило

**Пользователь — последний источник validation в своей реальной среде, а не замена внутреннему QA и диагностике.**

Перед любой передачей разработчик обязан подтвердить, что:

1. Цель передачи определена: Validation Build или Release Candidate.
2. Передаётся текущий идентифицированный artifact.
3. Проверен именно этот artifact в обязательном для текущего gate scope.
4. Для Validation Build пройден Validation Gate; для release — полный применимый Release Gate.
5. Evidence соответствует заявленным выводам.
6. Известные ограничения сообщены честно.
7. Автоматизация не повредила пользовательские данные и окружение.

До пользовательской validation должны быть исчерпаны разумные доступные технические способы проверки **её заявленного scope**. Это не означает автоматическое выполнение release-only ceremony до каждого пользовательского теста.

Цель процесса — не обещать невозможное отсутствие любых ошибок, а не передавать пользователю проблемы, которые должны были быть обнаружены предусмотренными для текущего gate инженерными проверками.

**Написанный код — не то же самое, что проверенный продукт.  
Успешная сборка — не то же самое, что корректная работа.  
Проверенная версия — не то же самое, что любая следующая сборка.  
Передавать нужно именно тот artifact, для которого есть актуальные доказательства.**

