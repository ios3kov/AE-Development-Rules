# Numerical render fixtures

Four 4×4 straight-alpha, linear-sRGB, RGBA32F numerical fixtures cover transparent color, fractional alpha gradients, negative/extended float colors and frame edges. They are mathematical inputs, not screenshots or evidence from After Effects. An AE adapter should create a controlled test project or map equivalent buffers while preserving declared color/alpha/bpc semantics.

`edge-roi.json` marks border behavior. It does not establish an ROI checkout contract; the host test must vary actual ROI/downsample/render scale and compare the expected full-frame or cropped result.

Use `node starter-kit/scripts/compare-render.mjs reference.json actual.json 0.0001 new-diff.json` only when 0.0001 is the product's approved absolute tolerance in the declared numeric units. There is no universal tolerance. Dimensions, channels, color space, alpha convention and bit depth must match; conversions are the caller's responsibility. Nonfinite inputs fail closed. The report includes channel errors and RMSE and preserves a full difference array when requested.

Test the capture/export adapter with a known control image before using it as an oracle. File creation does not prove correct pixels. Run target-host tests separately for 8/16/32 bpc, working space, premultiplication, MFR/SmartFX and CPU/GPU modes actually claimed by the product.
