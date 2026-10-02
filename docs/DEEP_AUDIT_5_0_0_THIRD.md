# Третий глубокий аудит правил версии 5.0.0

Аудит выполнен 2026-10-02. Прежние D01–D07 и I01–I04 сохранены в [журнале замечаний](DEEP_AUDIT_BACKLOG.md). Подтверждён один новый дефект вспомогательного API scanner: корректный исходник с символом U+FFFD ошибочно отвергается. Новых серьёзных противоречий нормативного текста в проверенных взаимодействиях не обнаружено. Отсутствие находки не является доказательством отсутствия других ошибок.

Проверяемый опубликованный baseline: `8d88b19afea726b7c79988c5f6958f65d13995ba`, версия 5.0.0. Начальная audit revision: `cdfef14f27538458e6c20da70198b03c7117eb3b`, clean Git state. Работа выполнена в существующей отдельной локальной audit ветке. Этот проход фиксирует результаты; правила, scripts, VERSION, main и опубликованный тег не изменялись.

## Что проверено

Третий проход использует предыдущий полный аудит неизменённого baseline и углубляет проверку взаимодействий. Свежая сверка всех 119 tracked файлов начальной audit revision: 738960 байт, все обычные файлы. По сравнению с первым опубликованным inventory отличаются только README с audit link и три добавленных audit document/evidence файла; изменений нормативных источников или исполняемых scripts нет. Fresh fetch подтвердил прежний SHA origin/main и v5.0.0. Старые отчёты и Evidence сохранены без переписывания.

Повторно сопоставлены Validation/Release Gate, project-record evaluator/schema, Build Identity, Evidence lifecycle, AI task state/resume, trust/permission boundaries, runtime test ownership и IPC/Undo/repeated execution. Проверен UTF-8 input path API scanner. Изолированные probes выполнялись в принадлежащем аудиту workspace вне standard checkout, без запуска After Effects, установки пакетов или передачи реального test build пользователю.

Это целевой повторный проход по границам и отрицательным входам, а не новая построчная аттестация каждого исторического документа, повторная проверка каждого Adobe/Apple/Microsoft источника или actual model evaluation. SOURCES.md не обновлялся.

## D08 Корректный символ Unicode принимается за повреждение кодировки

**P3, CONFIRMED, OPEN.** Затронуты API-SOURCE-001, Engineering §33 и API inventory tooling; дефект не меняет обязательный API-source contract.

В собственном `source.cpp` содержатся две строки:

```cpp
int PF_Cmd_RENDER = 0;
const char* marker = "�";
```

Имя переменной здесь синтетическое, а не вызов Adobe SDK. Символ внутри string literal — настоящий U+FFFD, байты UTF-8 `EF BF BD`. SHA-256 всего файла: `d57e00a8773b4c74fa9717e861d555dc9e673d31f68b5a70f744949752be2a28`.

Строгое декодирование `new TextDecoder('utf-8', { fatal: true }).decode(bytes)` успешно. Apple clang 21.0.0 с `-fsyntax-only` принимает исходник, exit 0. При этом штатный `scan-adobe-api.mjs SOURCE_DIR NEW_OUTPUT_DIR` заканчивается exit 2: `INCOMPLETE: non UTF-8 candidate`.

Причина: [scan-adobe-api.mjs, строки 18–19](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/scan-adobe-api.mjs#L18) после обычного UTF-8 decoding ищет U+FFFD в готовом тексте. Наличие этого символа не различает подстановку decoder при ошибке и корректно закодированный буквальный символ. [WHATWG Encoding Standard](https://encoding.spec.whatwg.org/#interface-textdecoder) определяет fatal decoding, при котором ошибка входных bytes приводит к исключению; это подходящая граница для проверки кодировки.

**Контроли:** ASCII и кириллический string literal дают Collection COMPLETE, exit 0. Файл с действительно недопустимым UTF-8 byte `FF` в comment отвергается и fatal decoder, и scanner, exit 2. Clang принимает этот comment: compiler syntax result сам по себе не используется как доказательство валидности UTF-8.

**Влияние:** допустимый source может необоснованно остановить сбор API inventory и потребовать ручного обхода. Это узкое ложное отклонение, а не ложный PASS, нарушение безопасности AE или доказательство неправильной работы ИИ. В опубликованном standard source фактического повреждения кодировки этим тестом не обнаружено. Лексический scanner не устанавливает корректность Adobe API или runtime совместимость.

**Исправление:** проверять исходные bytes строгим decoder, затем использовать decoded text для лексического поиска. Не заменять некорректные bytes молча; сохранить исходный byte hash и определить поведение BOM. Не запрещать допустимый символ только из-за его внешнего вида.

**Приёмка:** ASCII, кириллица и буквальный U+FFFD принимаются; malformed UTF-8 отвергается до Collection COMPLETE. Inventory hashes относятся к исходным bytes; ограничения scope, oversized input и безопасные source/output boundaries не ослаблены. Исправление в этом audit не применялось.

## Гипотезы, которые не стали замечаниями

**Переводы строк в identity.** Для standard.commit, candidate.commit и candidate.sha256 проверено по пять суффиксов: LF, CR, CRLF, U+2028, U+2029. Все 15 JSON CLI inputs отвергнуты как invalid pattern, exit 2. Контроль без добавленного суффикса даёт recorded_policy PASS и release_readiness NOT_ASSESSED. Ошибка сравнения со stale check identity исключена: dependent check fields менялись вместе с candidate.

JavaScript `$` без multiline flag требует конец input, что согласуется с [ECMAScript CompileAssertion](https://tc39.es/ecma262/multipage/text-processing.html#sec-runtime-semantics-compileassertion). Здесь нельзя переносить поведение regex другого языка на JavaScript. Нового дефекта identity не зарегистрировано.

**Фазы и статусы gate.** Проверено 240 сочетаний: 3 delivery × 4 phase (legacy/pre-handoff/user-validation/release-acceptance) × 5 status × required/optional × CLEAN/DIRTY. Расхождений с отдельно сформулированной ожидаемой declared policy не найдено. Каждый fixture сохранял обязательный pre-handoff prerequisite; PASS имел реальный owned Evidence file с проверенным hash, N/A — substantive synthetic reason.

Это проверка типизированной заявленной политики. Она не доказывает правильность выбранных project checks, обоснованность N/A в реальном проекте, безопасную классификацию user-validation, полноту prerequisites или фактическую release readiness. Существующие требования запрещают переносить доступную внутреннюю проверку в user-validation ради обхода gate. Новый дефект по этой матрице не зарегистрирован.

**Прежние замечания.** D01–D07 не исправлены и не закрыты. Их reproductions и ограничения остаются в предыдущих records; этот проход не выдаёт сохранённые старые observations за новые прогоны. I01 про неизвестный результат IPC mutation остаётся отдельным предложением, а не новым подтверждённым нарушением.

## Проверки и следующий шаг

Static code scanner: exit 0, no findings in scanned scope; 109 text files, 712564 байт начальной audit revision, release_readiness not_assessed. Этот scanner не обнаруживает D08 и не аттестует смысл правил.

После сохранения новых audit documents локальный self-test прошёл доступный Node/POSIX/macOS subset. Две Windows-only проверки пропущены; PowerShell runtime локально NOT RUN. Полный log и точная итоговая audit revision сохраняются отдельным verification record вне standard checkout. Прежний baseline CI не объявляется CI новой ветки.

Actual AI behavior и AE runtime: **NOT RUN**. Никакой новой гарантии «всё без ошибок» или оценки 10/10 этот проход не даёт.

[Redacted Evidence](evidence/deep-v5-third-probes.json) содержит source bytes, hashes, observations, controls, environment и coverage limits. Журнал теперь содержит **8 открытых замечаний и 4 предложения**. Следующий практический шаг — исправить D01/D05, затем D02–D04/D06–D08 с focused regressions; новый аудит не заменяет закрытие уже подтверждённых пунктов. Canonical MUST changes требуют compatibility analysis, а опубликованный 5.0.0 сохраняется неизменным.
