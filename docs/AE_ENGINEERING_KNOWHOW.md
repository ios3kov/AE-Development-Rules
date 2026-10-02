# Reusable AE rendering and validation know-how

Added 2026-10-02 following the ElasticGridFX performance/release cycle. These are
engineering notes, not additional mandatory rules, a new supported-platform matrix
or certification of another product. They explain ways to implement existing
Engineering §§19–21/25/32 and Release identity/evidence requirements.

## Provenance and confidence

The source host observations used AE25.6x101, macOS26.6.2, Apple Silicon M1 Pro,
16 GiB. Source artifact `f611312bd7b76ebe5bc5f2bd8b48b44f50c0c761`, Build ID
`EGFX-6147dc406abc596e7f2d1b60`. Source records below are pinned to documentation
commit `156bccd56d748f45e2cb5a1176a96d1b9dd0c427`; candidate identity is separate.
Raw user projects, crash reports and media remain local.

Confidence: PROVEN = demonstrated in the named scope, OBSERVED = limited
observation, USER-REPORTED = user acceptance without independent reproduction,
UNVERIFIED = unresolved. Outcome (accepted/rejected) and Test Status are separate.
Apply these notes only after checking the target product/host assumptions.

## 1. Identify the route actually exercised

**PROVEN in source host observations; outcome accepted.** Optimizing an older
renderer did not by itself accelerate a newer plane-render dispatch. Resolve
which callback/bridge the exact installed candidate invokes before profiling.
Use bounded instrumentation for attribution and ordinary builds for acceptance.

Reusable approach: record source/build/package identity, loaded image identity,
fixture geometry and requested route. Record observed route separately from a
request. An instrumented callback duration is not normal Render/RAM Preview time.
[Source route and attribution](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-host-attribution-2026-10-02.json).

## 2. Preserve sampling semantics while caching repeated work

**PROVEN for separable plane fixtures; outcome accepted.** Exact per-axis mapping
and a call-local four-row Bicubic cache can reuse computations while preserving
channel arithmetic. General perspective/nonfinite/unsupported cases need an
explicit unchanged path. Identity shortcuts can alter NaN, Inf or negative-zero
behavior even when finite fixtures appear equal.

Reuse only where separability and row reuse hold. Keep scratch ownership local
to the render call; source review alone is not MFR certification. Compare external
before/after pixel bytes, padding, all actual depths, exceptional floats,
cancellation and independent-frame concurrency. Do not import the source
product's speedup into a different renderer.
[Correction and comparison history](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-resume-2026-10-01.md),
[exceptional-float comparisons](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-plane-nonfinite-comparison-2026-10-01.json).

## 3. Match the toolchain and the exported-pixel contract

**PROVEN for recorded paired outputs; outcome accepted.** Original-artifact and
new-toolchain outputs showed small color differences; matching-toolchain unchanged
source versus optimized source was exact. Preserve both results. This isolates
an optimization comparison, but does not prove the cause of an old-artifact delta.

Fix source/build/settings identity, source fixture hash, AE working space,
linearization, alpha convention, output precision and decoder behavior. Native
32-bpc input exported to straight RGBA16 PNG is an RGBA16 output comparison,
not universal preservation of all float/HDR values. Calibrate the decoder.
[Matrix and queue-chain evidence](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-host-matrix-2026-10-02.json).

## 4. Separate performance quantities and retain outliers

**PROVEN for ordinary exports; OBSERVED for UI-bracketed intervals; outcome accepted.**
Native sampling, callback attribution, AE process/export time, full-cache arrival,
first-playable latency and onscreen playback answer different questions. Total
export includes startup, polling and PNG work. A composition-frame-rate label
is not cache-fill or input-to-display latency.

Use matching fixtures, depth/quality, viewer zoom and actual Preview preset.
Viewer Full does not establish Preview Full. Keep raw samples, warmup policy,
fixed-order/capture/cache limitations and inconclusive pairs. Report interval
bounds as bounds; later preset readback cannot certify an earlier series.
[Ordinary Render comparison](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-host-render-2026-10-02.json),
[all Preview intervals](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-host-preview-intervals-2026-10-02.json).

## 5. Do not equate launcher success or non-reproduction with a fix

**PROVEN completion-check failure mode; crash cause UNVERIFIED.** A launcher exited0
while only19/60 frames existed and the matching render process had aborted.
Verify expected frame coverage, independent decode and process/image identity.
An MFR-requested-ON setting does not establish observed callback concurrency.

Use a bounded hypothesis-driven retry, retaining the original failure, control,
candidate and enabled/bypass outcomes. No plugin frame in a crash stack does not
exonerate a plugin. If failure does not recur, record NOT REPRODUCED and separate
issue disposition from root cause, shipping fix and stability certification.
[Original incident](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/performance-host-mfr-2026-10-02.json),
[bounded retry/closure](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/mfr-closure-retry-2026-10-02.json).

## 6. Bind distribution proof to the downloaded candidate

**PROVEN on one existing Mac; clean-environment acceptance USER-REPORTED.** Check
public archive hash, extracted payload, retained quarantine, signature identity,
single active install and exact loaded image. Preserve a rollback copy outside
plugin roots. Do not transfer an existing-machine result to all clean machines.
Ad-hoc distribution is permitted under rules6.0.0; it does not promise absence
of macOS warnings or authorize removing quarantine/security protections.

Separate package revision, embedded plugin version, source SHA, immutable asset
and public release state. Publishing updated repository instructions without
rebuilding the tested payload preserves identity, but immutable archived README
text may need explicit supersession in current user guidance.
[Downloaded install/project evidence](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/public-install-project-check-2026-10-02.json),
[human acceptance](https://github.com/ios3kov/ElasticGridFX/blob/156bccd56d748f45e2cb5a1176a96d1b9dd0c427/docs/release-user-acceptance-2026-10-02.json).

## Reuse and tooling

These are reusable validation patterns, not an Adobe SDK/API reference. Existing
source implementations include `render_observation.py`, `live_identity.py` and
`perf_fixture_runner.py`. Review process guards, fixture ownership, paths,
output format and host versions before adapting them. No new executable tooling,
wrapper schema, adoption baseline or mandatory requirement changes in this note.
