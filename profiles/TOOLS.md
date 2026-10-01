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

---

