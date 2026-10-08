# AE Development Rules

Правила для ИИ, который разрабатывает наш продукт для Adobe After Effects: от пользовательской цели и подтверждённых решений до кода, проверок и передачи результата. Инженерные требования также применимы к разработчикам и командам.

Этот репозиторий является **центральным источником правил для всех наших AE-проектов**: native plugins/effects, scripts, ScriptUI, CEP/UXP, helper-приложений и связанных компонентов.

## Версия стандарта

**Версия текущего checkout: v11.0.0 — 2026-10-08.**

Кандидат сокращённой редакции; не опубликован.

11.0.0 сокращает обязательное чтение: [короткое ядро](core/PROCESS.md#1-применение-правил-и-обязательность-проверок), профиль инструмента и [единый чеклист передачи](profiles/RELEASE.md#26-validation-gate-и-release-gate). Допуск text/local executable/remote MCP разделён; evaluation tools вынесены в optional package. [Изменения и миграция](docs/COMPACT_STANDARD.md). Опубликованная 10.0.2 и её Evidence остаются неизменными; новые условия требуют явного принятия baseline.

10.0.2 исправляет учёт повторных проверок, откат одинаковых skill-пакетов, привязку witness к файлу реализации, маршруты чтения и статусы Errata. [Внедрение и совместимость](docs/releases/10.0.2.md). Старые witness-манифесты без `owner_sha256` требуют нового независимого review/pin. Публикацию и точный коммит подтверждают GitHub Release v10.0.2 и приложенное Evidence; CI не подтверждает пользу агентского слоя или независимую custody.

10.0.1 — исправляющий выпуск: раздельные source/Evidence commits, отказ при ошибке чтения package, общий таймаут протокола агента и проверка пересечений cache/output. [Исправления и внедрение](docs/releases/10.0.1.md). Публикация подтверждается GitHub Release v10.0.1 и приложенным exact-commit CI Evidence. Защита GitHub и реальные пилоты оцениваются отдельно; успешный CI не подтверждает их выполнение.

10.0.0 вводит conditional **Agent Skills §43**: независимый допуск, полный package digest, управляемый lifecycle и проверка фактических возможностей среды. Добавлены исполняемые evaluation/process/native инструменты; Reference Evidence из PR #22 включено в этот release candidate. Обычная задача без внешних расширений не получает skill-инфраструктуру. Это major process release по §34; статус публикации проверяйте по GitHub Release.

9.0.0 вводит **Decision Grill** для материальных взаимозависимых решений: агент строит design tree, сам исследует доступные факты и задаёт пользователю только текущий frontier с рекомендуемым вариантом. Ясные bugfix/малые правки остаются без интервью. Это major process release по §34.

8.0.0 вводит явный контроль существенной задачи: применимые требования связываются с tasks/checks/Evidence, перед завершением сверяются все текущие обязательства. Для нового набора фичей в текущем проекте восстановить baseline, оценить impact и обновить scope/план/приёмку без потери прежних решений.

Сохраняется введённая в 7.0.0 проверка потребности в безопасной уборке после разработки и протокол её выполнения: ownership, защита параллельной работы, план, проверенное восстановление и сохранность релизных материалов. Неизвестные материалы остаются на месте; перемещение тоже требует проверки зависимостей.

Сохраняется введённый в 6.2.0 протокол проверки совместимости без локальной установки всех AE: аудит API и exact artifact, SDK/fallback probes и переносимый пакет для реального запуска на другой машине. Static/mock/build checks не подтверждают непроверенные версии AE.

Сохраняется введённая в 6.1.0 явная передача пользовательской документации после релиза: ИИ даёт ссылку на руководство и предлагает перейти к нему; ответ на «что дальше?» начинается с проверки документации. Необходимые инструкции готовятся до публикации.

Сохраняется установленная в 6.0.0 macOS/Windows-политика: выпуск без обязательных платных сертификатов и внешних сервисов подписания/проверки. Приёмка опирается на целостность artifact, установку и фактическую загрузку в AE. Точный released commit, платформенные CI и checksums архивов записаны в release-evidence.json у GitHub Release.

- [VERSION](VERSION)
- [Исправления и переход на 10.0.1](docs/releases/10.0.1.md)
- [Начало работы и переход на 10.0.0](docs/releases/10.0.0.md)
- [Описание релиза и переход на 9.0.0](docs/releases/9.0.0.md)
- [CHANGELOG.md](CHANGELOG.md)
- [Описание релиза и переход на 8.0.0](docs/releases/8.0.0.md)
- [Описание релиза и переход на 7.0.0](docs/releases/7.0.0.md)
- [Описание релиза и переход на 6.2.0](docs/releases/6.2.0.md)
- [Описание релиза и переход на 6.1.0](docs/releases/6.1.0.md)
- [Описание релиза и переход на 6.0.0](docs/releases/6.0.0.md)
- [Описание релиза и переход на 5.1.0](docs/releases/5.1.0.md)
- [Описание релиза и переход на 5.0.0](docs/releases/5.0.0.md)
- [GitHub Release v10.0.1](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v10.0.1)
- [GitHub Release v10.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v10.0.0)
- [Предыдущий GitHub Release v9.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v9.0.0)
- [GitHub Release v8.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v8.0.0)
- [Предыдущий GitHub Release v7.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v7.0.0)
- [Предыдущий GitHub Release v6.2.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v6.2.0)
- [Предыдущий GitHub Release v6.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v6.1.0)
- [Предыдущий GitHub Release v6.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v6.0.0)
- [Предыдущий GitHub Release v5.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.1.0)
- [Предыдущий GitHub Release v5.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.0.0)

Для release проекта фиксируйте и версию стандарта, и конкретный commit SHA.

6.0.0 — major release: изменение macOS/Windows-приёмки и интерфейсов проверок. Переход оформляется осознанно; прежние Evidence и принятые baselines сохраняются.

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
- [AE engineering know-how](docs/AE_ENGINEERING_KNOWHOW.md) — reusable render-validation patterns with evidence and scope; no new mandatory policy.
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



## Методические источники

Conditional **DECISION-GRILL (§42)** адаптирует design-tree / frontier-rounds подход из MIT-репозитория [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), проверенного 2026-10-06. В стандарт перенесён общий процесс принятия решений, а не текст skill: агент сам добывает доступные факты, пользователь закрывает материальные решения, зависимые вопросы открываются только после prerequisites.


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

## Conditional reference tooling (included in 10.0.0)

[Scope reconciliation](docs/REFERENCE_UPDATE_RECONCILIATION.md), [reference adapters](docs/REFERENCE_EVIDENCE_OBLIGATIONS_PROPOSAL.md), [offline helpers](docs/REFERENCE_ENGINEERING_TOOLS.md) and [agent evaluation delta](docs/REFERENCE_AGENT_EVALUATION.md). Existing adopted baselines and historical releases remain unchanged; adopt 10.0.0 and its exact release commit explicitly. Standard CI verifies synthetic tooling contracts, not real AE/iPhone parity. Product/market/publication items remain paused.
