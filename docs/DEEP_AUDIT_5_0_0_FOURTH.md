# Четвёртый глубокий аудит правил версии 5.0.0

Аудит выполнен 2026-10-02. Прежние восемь замечаний и четыре предложения сохранены. Подтверждены два дополнительных дефекта инструментов: слабая проверка согласованности версии и некорректная проверка уникальности JSON объектов. Новых серьёзных противоречий нормативного текста в проверенных взаимодействиях не обнаружено.

Опубликованный baseline: `8d88b19afea726b7c79988c5f6958f65d13995ba`, версия 5.0.0. Начальная audit revision: `2f8f06790bfe2c912831391d4135693e40efb57c`, clean Git state. Свежий fetch подтвердил прежний SHA origin/main и v5.0.0. Этот проход добавляет документацию и Evidence в существующую отдельную локальную audit ветку; правила, scripts, VERSION, main и релиз не изменялись.

## Проверенный объём

Свежая сверка всех 121 tracked файлов начальной audit revision: 762324 байт, все обычные файлы. По сравнению с исходным опубликованным inventory изменён только README с audit link и добавлены пять audit document/evidence файлов. Нормативные источники и исполняемые scripts совпадают с ранее проверенным baseline.

Повторно сопоставлены Smart Entry, task state и разрешения, пропорциональность Risk/Delivery, micro-helper eligibility, Validation/Release templates, Stage 0 и Reference Audit exit criteria, traceability, Undo/state/lifecycle, Unicode, update/privacy и baseline versioning. Проверены manifest/schema/routing, snapshot/record/inspector, parser/preflight и platform/dependency collectors. Различия между обязательным правилом, optional template и ограниченной проверкой инструмента учитывались отдельно. Предыдущий полный аудит остаётся исходным inventory; этот проход углубляет взаимодействия и отрицательные входы, а не выдаёт исторические observations за новые прогоны.

Изолированные пробы: шесть собственных локальных копий стандарта для version cases, двенадцать JSON CLI inputs с неизвестными полями и три JSON CLI records с Evidence duplicates. Ни After Effects, ни модель ИИ не запускались. Установка, публикация, смена tag и реальные platform distribution checks не выполнялись. SOURCES.md не обновлялся; все прежние vendor checks остаются датированным Evidence.

## D09 Проверка версии пропускает неправильный baseline

**P3, CONFIRMED, OPEN.** Затронуты Engineering §34 и существующая проверка версии self-test; CONTRIBUTING требует согласованности VERSION, CHANGELOG и README перед публикацией.

В отдельных owned clones полный `self-test.mjs --dry-run --require-posix` дал следующие результаты. Runtime scripts во всех копиях одинаковы; изменены только указанные version documents.

| Случай | VERSION | Стабильная версия в README | Результат self-test |
| --- | --- | --- | --- |
| Неизменённый контроль | 5.0.0 | v5.0.0 | PASS, exit 0 |
| Все README occurrences заменены на prerelease | 5.0.0 | v5.0.0-rc.1 | PASS, exit 0 |
| Только baseline declaration заменён; release link остался v5.0.0 | 5.0.0 | v5.0.1 | PASS, exit 0 |
| VERSION и README заменены на leading-zero version | 05.0.0 | v05.0.0 | PASS, exit 0 |
| Все README occurrences заменены на другую версию | 5.0.0 | v6.0.0 | FAIL, exit 1 |
| VERSION без patch component | 5.0 | v5.0 | FAIL, exit 1 |

Каждый PASS проверил 121 файл доступным локальным subset. Это воспроизведение недостаточности проверки, а не успешная приёмка этих повреждённых копий.

Причина: [self-test.mjs, строки 84–89](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/self-test.mjs#L84) использует три группы цифр для SemVer и `readme.includes('v' + version)` для baseline. Поиск подстроки принимает prerelease suffix или постороннюю ссылку вместо authoritative declaration. Regex допускает leading zero; [SemVer 2.0.0, пункт 2](https://semver.org/#spec-item-2) запрещает его в normal version.

**Влияние:** будущая ошибка version metadata может пройти этот self-test и ввести потребителя правил в заблуждение. На опубликованном baseline VERSION и README согласованы; фактического ошибочного release этим проходом не обнаружено. Self-test не публикует продукт и не заменяет release review; поэтому это P3, а не подтверждение обхода всех требований публикации. D05 касается определений routing, а D09 — другой проверки целостности.

**Исправление и приёмка:** сравнивать VERSION с полным version field актуального README baseline и применимым current release link; не принимать любое вхождение в документе. Для поддерживаемого normal version запретить leading zeros. Все три воспроизведённые ошибки должны блокироваться, обычный 5.0.0 и обе отрицательные контрольные пробы сохраняют ожидаемое поведение. Возможную поддержку prerelease определить явно; это не требование менять продуктовую versioning policy каждого AE-проекта. Изменения правил классификации major/minor/patch не требуются для устранения этого дефекта инструмента.

## D10 Перестановка полей скрывает duplicate Evidence

**P3, CONFIRMED, OPEN.** Затронуты optional project-record schema, EVD-001 и существующее обещание strict schema validation.

В одном check указаны два объекта с одним и тем же `path` и `sha256`. Во втором объекте порядок полей изменён:

```json
[
  { "path": "duplicate-evidence.txt", "sha256": "5eee0c524ce3d768836b7538fe00d810743f71f30d105000ec62781c46fd4416" },
  { "sha256": "5eee0c524ce3d768836b7538fe00d810743f71f30d105000ec62781c46fd4416", "path": "duplicate-evidence.txt" }
]
```

Это обычный сериализованный JSON. Owned Evidence file существует, его hash совпадает. `validate-project-record.mjs` заканчивается exit 0: recorded_policy PASS, release_readiness NOT_ASSESSED. Контроль с одним объектом также PASS. Два одинаковых объекта с одинаковым порядком полей правильно отвергаются, exit 2, `duplicate item`.

Причина: [schema.mjs, строка 17](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/lib/schema.mjs#L17) сравнивает `JSON.stringify()` каждого item. Порядок object properties влияет на сериализованную строку. Но [JSON Schema 2020-12 Instance Equality §4.2.2](https://json-schema.org/draft/2020-12/json-schema-core#section-4.2.2) считает object properties неупорядоченными, а [uniqueItems §6.4.3](https://json-schema.org/draft/2020-12/json-schema-validation#section-6.4.3) требует уникальности всех элементов. [Project-record schema](../starter-kit/schemas/project-record.schema.json) явно включает uniqueItems для Evidence.

**Влияние:** validator не полностью выполняет собственную объявленную JSON Schema semantics; форматирование меняет результат проверки одних и тех же значений. Дубликат не становится вторым независимым доказательством. При этом проверка фактических hashes не обходится, количество check IDs не увеличивается, разрешения и runtime результаты не подтверждаются. D03 касается sparse/inherited arrays в direct-JS API; D10 имеет другой механизм и воспроизводится через JSON CLI.

**Исправление и приёмка:** использовать структурное JSON equality или корректную bounded canonicalization с сортировкой object keys на всех уровнях и сохранением array order. Оба варианта duplicate Evidence должны отвергаться; один item и действительно разные items остаются допустимыми. Проверить nested object cases, обычные primitive duplicates и существующие защиты unknown fields/dense arrays. Не ослаблять hash/revision checks и не переписывать исторические records как более полные доказательства. Исправление не применялось.

## Неподтвердившиеся гипотезы и границы

Все двенадцать вариантов неизвестных полей `unexpected`, `constructor`, `toString`, `__proto__` в root/candidate/check отвергнуты JSON CLI, exit 2. Имеющаяся own-property защита работает; старый исправленный дефект не переоткрывается.

Micro-helper допускает соразмерный процесс, но public delivery сохраняет применимый Release Gate. Stage 0/Reference Audit позволяют продолжать независимый определённый scope, сохраняя блокировку зависимого решения при critical unknown. Templates не дают разрешения на host mutation или publication. Нового противоречия по этим проверенным взаимодействиям не зарегистрировано. Пробелы в выборе модулей уже покрыты D01, неизвестный результат IPC mutation — предложением I01.

D01–D08 остаются OPEN; их reproductions сохранены в предыдущих records и не объявляются повторно выполненными в этом проходе. I01–I04 остаются отдельными предложениями.

## Итоговая проверка и следующий шаг

Static code scanner начальной audit revision: exit 0, no findings in scanned scope; 111 text files, 735928 байт, release_readiness not_assessed. Он не обнаруживает D09/D10 и не аттестует полноту правил.

После добавления audit documents локальный self-test прошёл доступный Node/POSIX/macOS subset. Две Windows-only проверки пропущены, PowerShell runtime NOT RUN. Точная итоговая revision и hash полного log сохраняются в отдельном verification record вне standard checkout. Новый CI этой ветки и actual AI/AE runtime: NOT RUN.

[Журнал](DEEP_AUDIT_BACKLOG.md) содержит **10 открытых замечаний и 4 предложения**. [Redacted Evidence](evidence/deep-v5-fourth-probes.json) сохраняет observations, inputs, hashes и controls; старые отчёты не изменены. Первым исправлять D01/D05, затем остальные focused tooling defects. Этот аудит не изменяет опубликованный baseline и не закрывает ни один неисправленный пункт.
