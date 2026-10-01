# AE Development Rules

Единый инженерный стандарт разработки инструментов для Adobe After Effects.

Этот репозиторий является **центральным источником правил для всех наших AE-проектов**: native plugins/effects, scripts, ScriptUI, CEP/UXP, helper-приложений и связанных компонентов.

## Версия стандарта

**Текущий стабильный baseline: v1.2.0**

- [VERSION](VERSION)
- [CHANGELOG.md](CHANGELOG.md)

Для release проекта фиксируйте и версию стандарта, и конкретный commit SHA.

## Главные документы

- [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) — нормативный индекс, ключевые определения и сгенерированная applicability map.
- [core/PROCESS.md](core/PROCESS.md) — общий процесс, testing, Git, identity, regression и Evidence.
- [core/ENGINEERING.md](core/ENGINEERING.md) — safety, performance, compatibility/maturity, docs, dependencies и engineering controls.
- [profiles/](profiles/) — Native / JSX / CEP / UXP / Helper / Release профили.
- [WORKFLOW.md](WORKFLOW.md) — рабочий ритм и статус-коммуникация.
- [rules-manifest.yaml](rules-manifest.yaml) — machine-readable applicability source of truth.
- [SOURCES.md](SOURCES.md) — freshness registry внешних time-sensitive источников.
- [LICENSE](LICENSE) — MIT license.

## Как использовать в AE-проектах

Каждый AE-проект должен:

1. Ссылаться на этот репозиторий как на основной стандарт разработки.
2. Перед значимым этапом сверяться с актуальными правилами.
3. Если проект требует отклонения — документировать причину и scope отклонения.
4. Для воспроизводимых milestone/release при необходимости фиксировать конкретный commit этого репозитория.
5. Не создавать локальную изменённую копию общих правил без необходимости: общие улучшения вносятся сюда.

Проектные правила могут **дополнять** этот стандарт, но не должны молча отменять его обязательные требования.

## Принцип

Написанный код — не проверенный продукт. **Risk Profile** (Light / Standard / Critical) и **Delivery Gate** (Development / Validation / Release) выбираются независимо. Пользовательская validation не заменяет внутренний QA.


## Starter kit

Практические scripts и шаблоны для внедрения стандарта без лишней ручной работы:

- [starter-kit/README.md](starter-kit/README.md)

Набор обобщает автоматизацию и Evidence-паттерны, уже использованные в наших AE-проектах.
