# Development Rules
## Правила разработки инструментов для Adobe After Effects

Эти правила применяются ко всем инструментам для Adobe After Effects:

- native plugins / effects: `.plugin`, `.aex`;
- scripts: `.jsx`, `.jsxbin`;
- ScriptUI panels;
- CEP extensions;
- UXP plugins / panels — только при подтверждённой поддержке целевой версией After Effects;
- вспомогательным приложениям и helper-процессам;
- пакетам из нескольких связанных компонентов.

Правила применяются с учётом типа инструмента, заявленных возможностей, целевых платформ и риска изменений.

Наличие технологии в экосистеме Adobe не означает, что она поддерживается конкретной версией After Effects или предоставляет необходимые host API.

---

## AI Smart Entry

При работе с ИИ пользователь описывает цель обычным языком. [AI_ENTRYPOINT.md](AI_ENTRYPOINT.md) определяет, как ИИ должен сам:

- понять тип задачи;
- использовать уже известный контекст;
- определить необходимость Product Discovery;
- выбрать внутренние Risk Profile / Delivery Gate;
- выбрать только применимые rule modules;
- задать пользователю только material questions человеческим языком.

Пользователь не обязан управлять инженерной классификацией стандарта.

---

## Reference-driven development

Если пользователь явно выбрал конкретный внешний продукт/artifact как референс, основу, аналог или parity target, применяется [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md).

Этот путь **условный**: он не включается для общей категории эффекта или случайного упоминания внешнего продукта.

Для whole-product analogue Reference Audit MUST восстановить максимально полный доказуемый внешний контракт до Technical Design: UI/controls, functionality, presets, state/persistence, animation, render/output, edge cases, performance, packaging/integration и известные internal claims.

Недоказанная внутренняя реализация не считается фактом. Существенные claims классифицируются как **PROVEN / OBSERVED / INFERRED / UNKNOWN**.

Reusable Reference Specification: [starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md](starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md).

Типовая цепочка:

**Smart Entry → Reference Audit (если triggered) → Reference Specification → Product Discovery/Product Vision (если требуется) → Product Spec → Technical Design → Production Plan → Development → Parity Testing → Validation → Release**

---

## Stage 0 — Product Discovery

До выбора технической архитектуры для нового продукта, крупной функции или существенного product-direction change применяется [PRODUCT_DISCOVERY.md](PRODUCT_DISCOVERY.md).

Stage 0 отвечает на вопрос **«что именно должен дать продукт пользователю?»** до вопроса **«как это реализовать?»**.

Основная цепочка:

**Product Discovery → Product Vision → Product Scope → Product Spec → Technical Design → Production Plan → Development → Validation → Release**

Reusable interview/vision template: [starter-kit/templates/PRODUCT_DISCOVERY_TEMPLATE.md](starter-kit/templates/PRODUCT_DISCOVERY_TEMPLATE.md).

## Нормативные ключевые слова

Чтобы обязательность правил трактовалась одинаково:

- **MUST / ОБЯЗАТЕЛЬНО / ДОЛЖЕН** — требование обязательно в применимом scope; пропуск требует явного статуса BLOCKED/N/A или документированного deviation.
- **MUST NOT / НЕЛЬЗЯ / ЗАПРЕЩЕНО** — действие запрещено в применимом scope.
- **SHOULD / СЛЕДУЕТ** — сильная рекомендация; отклонение допустимо при документированной технической причине.
- **MAY / ДОПУСКАЕТСЯ** — разрешённый вариант, не обязательный сам по себе.
- **APPLICABLE WHEN / ПО ПРИМЕНИМОСТИ / ГДЕ ПРИМЕНИМО** — требование становится MUST только когда указанный риск, component, platform или delivery path реально входит в scope.

Слова без нормативного смысла не должны использоваться как скрытый gate. Если формулировка допускает несколько трактовок, приоритет имеет более узкий документированный scope и явный риск, а не максимальный объём ceremony.

---

## Быстрая карта применимости

Стандарт использует **две независимые оси**:

1. **Risk Profile:** Light / Standard / Critical — насколько рискованно текущее изменение.
2. **Delivery Gate:** Development / Validation / Release — кому и для чего передаётся artifact.

Critical не означает Release. Низкорисковый patch может идти в Release Gate, а критичное внутреннее изменение может оставаться Development до готовности.

Карта ниже генерируется из [rules-manifest.yaml](rules-manifest.yaml). Rule Group ID — стабильный идентификатор группы требований; соответствующий § указан рядом.

<!-- APPLICABILITY_TABLE:START -->
### Risk Profile × artifact

| Тип проекта | Light | Standard | Critical |
|---|---|---|---|
| Native plugin / effect | CORE-SCOPE ([§1](core/PROCESS.md)), GIT ([§6](core/PROCESS.md)), IDENTITY ([§7](core/PROCESS.md)), REGRESSION ([§9](core/PROCESS.md)), EVIDENCE ([§10](core/PROCESS.md)), CODE-SAFETY ([§14](core/ENGINEERING.md)), NATIVE-RUNTIME ([§23](profiles/NATIVE.md)) | light + BASELINE ([§8](core/PROCESS.md)), TEST-CONTROL ([§2](core/PROCESS.md)), COMPAT ([§21](core/ENGINEERING.md)), PERF ([§17-19](core/ENGINEERING.md)), real AE runtime tests | standard + REPRO ([§20](core/ENGINEERING.md)), deep risk-specific checks; Critical does not imply Release |
| JSX / ScriptUI | CORE-SCOPE ([§1](core/PROCESS.md)); micro-helper profile allowed when eligible | GIT ([§6](core/PROCESS.md)), IDENTITY ([§7](core/PROCESS.md)), REGRESSION ([§9](core/PROCESS.md)), EVIDENCE ([§10](core/PROCESS.md)), TOOL-RUNTIME ([§22](profiles/TOOLS.md)), real AE smoke/integration test | standard + risk-specific CODE-SAFETY ([§14](core/ENGINEERING.md)) / PERF ([§17-19](core/ENGINEERING.md)) / COMPAT ([§21](core/ENGINEERING.md)) |
| CEP | CORE-SCOPE ([§1](core/PROCESS.md)), TOOL-RUNTIME ([§22](profiles/TOOLS.md)) | GIT ([§6](core/PROCESS.md)), IDENTITY ([§7](core/PROCESS.md)), REGRESSION ([§9](core/PROCESS.md)), EVIDENCE ([§10](core/PROCESS.md)), COMPAT ([§21](core/ENGINEERING.md)), TOOL-RUNTIME ([§22](profiles/TOOLS.md)), bridge/lifecycle/package/runtime tests | standard + risk-specific security/IPC/helper checks |
| UXP | CORE-SCOPE ([§1](core/PROCESS.md)), UXP ([§40](profiles/UXP.md)) | GIT ([§6](core/PROCESS.md)), IDENTITY ([§7](core/PROCESS.md)), REGRESSION ([§9](core/PROCESS.md)), EVIDENCE ([§10](core/PROCESS.md)), COMPAT ([§21](core/ENGINEERING.md)), TOOL-RUNTIME ([§22](profiles/TOOLS.md)), UXP ([§40](profiles/UXP.md)), host/Min Version/runtime tests | standard + risk-specific permissions/lifecycle/native-addon checks |
| Helper / companion app | CORE-SCOPE ([§1](core/PROCESS.md)), GIT ([§6](core/PROCESS.md)), IDENTITY ([§7](core/PROCESS.md)), REGRESSION ([§9](core/PROCESS.md)), EVIDENCE ([§10](core/PROCESS.md)), CODE-SAFETY ([§14](core/ENGINEERING.md)) | light + BASELINE ([§8](core/PROCESS.md)), COMPAT ([§21](core/ENGINEERING.md)), PERF ([§17-19](core/ENGINEERING.md)), IPC/files/network/runtime tests | standard + REPRO ([§20](core/ENGINEERING.md)), DEPSEC ([§35](core/ENGINEERING.md)), security/data-loss checks |

### Delivery Gate × artifact

| Тип проекта | Validation | Release |
|---|---|---|
| Native plugin / effect | GATES ([§26](profiles/RELEASE.md)) / Validation Gate | GATES ([§26](profiles/RELEASE.md)) / Release Gate + MAC-DIST ([§28](profiles/RELEASE.md)) or WIN-DIST ([§30](profiles/RELEASE.md)) when applicable |
| JSX / ScriptUI | GATES ([§26](profiles/RELEASE.md)) / Validation Gate | GATES ([§26](profiles/RELEASE.md)) / Release Gate; OS signing only for executable installer/helper |
| CEP | GATES ([§26](profiles/RELEASE.md)) / Validation Gate | GATES ([§26](profiles/RELEASE.md)) / Release Gate + Adobe distribution requirements; OS signing only for executable code |
| UXP | GATES ([§26](profiles/RELEASE.md)) / Validation Gate | GATES ([§26](profiles/RELEASE.md)) / Release Gate + current Adobe distribution requirements; OS signing only for native addon/executable |
| Helper / companion app | GATES ([§26](profiles/RELEASE.md)) / Validation Gate | GATES ([§26](profiles/RELEASE.md)) / Release Gate + MAC-DIST ([§28](profiles/RELEASE.md)) or WIN-DIST ([§30](profiles/RELEASE.md)) when applicable |
<!-- APPLICABILITY_TABLE:END -->

Правило выбора:

0. определить, triggered ли conditional Reference Audit;
1. определить фактический тип artifact;
2. выбрать Risk Profile по риску текущего изменения;
3. выбрать Delivery Gate по текущей цели передачи;
4. объединить требования строки artifact + Risk Profile + Delivery Gate;
5. добавить требования для реально затронутых рисков, даже если они не перечислены в краткой карте.

Для смешанного продукта использовать объединение профилей его компонентов. Например, UXP panel с native helper проверяется как UXP + Helper, а native addon получает отдельные platform requirements.

Conditional Rule Groups не обязаны появляться в artifact matrix. Например, **REFERENCE-AUDIT (§R0)** применяется по trigger `explicit_external_reference`, независимо от типа artifact.

Организационный порядок работы и формат коротких статусов вынесены в [WORKFLOW.md](WORKFLOW.md).

---

## Нормативные модули

`DEVELOPMENT_RULES.md` — индекс стандарта. Нормативный текст разделён по модулям; один Rule Group имеет один canonical location.

- [AI Smart Entry](AI_ENTRYPOINT.md) — пользовательский вход в стандарт для AI-assisted работы.
- [Reference Audit](REFERENCE_AUDIT.md) — conditional reference-driven path / §R0.
- [Product Discovery](PRODUCT_DISCOVERY.md) — Stage 0 / §0.
- [Process Core](core/PROCESS.md) — §§1–13, §27.
- [Engineering Core](core/ENGINEERING.md) — §§14–21, §§24–25, §§31–39, §41.
- [Tools / Panels Runtime](profiles/TOOLS.md) — §22.
- [Native Effect / Render Plugin](profiles/NATIVE.md) — §23.
- [Release / Distribution](profiles/RELEASE.md) — §26, §§28–30.
- [UXP](profiles/UXP.md) — §40.
- [JSX / ScriptUI navigation](profiles/JSX.md).
- [CEP navigation](profiles/CEP.md).
- [Helper / Companion App navigation](profiles/HELPER.md).

Machine-readable applicability/source-of-truth: [rules-manifest.yaml](rules-manifest.yaml).

Time-sensitive external facts: [SOURCES.md](SOURCES.md).

Операционный workflow: [WORKFLOW.md](WORKFLOW.md).

---

## Главное правило

**Risk Profile и Delivery Gate выбираются независимо. Пользовательская validation не заменяет внутренний QA, а release-only ceremony не должна автоматически навязываться каждому тестовому build.**

Перед передачей artifact MUST быть однозначно известно:

1. какой Risk Profile применяется;
2. какой Delivery Gate применяется;
3. какой commit / Build ID / artifact проверяется;
4. какие обязательные проверки текущего scope имеют Test Status PASS / FAIL / BLOCKED / NOT RUN / N/A;
5. какие ограничения остаются;
6. какие Evidence подтверждают вывод.

Написанный код — не то же самое, что проверенный продукт. Проверенная версия — не то же самое, что следующая сборка.
