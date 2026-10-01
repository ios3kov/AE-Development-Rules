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

