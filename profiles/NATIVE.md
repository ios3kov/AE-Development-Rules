# Native Effect / Render Plugin Profile

Специфические требования native AE effects/render plugins.

Нумерация § сохранена глобально для стабильных ссылок из manifest/templates.

## 23. Дополнительные проверки Native Effects / Render Plugins
<!-- REQ: RENDER-001 -->

### Render Context

Проверять заявленные:

- interactive render;
- RAM Preview;
- render queue;
- `aerender`;
- background rendering;
- MFR;
- Smart Render.

Ни один non-interactive render path не должен требовать UI.

### Покрытие native review и единицы (10.0.0)
<!-- REQ: NATIVE-REVIEW-001 -->

Общий C/C++ review, risk-scoped inventory и его статусы определены в [Engineering §14](../core/ENGINEERING.md#14-качество-и-безопасность-кода). Для native inventory SHOULD сохранить exact candidate/source digest и основание. Общая сборка не превращает UNREVIEWED/BLOCKED в REVIEWED. Необязательный [native review record](../starter-kit/templates/NATIVE_REVIEW.md), schema и `check_native_review.py` сверяют объявленный reviewed scope, actual source/Evidence bytes и пять областей (`memory`, `numeric`, `ownership`, `concurrency`, `units`); они не исполняют SDK callbacks и не выдают SDK/host certification.

При затронутой арифметике SHOULD явно назвать input/output units и conversion/invariant: кадры ↔ секунды при заданном fps; image pixels ↔ composition coordinates с render scale/pixel aspect/ROI; integer channel scale ↔ float/HDR при выбранном bit depth. Generic `16-bit` не определяет native AE channel maximum: сверить выбранные SDK headers и применимые Adobe docs. Назвать rounding, precision/tolerance и диапазон, не нормализовать HDR/negative float/alpha неявно. Property/fuzz checks pure math/parser/state и примеры ошибки units — Engineering §41; existing render comparator сохраняет явные bpc/alpha/color-management contracts.

Primary authority для API — headers точной выбранной SDK версии и применимые Adobe документы. General skills, Context7 results, обучающий offline fixture, flags и static review не подтверждают runtime AE correctness. Сохраняются все нижеследующие MFR/SmartFX, alpha/bit-depth/color-management и real-host checks.

### Host API и ресурсы

Проверять:

- ограничения вызова SDK из потоков;
- корректность flags / capabilities;
- владение buffers и handles;
- соответствие checkout / checkin;
- cleanup при ошибке и отмене;
- отсутствие race conditions;
- отсутствие unsafe shared mutable state.

Не заявлять поддержку MFR или другого режима только на основании выставленного флага.

### Pixel Correctness

Проверять применимые:

- 8 / 16 / 32 bpc;
- alpha;
- premultiplied / unpremultiplied сценарии;
- transparent pixels;
- negative float values;
- float values выше `1.0`;
- extreme values;
- отсутствие unintended clipping;
- отсутствие unintended quantization;
- row bytes / stride;
- размеры и границы buffers.

### Spatial / Temporal Behaviour

По применимости проверять:

- ROI;
- render scale / downsampling;
- pixel aspect ratio;
- границы кадра;
- выход эффекта за границы исходного изображения;
- зависимости от соседних кадров;
- cache invalidation после изменения параметров;
- отмену рендера;
- повторный рендер.

### Color Management

Проверять заявленные:

- Working Space;
- Linear Working Space;
- OCIO;
- HDR / extended range;
- CPU/GPU consistency.

### CPU / GPU Parity

Если есть CPU и GPU implementations:

- заранее определить допустимую погрешность;
- сравнивать численно, а не только визуально;
- проверять alpha и color channels;
- учитывать near-zero и extended-range значения;
- сохранять difference output для значимых расхождений.

Bit-exact совпадение требовать только там, где это соответствует алгоритму и требованиям.

GPU fallback и отсутствие поддерживаемого GPU должны иметь определённое поведение.

---

