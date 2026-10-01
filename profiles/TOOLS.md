# Tools / Panels Runtime Profile

Общие runtime-требования для scripts, ScriptUI, CEP, UXP и helper/controller инструментов.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 22. Дополнительные проверки Scripts / Panels / Tools

### Lifecycle

- первый запуск;
- повторный запуск;
- закрытие;
- повторное открытие;
- reload extension;
- restart After Effects;
- восстановление состояния;
- корректное завершение helpers.

### UI

- responsiveness;
- resize;
- scaling;
- HiDPI / Retina;
- маленькие размеры панели;
- отсутствие accidental double-actions;
- состояние UI во время длительной операции;
- доступность отмены, если предусмотрена.

### After Effects Integration

- правильный project / composition;
- отсутствие composition;
- отсутствие selection;
- неправильный тип selection;
- удалённые или изменённые layers / items;
- locked layers;
- missing footage / files;
- изменение контекста пользователем;
- отмена операции;
- повтор после ошибки.

### Undo Safety

Операция с `app.beginUndoGroup()` должна обеспечивать корректное закрытие успешно открытой группы при обычном выполнении, exception и раннем выходе.

Для синхронных операций использовать `try ... finally`, где `app.endUndoGroup()` вызывается в `finally`.

Не предполагать, что:

- закрытие Undo Group автоматически откатывает частично выполненную операцию;
- Undo Group можно безопасно держать открытой между произвольными asynchronous callbacks;
- все host / filesystem / helper операции поддерживают Undo.

Поведение при частичном выполнении должно быть определено.

Проверять:

- exception внутри группы;
- early return;
- отмену;
- Undo;
- Redo;
- несколько последовательных операций;
- повторный запуск после ошибки.

Аварийное завершение процесса не может обрабатываться как обычный `finally`; связанные риски состояния проверять отдельно.

### State

- preferences;
- saved state;
- corrupted state;
- migration;
- reset;
- совместимость схемы настроек;
- безопасное поведение при неизвестной версии состояния.

### Repeated Execution

Операция должна корректно работать:

- первый раз;
- второй раз;
- много раз подряд.

Не оставлять:

- duplicate listeners;
- duplicate UI;
- zombie state;
- лишние timers;
- потерянные callbacks;
- orphaned background processes.

### File System

Проверять:

- отсутствующие файлы;
- read-only locations;
- permissions;
- длинные пути;
- пробелы;
- Unicode и кириллицу;
- специальные символы;
- частичную запись;
- ошибку диска;
- отмену file dialog;
- применимые sandbox restrictions.

Где важна целостность данных, использовать безопасную стратегию записи и восстановления.

### Debugging by runtime

Общий процесс расследования определён в [Engineering Core §16](../core/ENGINEERING.md). Для tools/panels дополнительно SHOULD локализовать ошибку по runtime boundary.

#### ExtendScript / ScriptUI

По возможности фиксировать:

- message / error number;
- file и line;
- доступную stack information;
- текущий project/comp/selection context;
- состояние Undo Group;
- входные arguments / IDs без чувствительных пользовательских данных.

Не скрывать исходный exception общим `catch`, если после этого теряется причина сбоя. Если exception преобразуется в пользовательскую ошибку, диагностический Evidence SHOULD сохранять исходную техническую причину.

#### CEP

Разделять как минимум:

1. panel/browser JavaScript;
2. CEP ↔ ExtendScript bridge;
3. host-side ExtendScript;
4. helper/network/backend, если используется.

Для async/bridge операций SHOULD использовать correlation/request ID, чтобы связать panel log, bridge request, host result и helper response одного действия.

Ошибка panel JavaScript не является доказательством ошибки JSX; bridge timeout не является доказательством host crash; успешный callback не доказывает корректность host-side результата без проверки payload/contract.

#### UXP

Дополнительно проверять:

- rejected Promise и место его обработки;
- stale host context после `await`;
- permission/sandbox failure;
- lifecycle entrypoint;
- concurrent invocation / stale operation;
- host API `Min Version` и фактическую версию AE.

Browser-like stack или JavaScript exception не следует трактовать как доказательство browser runtime semantics.

#### Helper / IPC

Связывать обе стороны операции через correlation ID и проверять:

- request/response schema;
- timeout/cancellation;
- process identity/version;
- stderr/stdout или structured logs;
- partial response;
- disconnect/restart;
- protocol-version mismatch.

---


