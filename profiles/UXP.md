# UXP Profile

UXP-specific runtime/security/lifecycle/package requirements. Technology maturity определяется отдельно через §21 и SOURCES.md.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 40. UXP-specific engineering rules

UXP считать отдельной runtime / security / lifecycle моделью, а не «тем же CEP/ExtendScript на современном JavaScript».

Перед выбором UXP для After Effects обязательно подтвердить текущую поддержку целевой версии AE и требуемых host APIs по официальной документации Adobe. Для каждого используемого host member учитывать его `Min Version`, если Adobe её публикует.

На baseline 2026-10-01 Adobe объявляет public beta UXP plugins для After Effects к ноябрю 2026. Пока public beta фактически не доступна, UXP для AE рассматривается как **Technology Lifecycle: PREVIEW**. После выхода beta статус обновляется только после повторной проверки [SOURCES.md](../SOURCES.md), а не по календарю автоматически.

Конкретные возможности нужно подтверждать для целевой версии host, не переносить из Photoshop / Premiere / общей UXP документации автоматически. After Effects API Reference публикует `Min Version` для host members — эти значения входят в compatibility contract.

Официальные starting points:

- [After Effects UXP](https://developer.adobe.com/after-effects/uxp/)
- [After Effects UXP API Reference](https://developer.adobe.com/after-effects/uxp/after-effects-api/)
- [UXP Hub](https://developer.adobe.com/uxp/)
- [UXP Manifest](https://developer.adobe.com/uxp/guides/explanation/concepts/manifest/)
- [UXP Entrypoints / lifecycle](https://developer.adobe.com/uxp/guides/explanation/concepts/entrypoints/)
- [UXP package / distribution](https://developer.adobe.com/uxp/guides/how-to/distribution/package/)

### Runtime assumptions

UXP поддерживает современный JavaScript, но не является обычным browser runtime и не является Node.js runtime.

Нельзя предполагать наличие API только потому, что он существует в Chrome, Safari или Node.js.

Для каждого используемого web / JS / module API проверять UXP support в целевом runtime.

Node.js tooling допустим на build/test этапе, но runtime plugin не должен случайно зависеть от Node-only APIs.

Если используется TypeScript / bundler / framework, production bundle должен проверяться отдельно от исходного TypeScript/source.

### Async / await и состояние

Асинхронная операция должна иметь определённый lifecycle и ownership.

Текущая UXP документация отдельно ограничивает async lifecycle entrypoints: Promise support явно указан для plugin `destroy()` и panel `create()/show()/hide()/destroy()`. Не предполагать, что любой lifecycle callback можно безопасно превратить в долгую async-операцию.

В актуальном UXP Entrypoints guide lifecycle methods имеют ограниченный timeout (сейчас документировано 300 ms). Поэтому lifecycle callback должен выполнять только короткую обязательную работу; длительные операции запускать через отдельный управляемый operation flow, а не удерживать lifecycle transition.

По применимости:

- ловить rejected Promises и host API errors;
- не оставлять unhandled Promise rejection;
- предусматривать timeout для внешних I/O / IPC / network операций;
- не считать сохранённую selection / project / layer reference автоматически актуальной после `await`;
- после длительного `await` повторно валидировать host context перед mutation;
- предотвращать stale async result, который перезаписывает более новое состояние;
- определять семантику duplicate click / concurrent command / re-entry;
- использовать cancellation / operation token, если операция может устареть;
- UI должен явно показывать busy/error state для длительных операций.

### Manifest и permissions

`manifest.json` является частью production contract.

По применимости проверять:

- host и minimum host version;
- manifest version;
- entrypoints;
- requiredPermissions;
- network domains;
- local filesystem scope;
- IPC / process-launch permissions;
- plugin ID и distribution requirements.

Запрашивать минимально необходимые permissions.

Нельзя использовать `"all"` / broad wildcard permission только ради удобства без обоснования.

Permission denial, revoked access и недоступный resource должны быть штатно обработаны.

Изменение manifest / permissions считать behavior / packaging change и повторно проверять load / install / permission scenarios.

### File system / storage

Различать:

- plugin install area;
- plugin data / persistent storage;
- temp storage;
- user-selected external files/folders.

Не хранить незаменимые пользовательские данные только во временном storage.

Доступ за пределы sandbox выполнять через поддерживаемый permission model.

Tokens / saved references должны проверяться на stale / revoked state после restart.

### Network

Если используется network:

- объявить необходимые domains в manifest;
- предпочитать HTTPS;
- валидировать response schema и size;
- иметь timeout / retry policy;
- не блокировать UI бесконечным ожиданием;
- не считать network permission доказательством доступности endpoint.

### Lifecycle

Для plugin/panel entrypoints проверять фактическое поведение `create / show / hide / destroy` в целевой версии AE.

UXP platform documentation прямо предупреждает, что `hide()` и `destroy()` работают ненадёжно не во всех host-приложениях. Поэтому:

- не делать essential cleanup, сохранность данных или security invariant зависимыми только от `hide()` / `destroy()`;
- подтверждать фактическое поведение именно в целевой версии After Effects;
- при нескольких panels проверять, какой panel реально вызвал lifecycle event: общая UXP документация отмечает ограничения multi-panel lifecycle;
- учитывать, что command entrypoints выполняются как команды и не имеют persistent panel lifecycle.

Listener / timer / subscription должны иметь явный owner и защиту от duplicate registration после reload / reopen.

Lifecycle handler должен быть коротким и укладываться в platform timeout. Долгий network / file / host workflow не выполнять как обязательную часть teardown callback.

### Packaging / distribution

Различать pure UXP и hybrid UXP:

- pure UXP package распространяется как `.ccx`; по текущей Adobe UXP документации `.ccx` не требует package-level digital signature или timestamp;
- package создавать поддерживаемым Adobe tooling, а не считать ручной ZIP эквивалентом production package;
- plugin ID должен соответствовать выбранному distribution channel;
- hybrid plugin с native `.uxpaddon` требует отдельной проверки platform/architecture layout и native binaries;
- для macOS hybrid `.uxpaddon` выполнять Adobe-required Developer ID signing/notarization native binary;
- installation test выполнять через реальный поддерживаемый `.ccx` flow / Creative Cloud Desktop для заявленного distribution channel.

Не переносить CEP ZXP signing rules на UXP CCX и наоборот.

### UXP-specific test cases

По применимости включать:

- install / load through supported UXP tooling;
- panel open / close / reopen;
- reload;
- restart After Effects;
- manifest change → unload/reload;
- permission grant / deny / revoke;
- network allowed / blocked / timeout;
- storage persistence;
- stale token / stale async operation;
- concurrent invocation;
- malformed host/network data;
- UI resize / scaling;
- exact host / UXP runtime / plugin version in diagnostics.

Статические browser tests не заменяют runtime UXP test внутри After Effects.

---

