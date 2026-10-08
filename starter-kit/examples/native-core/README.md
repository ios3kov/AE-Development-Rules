# Offline native core example (unreleased)

Original C++17 teaching API, independent of Adobe SDK. No install or host/device run. Requires Python 3.11+ and an available `clang++` or `g++`:

```sh
python3 starter-kit/scripts/check_native_examples.py
python3 starter-kit/scripts/check_native_examples.py --sanitizers
python3 -m unittest discover -s starter-kit/tests -p test_engineering_execution.py -v
```

Sanitizers explicitly request compiler/runtime support: failure remains FAIL/BLOCKED, not silently disabled. Missing compiler is BLOCKED (exit 2). The ordinary run is compiler independent; sanitizer availability is a separate result.

`native_core.hpp` is the tested source: overflow-safe stride/capacity checks before any buffer offset; strong frame/rate/seconds types; explicit RGBA8 conversion; unique ownership with move and error-path release; bounded strict decimal parser; cancel/reset state transition contract. `check_native_core.cpp` runs 20,000 iterations with seed `0xAEE2026`: parser roundtrip, random byte fuzz, geometry bounds/offsets, numeric time conversion inverse and state cancellation invariants. Malformed/overflow/nonfinite cases are explicit. Finite random input coverage is bounded, not exhaustive fuzz certification.

The runner compiles exactly the same source twice. `DEMONSTRATE_ORIGINAL_DEFECT` selects the preserved `x > width` defect; the same regression assertion for `x == width` in a padded row exits 1 at `REGRESSION:x-equals-width`. Corrected `x >= width` source passes. The original variant runs only the regression case. A compiler/setup failure does not count as red detection. This controlled mutation proves fixture test sensitivity, not reproduction of any product's original defect.

`invalid_units.cpp` deliberately calls frame conversion with `Seconds`: compilation must fail naming the incompatible types. It is a negative API example, not a standalone build target. Correct API calls are compiled in the main harness. Reports bind actual source digests/compiler, iterations, sanitizer selection and observed exits.

No threading stress/TSAN, AE suites/checkout/checkin, MFR/SmartFX, alpha, 16bpc channel maximum, HDR/color management or native host runtime is tested here. These remain risk-scoped checks in the existing standard, with real AE results recorded separately. The fixture's RGBA8 maximum of 255 says nothing about Adobe 16bpc or float scale. All reports say `sdk_certified:false` and `host_status:NOT_RUN`.

Research provenance/licensing: [engineering sources](../../../docs/ENGINEERING_EXTENSION_SOURCES.json). No upstream code, prompts, expressions or assets were copied, installed or executed.
