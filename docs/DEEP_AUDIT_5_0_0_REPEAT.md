# Повторный глубокий аудит правил версии 5.0.0

Аудит выполнен 2026-10-02 для опубликованного baseline `8d88b19afea726b7c79988c5f6958f65d13995ba`. Предыдущие четыре замечания и четыре предложения сохранены в [журнале](DEEP_AUDIT_BACKLOG.md). Повторные изолированные проверки подтвердили D01–D04; обнаружены три дополнительных дефекта инструментов D05–D07. Новых критических противоречий нормативного текста в проверенном scope не обнаружено.

Это аудит и фиксация результатов. Canonical requirements, VERSION, main и опубликованный тег не изменялись. Новая ветка содержит только документацию и redacted Evidence. Исправление, merge, новая версия и релиз не входят в этот проход.

## Проверенный scope

Перечитаны Smart Entry, нормативный индекс, Process Core, Engineering Core, все technology profiles, Reference Audit, Product Discovery и Workflow; сопоставлены требования с шаблонами discovery, identity, safety, acceptance, migration и передачи результата. Проверены manifest, registry, schemas, routing, artifact/Evidence tools, AI fixture inspector и применимые проверки целостности. Исторические remediation records не трактовались как текущие открытые дефекты.

Свежая inventory сверка всех 116 tracked файлов показала 700621 байт и ноль отличий от предыдущего аудита baseline. В публичном origin/main и теге 5.0.0 сохранён тот же SHA. Изменения этого прохода — дополнительные audit documents, а не изменение проверенных runtime scripts. Это не повторная загрузка release archives и не новый CI-прогон ветки.

Повторно прочитаны первичные Adobe guides по [UXP lifecycle](https://developer.adobe.com/uxp/guides/explanation/concepts/entrypoints/) и [packaging](https://developer.adobe.com/uxp/guides/how-to/distribution/package/). Проверенные ограниченные claims профиля согласуются с этими страницами. Остальные source checks и vendor provenance из предыдущего аудита сохранены как прежнее Evidence; даты SOURCES.md не обновлялись без новой проверки каждого источника.

## D05 Отсутствующие определения модулей не блокируют routing и self test

**P2, CONFIRMED, OPEN.** Связанные требования: ROUTE-001, API-SOURCE-001, Engineering §33 и §34.

В изолированном клоне последовательно удалены определения `DEBUGGING`, `API-SOURCES`, `PRODUCT-DISCOVERY` из `rule_groups`, затем все три вместе. `loadManifest()` принимает каждую изменённую конфигурацию. `route()` возвращает соответствующие IDs, хотя получить их canonical source/section из принятого manifest уже нельзя. При удалении всех трёх полный локальный self-test завершился exit 0: `PASS (116 files checked)`.

Причина: [loadManifest, строки 36–38](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/lib/applicability.mjs#L36) проверяет ссылки только из artifact profiles. [Task overlays, строки 71–72](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/lib/applicability.mjs#L71) добавляют IDs отдельно и не проверяют наличие определений. Tests проверяют наличие строк в результате, но не их разрешимость в manifest.

**Влияние и граница:** повреждение manifest при будущем редактировании может пройти существующий gate и сломать карту чтения для ИИ. В опубликованном manifest все три определения есть: контроль 315 обычных сочетаний task/component/risk/delivery не нашёл undefined IDs. Это дефект проверки отрицательного входа, а не утверждение, что текущий normal routing уже возвращает несуществующие определения. D01 остаётся отдельным вопросом достаточности выбранных применимых модулей.

**Исправление:** проверять определения всех фиксированных overlays и каждый возвращаемый ID. Проверка должна связывать ожидаемый смысл с canonical source/section, а не только принимать любое определение с подходящим именем. Не добавлять универсальный новый процесс разработки.

**Приёмка:** missing/renamed/wrong-source определения блокируются; обычные bugfix/research/discovery пути и пропорциональный documentation scope продолжают работать. Полный self-test не принимает ту же испорченную конфигурацию.

## D06 Canonical source может находиться вне принятого checkout

**P3, CONFIRMED, OPEN.** Связанные требования: AI-STATE-001, Engineering §34 и existing canonical source boundary.

В отдельном клоне `core/PROCESS.md` заменён symlink на созданный аудитом файл вне checkout. Ссылка зафиксирована в собственном синтетическом commit. После изменения содержимого внешнего файла `git status --porcelain` остаётся пустым, SHA checkout прежний, но читаемый source hash меняется. `loadManifest()` принимает этот источник; map generator с `--check` сообщает PASS.

Причина: [строки 26–28](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/lib/applicability.mjs#L26) проверяют lexical `path.resolve()` через `startsWith`, затем чтение следует symlink. Реальная цель не проверяется против canonical root.

**Влияние и граница:** consumer, использующий этот loader/generator отдельно, может читать правила, чьи байты не определяются принятым commit. На опубликованном baseline все tracked файлы обычные; фактической подмены не обнаружено. Контроль с обычным `../external-process.md` правильно отвергается. AI fixture preparation также уже отвергает linked standard source с `unsafe standard source file`; не заявляется обход этого контроля или всего полного self-test.

**Исправление:** проверять canonical boundary через realpath и определить политику symlinks/ancestors; для immutable canonical sources проще запрещать ссылки. Учитывать обычный canonicalized checkout root, чтобы не ломать допустимые системные aliases.

**Приёмка:** external source link и link в ancestor отвергаются loader и generator до принятия manifest; обычные источники работают; существующая защита подготовки AI fixtures сохраняется. Тесты не требуют доступа к чужим файлам.

## D07 Проверка modes не учитывает специальные POSIX bits

**P3, CONFIRMED, OPEN.** Связанное требование: ART-001 и заявленный tooling scope modes.

Для принадлежащего аудиту каталога создан artifact record при mode `0770`. Затем установлен mode `01770`; фактический stat подтверждает изменение. `verify-artifact.mjs` завершился exit 0 и заявил, что entries/contents/modes совпадают. Это CLI-проба на macOS с Node 24.13.1, без запуска payload или повышения привилегий.

Причина: [files.mjs, строка 33](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/lib/files.mjs#L33) сохраняет только `stat.mode & 0o777`. Изменившийся специальный bit исчезает из manifest. [Формулировка verifier, строка 11](https://github.com/ios3kov/AE-Development-Rules/blob/8d88b19afea726b7c79988c5f6958f65d13995ba/starter-kit/scripts/verify-artifact.mjs#L11) не поясняет этот более узкий scope.

**Влияние и граница:** limited mode comparison нельзя трактовать как сохранение всех POSIX mode bits. Обычное изменение `0644 → 0755` уже обнаруживается существующими regressions. Не проверялись ACL, ownership, extended attributes, Linux/Windows semantics или действие этих прав между разными пользователями. В пробах установка setuid/setgid на data file фактически не сохранилась; эти попытки не считаются воспроизведённой потерей setuid/setgid контроля.

[Node 22 documentation](https://nodejs.org/docs/latest-v22.x/api/fs.html#file-modes) предупреждает, что значения mode выше `0777` имеют платформенные ограничения. Поэтому исправление должно явно определить поддерживаемый scope, а не обещать переносимость всех POSIX прав на Windows.

**Исправление:** связывать значимые специальные bits для поддерживаемой платформы либо отвергать такой input/сузить сообщение PASS и описать неподтверждённую metadata область. При расширении manifest определить совместимость старых records; не переписывать старое Evidence как более полное.

**Приёмка:** фактически сохранённое изменение специального bit обнаруживается или явно исключено из заявленного результата; обычные files/content/executable-mode/link cases не ослаблены; unsupported platform case честно отмечен.

## Проверки и ограничения

- Повторные исходные probes подтвердили D01–D04; stapling проверялся безопасными stubs, без настоящей notarization.
- Новый missing-overlay counterexample дважды дал полный self-test PASS в изолированном изменённом клоне. Это положительное Evidence дефекта проверки, а не исправление.
- Локальный self-test текущих scripts прошёл доступные Node/POSIX/macOS checks: smoke PASS, hardening 13 PASS и 2 Windows-only skipped, contracts 8 PASS, followup 9 PASS. Финальная проверка audit documents выполняется тем же self-test; точный verification record сохраняется вместе с результатами.
- Static code scanner: exit 0, no findings in scanned scope, release_readiness not_assessed. Он не обнаруживает описанные semantic counterexamples.
- Actual model behavior, AE product runtime и локальный PowerShell/Windows runtime: NOT RUN. Предыдущий exact-baseline CI не заменяет новый CI изменённой audit ветки.

[Redacted Evidence](evidence/deep-v5-repeat-probes.json) содержит observations, controls, source identity и границы проверок. Полные локальные logs/probes сохранены отдельно от стандартного checkout. Журнал теперь содержит **7 открытых замечаний и 4 отдельных предложения**. Не делать из этого числа обещание отсутствия остальных ошибок.

## Следующее исправление

Сначала закрыть D01 и D05: достаточность карты чтения и целостность её определений. Затем исправить D02–D04, D06–D07 с focused negative checks и совместимостью форматов. I01–I04 остаются предложениями, а фактическая оценка выбранного ИИ — отдельным Evidence scope. Изменение новых MUST и процесса требует compatibility analysis по §34; опубликованный 5.0.0 не перемещается.
