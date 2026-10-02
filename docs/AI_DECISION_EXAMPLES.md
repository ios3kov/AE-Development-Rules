# Короткие примеры решений для ИИ

Guidance для рабочей версии **5.1.0**, не опубликованный release и не результат исполнения модели. Source links ниже указывают canonical требования в том же checkout; exact commit и hashes примеров связываются с итоговым verification record. При копировании зафиксировать именно используемый commit. Примеры не заменяют Product Spec, выбранные SDK headers и реальные host проверки.

## 1. Локальный JSX bugfix: Undo и частичный сбой

**Запрос:** «Переименование падает на locked layer, исправь». Подтверждено: менять только имя выбранного слоя, сохранить параметры/проект. Иллюстративный target: AE 2025, ExtendScript, macOS; target SDK/API source revision ещё не выбрана, поэтому конкретную host compatibility не объявлять VERIFIED.

**Решение:** bugfix, JSX; подключить DEBUGGING/API-SOURCES и TOOL-RUNTIME. Малый script может остаться Light только при bounded Undo-safe mutation и соответствии [micro-helper eligibility](../starter-kit/templates/MICRO_HELPER_PROFILE.md); частичный data-loss риск требует повышения. До реализации проверить применимый API contract по [Process §3](../core/PROCESS.md#3-research-перед-разработкой). По [Tools Undo Safety](../profiles/TOOLS.md#undo-safety) закрывать успешно открытую группу при exception/early return, определить partial result, не считать закрытие rollback.

**Что проверить:** ordinary rename, missing selection, exception после частичного изменения, Undo/Redo/repeated execution по scope. Parser/mock tests подтверждают свой ограниченный сценарий. Реальный AE smoke/Undo остаётся NOT RUN до исполнения на точном target. Наличие удачного теста не разрешает менять пользовательский открытый проект без соответствующего ownership/permission.

## 2. IPC helper: ответ потерян после применения

**Запрос:** «После timeout операция продублировалась». Подтверждено: одна пользовательская команда должна иметь один логический эффект. Иллюстративный target: CEP → helper → AE 2025; protocol/session revision пока UNKNOWN. Не выдумывать host API, delivery guarantee или deduplication window.

**Решение:** bugfix, mixed `cep`/`helper`, feature `ipc`; риск определяется mutation/data-loss областью. [Helper / IPC](../profiles/TOOLS.md#helper--ipc) требует correlation/protocol/lifecycle диагностику. При неизвестном исходе использовать [recovery guidance](../profiles/TOOLS.md#неизвестный-результат-ipc-mutation): спросить статус той же операции или проверить состояние в разрешённой области, затем выбрать доказанно безопасный retry/deduplication. Новый request ID после timeout не доказывает отсутствие первого эффекта.

**Что проверить:** apply-before-response-loss, reject-before-apply, session restart, changed payload with reused key, cancellation/partial result. Mock transport не доказывает атомарность AE. Если статус/владение состоянием неизвестны, зависимый retry BLOCKED; независимая диагностика продолжается. Publish/kill/cleanup не следуют из «исправь».

## 3. Native render: отмена и реально загруженная сборка

**Запрос:** «Исправь cleanup при отмене рендера». Подтверждено: сохранить alpha/parameter/state contracts и не затрагивать чужой render. Иллюстративный target: AE 2025 native effect, CPU RGBA32F; SDK/header revision, OS и применимость MFR должны быть установлены из проекта до нового host вызова.

**Решение:** native, Critical по render/memory ownership риску, Development до ограниченной передачи. По [Native §23](../profiles/NATIVE.md#23-дополнительные-проверки-native-effects--render-plugins) проверить ownership, checkout/checkin, error/cancel cleanup и повторный render в заявленном context. [Process identity](../core/PROCESS.md#7-build--artifact-identity) связывает Evidence с candidate; файл на диске не доказывает, что AE загрузил эту сборку. Не считать поддержкой MFR один выставленный flag.

**Что проверить:** отмена до/после получения ресурсов, однократное освобождение принадлежащих операции ресурсов, сохранение чужих handles/state, numerical output по выбранной tolerance и повторный render. Standalone tests могут подтвердить core/lifecycle model. [AE runtime safety](../starter-kit/templates/AE_RUNTIME_TEST_SAFETY.md) и реальный Build ID/host capture остаются отдельными prerequisites; недоступный host сценарий честно BLOCKED/NOT RUN.

Во всех трёх случаях source review подтверждает соответствие примера выбранным правилам, но не фактическое поведение кода в AE. Принятый baseline сохраняется до явного adoption; примеры и held-out fixtures не являются разрешением или production Evidence.
