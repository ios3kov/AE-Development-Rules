# AE Development Rules

Правила для ИИ, который разрабатывает наш продукт для Adobe After Effects: от пользовательской цели и подтверждённых решений до кода, проверок и передачи результата. Инженерные требования также применимы к разработчикам и командам.

Этот репозиторий является **центральным источником правил для всех наших AE-проектов**: native plugins/effects, scripts, ScriptUI, CEP/UXP, helper-приложений и связанных компонентов.

## Версия стандарта

**Версия текущего checkout: v6.0.0 — не опубликована.**

Текущий checkout содержит новую macOS/Windows-политику: выпуск без обязательных платных сертификатов и внешних сервисов подписания/проверки. Приёмка опирается на целостность artifact, установку и фактическую загрузку в AE. Последняя опубликованная стабильная версия — 5.1.0; кандидат 6.0.0 не заменяет её автоматически.

- [VERSION](VERSION)
- [CHANGELOG.md](CHANGELOG.md)
- [Изменения и миграция кандидата 6.0.0](docs/releases/6.0.0.md)
- [Описание релиза и переход на 5.1.0](docs/releases/5.1.0.md)
- [Описание релиза и переход на 5.0.0](docs/releases/5.0.0.md)
- [GitHub Release v5.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.1.0)
- [Предыдущий GitHub Release v5.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.0.0)

Для release проекта фиксируйте и версию стандарта, и конкретный commit SHA.

5.1.0 — minor release: исправления enforcement существующих требований и необязательные материалы для ИИ. Уже принятый проектом baseline сохраняется до осознанного перехода; миграция tooling описана отдельно. 5.0.0 — первая публикация этого репозитория через GitHub Release; предыдущие версии в CHANGELOG описывают историю правил, а не наличие опубликованных GitHub-тегов.

## С чего начинать

Если работа ведётся с ИИ, пользователь может просто написать обычным языком:

> Хочу сделать такой инструмент. Посмотри правила и начинай.

Первым ИИ читает [AI_ENTRYPOINT.md](AI_ENTRYPOINT.md), сам определяет применимый путь и задаёт только действительно необходимые вопросы. Пользователь не обязан выбирать Stage 0, Risk Profile, Delivery Gate или другие инженерные режимы.

## Главные документы

- [AI_ENTRYPOINT.md](AI_ENTRYPOINT.md) — вход и протокол ИИ: намерение, приоритет решений, восстановление контекста, маршрутизация и автономность.
- [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) — обязательная декомпозиция конкретного внешнего референса, когда пользователь выбрал его как основу/аналог.
- [PRODUCT_DISCOVERY.md](PRODUCT_DISCOVERY.md) — обязательный Stage 0 для нового продукта / крупной новой функции: interview → Product Vision → Scope → User Flows → Success Criteria.
- [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) — нормативный индекс, ключевые определения и сгенерированная applicability map.
- [core/PROCESS.md](core/PROCESS.md) — общий процесс, testing, Git, identity, regression и Evidence.
- [core/ENGINEERING.md](core/ENGINEERING.md) — safety, performance, compatibility/maturity, docs, dependencies и engineering controls.
- [profiles/](profiles/) — Native / JSX / CEP / UXP / Helper / Release профили.
- [WORKFLOW.md](WORKFLOW.md) — рабочий ритм и статус-коммуникация.
- [rules-manifest.yaml](rules-manifest.yaml) — machine-readable applicability source of truth.
- [SOURCES.md](SOURCES.md) — freshness registry внешних time-sensitive источников.
- [LICENSE](LICENSE) — MIT license.

## Как использовать в AE-проектах

Если пользователь явно выбрал конкретный внешний продукт/artifact как референс, Smart Entry включает Reference Audit до Technical Design соответствующего scope. Для нового продукта / крупной новой функции ИИ отдельно определяет необходимость Stage 0 и, если требуется, проводит Product Discovery до технического планирования.

Каждый AE-проект должен:

1. Ссылаться на этот репозиторий как на основной стандарт разработки.
2. Перед каждым значимым этапом сверяться с применимыми правилами принятой проектом версии и заново оценивать scope и риски. Смена этапа не требует автоматически обновлять baseline стандарта.
3. Если проект требует отклонения — документировать причину и scope отклонения.
4. Для значимого milestone/release фиксировать версию, конкретный commit этого репозитория и дату принятия baseline по §34. Переход на новую версию делать осознанно.
5. Не создавать локальную изменённую копию общих правил без необходимости: общие улучшения вносятся сюда.

Проектные правила могут **дополнять** этот стандарт, но не должны молча отменять его обязательные требования.

## Принцип

Написанный код — не проверенный продукт. **Risk Profile** (Light / Standard / Critical) и **Delivery Gate** (Development / Validation / Release) выбираются независимо. Пользовательская validation не заменяет внутренний QA.


## Starter kit

Практические scripts и шаблоны для внедрения стандарта без лишней ручной работы:

- [starter-kit/README.md](starter-kit/README.md)

Набор обобщает автоматизацию и Evidence-паттерны, уже использованные в наших AE-проектах.

## Проверки и внедрение

- [План и результаты исправления аудита](docs/AUDIT_REMEDIATION.md)
- [Идентификаторы требований](REQUIREMENTS.json)
- [Заполненные примеры Native, JSX и CEP](starter-kit/examples/adoption/README.md)
- [Evidence lifecycle](core/EVIDENCE_LIFECYCLE.md)
- [Порядок изменения стандарта](CONTRIBUTING.md)
- [Сценарии оценки поведения ИИ](docs/AI_BEHAVIOR_SCENARIOS.md)
- [Шаблон состояния продолжающейся задачи](starter-kit/templates/AI_TASK_STATE.md)
- [Изменения протокола ИИ и проверка обновления](docs/AI_PROTOCOL_UPDATE.md)
- [Дальнейший аудит и список доработок протокола ИИ](docs/AI_PROTOCOL_BACKLOG.md)
- [Замечания глубокого аудита 5.0.0 и их состояние](docs/DEEP_AUDIT_BACKLOG.md)
- [Исправления D01–D10 и внедрение I01–I04](docs/DEEP_AUDIT_REMEDIATION_5_1.md)
- [Versioned errata для принятых baseline](docs/ERRATA.md)
- [Краткие примеры решений для ИИ](docs/AI_DECISION_EXAMPLES.md)

Скрипты требуют Node.js 22+; POSIX wrappers также требуют zsh. При копировании сохранять весь каталог `scripts`, включая `lib`, и соответствующие schemas/registry для project-record tooling.
