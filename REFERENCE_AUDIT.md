# Reference Audit

## R0. Reference-driven development

Reference Audit — обязательный условный этап для задач, где пользователь выбрал **конкретный внешний продукт / artifact как референс, основу, аналог или parity target**.

Цель — до проектирования собственного решения максимально полно восстановить **проверяемый контракт референса**: что пользователь видит, что каждый control делает, как ведут себя presets/state/render/edge cases, какие ограничения существуют и какие внутренние выводы действительно доказаны.

Reference Audit не обещает невозможное «100% знание» закрытой внутренней реализации. Полнота внешнего поведения должна быть максимальной в согласованном scope; недоказанные внутренние детали MUST оставаться явно помеченными как INFERRED или UNKNOWN.

Reusable output template: [starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md](starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md).

## R0.1. Когда Reference Audit включается

Reference Audit MUST включаться, если пользователь явно делает конкретный внешний продукт или artifact основой задачи, например:

- присылает plugin/effect/script/panel/helper или другой файл и говорит, что это референс;
- даёт ссылку на конкретный продукт и просит взять его за основу;
- называет конкретный продукт/продукты: «сделай как X», «аналог X», «повтори поведение X»;
- просит воспроизвести конкретный UI, mechanic, preset system, render behavior или другой behavior существующего продукта;
- даёт конкретные screenshots/video/documentation, однозначно обозначенные как reference target.

Reference Audit **не включается автоматически**, если пользователь:

- описывает только общий класс эффекта/инструмента: «хочу glow», «хочу line generator»;
- упоминает продукт только как compatibility target, источник проблемы, marketplace context или случайный пример;
- просит независимый продукт без конкретного external parity target.

Если неясно, является ли названный продукт именно основой/аналогом, ИИ задаёт один короткий человеческий вопрос, а не запускает полный аудит по одному упоминанию бренда.

## R0.2. Scope референса

Сначала определить, что именно пользователь выбрал reference target:

- **whole-product reference** — весь доступный продукт является основой; аудитировать все существенные области;
- **feature reference** — только конкретная функция/механика;
- **UI reference** — внешний вид, структура и interaction;
- **behavior/render reference** — результат и поведение;
- **multi-reference** — несколько продуктов, каждый для своей области.

Если пользователь сказал «сделай аналог продукта X» без более узкого ограничения, по умолчанию считать scope **whole-product reference**.

Не расширять reference scope на несвязанные продукты или функции без причины.

## R0.3. Зафиксировать identity референса

До выводов MUST зафиксировать доступную identity:

- название продукта;
- версия/build, если доступна;
- platform / architecture;
- host / After Effects version;
- URL/source;
- filename/package identity;
- SHA-256 предоставленного artifact, когда файл доступен;
- дата наблюдения;
- лицензия/доступ/разрешение на исследование, если это существенно для метода анализа.

Нельзя смешивать результаты разных версий референса как будто это один artifact.

Если reference обновился, отличать старый и новый baseline.

## R0.4. Использовать максимально глубокое допустимое исследование

Для whole-product reference аудит SHOULD исчерпать доступные безопасные и разрешённые источники Evidence до начала Technical Design.

По применимости использовать:

### Black-box runtime analysis

- запуск в целевом After Effects;
- полный inventory UI;
- systematic parameter sweeps;
- presets;
- state/save/reopen;
- keyframes/animation/expressions;
- copy/paste/duplicate/reset;
- representative inputs;
- edge/extreme inputs;
- error paths;
- render queue / preview / aerender / MFR, где применимо;
- performance measurements.

### Static artifact inspection

По доступности и применимости:

- package/bundle structure;
- metadata / manifest / Info.plist / PiPL / resources;
- binary architecture and dependencies;
- imports/exports/symbols;
- embedded strings/resources/assets;
- file formats, preset files, config/state schemas;
- observable serialization/project data;
- host API surface;
- external helpers/processes/files/network dependencies.

### Documentation / public evidence

- official manual;
- product page;
- changelog/version history;
- vendor examples/tutorials;
- documented presets/defaults/requirements.

### Decompilation / disassembly / invasive analysis

Использовать только когда это разрешено применимыми правами/лицензией/явным разрешением и действительно нужно для заявленного scope.

Reference Audit MUST NOT требовать обхода DRM, licensing, activation, anti-tamper или других access controls и MUST NOT предполагать право на перераспространение чужого proprietary code/assets.

Если глубокий внутренний анализ недоступен, это не разрешает додумывать implementation: соответствующие claims остаются INFERRED/UNKNOWN, а parity строится по доказуемому внешнему контракту.

## R0.5. Reference Claim Status

Каждое существенное утверждение о референсе должно иметь один **Reference Claim Status**:

- **PROVEN** — подтверждено прямым техническим Evidence, достаточным именно для этого утверждения;
- **OBSERVED** — поведение непосредственно воспроизведено/измерено black-box тестом, но внутренняя причина не доказана;
- **INFERRED** — наиболее вероятный вывод из Evidence, но не доказанный факт;
- **UNKNOWN** — Evidence недостаточно или область недоступна.

Reference Claim Status — отдельная ось. Он не заменяет Test Status, Compatibility Status или Evidence Confidence из Process Core.

Запрещено повышать INFERRED до PROVEN только потому, что гипотеза хорошо объясняет наблюдаемое поведение.

## R0.6. Обязательная декомпозиция whole-product reference

Для whole-product reference MUST быть составлен inventory по применимым областям.

### UI / interaction

Для каждого control:

- точное имя/label;
- type;
- hierarchy/group/order;
- visibility/enabled rules;
- default;
- min/max/step;
- units;
- precision/rounding;
- modifier keys/gestures;
- dependencies on other controls;
- reset behavior;
- animatable/keyframe behavior;
- expression behavior, если применимо;
- tooltip/help/error state.

Также фиксировать:

- panel/effect layout;
- collapsed/expanded groups;
- resize/scaling/HiDPI behavior;
- context menus;
- dialogs;
- focus/keyboard behavior;
- dynamic UI changes.

### Functional behavior

Для каждого control/feature:

- что меняется;
- какой input нужен;
- deterministic/non-deterministic behavior;
- interaction с другими параметрами;
- order-dependent behavior;
- boundaries and saturation;
- disabled/zero/negative/extreme behavior;
- failure behavior.

### Presets

MUST определить:

- полный доступный preset inventory в scope;
- naming/categories/order;
- какие параметры меняет каждый preset;
- какие параметры не меняет;
- exact/observable parameter values;
- reset/default interaction;
- custom preset save/load, если есть;
- portability/version behavior, если применимо.

Preset не считается «понятым» только потому, что визуально похож на другой результат.

### State / persistence

Проверять по применимости:

- defaults;
- reset;
- duplicate/copy/paste;
- project save/reopen;
- app restart;
- effect remove/re-add;
- undo/redo;
- preset apply/save/load;
- migration between versions;
- corrupted/missing state behavior.

### Render / output

Проверять по применимости:

- representative visual cases;
- transparent pixels / alpha;
- premultiplication assumptions;
- 8/16/32 bpc;
- HDR/extended range;
- color management / working space;
- frame bounds / ROI;
- pixel aspect / resolution / downsample;
- temporal behavior;
- CPU/GPU paths;
- preview vs render queue vs aerender;
- MFR / Smart Render;
- deterministic repeatability.

### Performance

Фиксировать минимум:

- test scene/input;
- resolution / bit depth;
- relevant parameter state;
- hardware/host version;
- warm/cold behavior where meaningful;
- timing or throughput;
- known cliffs / expensive parameters.

### Packaging / integration

По применимости:

- install location;
- plugin discovery;
- menu/effect category;
- IDs/names visible to AE;
- helper processes/files;
- permissions;
- external dependencies;
- update/uninstall behavior;
- observable licensing/activation behavior без обхода защит.

## R0.7. Test matrix вместо случайного кликанья

Reference Audit MUST быть систематическим.

Для numerical/continuous controls использовать representative sweep:

- minimum;
- near-minimum;
- default;
- typical low/mid/high;
- near-maximum;
- maximum;
- zero/negative/out-of-range, если интерфейс/API допускает;
- взаимодействие с другими ключевыми параметрами.

Для discrete controls проверить каждое доступное значение, если число вариантов разумно.

Для combinations использовать pairwise/risk-based matrix и отдельно проверять известные критические взаимодействия.

Если reference behavior зависит от input, использовать несколько fixture-классов, а не один красивый пример.

## R0.8. Coverage Map

До Technical Design должен существовать Reference Coverage Map минимум по областям:

- identity/package;
- UI/interaction;
- parameters/functionality;
- presets;
- state/persistence;
- animation/keyframes/expressions;
- render/output;
- alpha/color/bit depth;
- edge cases/errors;
- performance;
- compatibility/host behavior;
- packaging/integration;
- internal implementation claims, если они вообще нужны.

Для каждой области фиксировать:

- scope;
- coverage: COMPLETE / PARTIAL / BLOCKED / N/A;
- Reference Claim Status для ключевых выводов;
- Evidence;
- оставшиеся gaps.

PARTIAL или BLOCKED допустимы только с явным объяснением влияния на будущий Product Spec/acceptance.

## R0.9. Несколько референсов

Если пользователь дал несколько конкретных products:

1. создать отдельную identity и Evidence boundary для каждого;
2. указать, какая область берётся из какого референса;
3. не смешивать противоречивые behaviors молча;
4. при конфликте либо использовать явно заданный пользователем приоритет, либо задать короткий product-level вопрос;
5. итоговую Reference Specification строить как осознанный target contract, а не как случайную смесь.

## R0.10. Reference Specification

Результат аудита MUST быть собран в Reference Specification.

Минимум:

- reference identity;
- scope / non-scope;
- UI/control inventory;
- behavior matrix;
- preset inventory;
- state/persistence contract;
- render/output contract;
- edge/error behavior;
- performance baseline;
- packaging/integration observations;
- claim/evidence ledger;
- Coverage Map;
- known gaps;
- parity acceptance tests.

Reference Specification описывает **что должен воспроизвести наш продукт**, но не обязывает копировать недоказанную внутреннюю архитектуру.

## R0.11. Exit criteria

Reference Audit считается достаточным для перехода к Product Spec / Technical Design, когда:

1. reference identity зафиксирована;
2. reference scope однозначен;
3. все существенные user-visible controls/features в scope inventoried;
4. для whole-product reference presets/state/render/edge/performance/package области проверены либо явно N/A;
5. Coverage Map заполнен;
6. существенные claims имеют PROVEN/OBSERVED либо явно INFERRED/UNKNOWN;
7. критические UNKNOWN не замаскированы как requirements;
8. сформированы parity acceptance tests;
9. известные gaps не делают целевой product contract двусмысленным.

Если critical gap не позволяет определить требуемое поведение, статус этапа BLOCKED и Technical Design соответствующей области не начинается.

## R0.12. Связь с Product Discovery и разработкой

Reference Audit — условный слой, а не замена Product Discovery.

Если продукт новый или меняется product direction, Stage 0 всё равно применяется по своим правилам. Reference evidence используется как input в Product Vision/Scope, но пользовательские цели имеют приоритет над слепым копированием референса.

Типовая цепочка:

**Smart Entry → Reference Audit (если triggered) → Reference Specification → Product Discovery/Product Vision (если требуется) → Product Spec → Technical Design → Production Plan → Development → Parity Testing → Validation → Release**

Stage 0 и Reference Audit MAY идти итеративно, если понимание одного уточняет scope другого, но оба применимых контракта MUST быть достаточно завершены до технического проектирования.

## R0.13. Parity Testing после реализации

Для reference-driven scope acceptance MUST включать parity tests.

Одинаковые или эквивалентные fixtures/scenarios запускаются на:

- reference;
- нашем implementation.

Сравнивать по применимости:

- control defaults/ranges/dependencies;
- presets;
- state transitions;
- numeric/visual output;
- alpha/color;
- edge cases;
- performance envelope;
- host/render modes;
- packaging-visible behavior.

Допустимые различия должны быть заранее определены Product Spec.

«Выглядит похоже на одном примере» не является достаточным parity Evidence для whole-product reference.

## Главное правило

**Конкретный внешний референс сначала превращается в доказуемый Reference Specification, и только потом — в реализацию.**

Нельзя заменять неизвестную внутреннюю реализацию уверенной догадкой.  
Нельзя начинать coding whole-product analogue после поверхностного просмотра UI.  
Нельзя считать parity доказанным без систематических сравнительных тестов.
