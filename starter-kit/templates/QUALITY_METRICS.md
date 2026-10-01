# Quality Metrics

Use metrics to find regressions and improve the process, not to score people.

## Period

- Product:
- Version / milestone:
- Period:
- Build / release scope:

## Metrics

| Metric | Definition | Current | Baseline / previous | Trend | Action |
| --- | --- | ---: | ---: | --- | --- |
| Escaped defects | Bugs confirmed after release | <n> | <n> | <up/down/stable> | <action> |
| Regression failures | Previously working required cases that failed | <n> | <n> | <trend> | <action> |
| Flaky tests | Tests with non-deterministic outcomes | <n/%> | <n/%> | <trend> | <action> |
| Crash / hang incidents | Confirmed runtime crash/hang cases | <n> | <n> | <trend> | <action> |
| Performance regressions | Benchmarks outside accepted baseline | <n> | <n> | <trend> | <action> |
| Critical/high open defects | Unresolved release-relevant defects | <n> | <n> | <trend> | <action> |
| Reopened bugs | Bugs reopened after claimed fix | <n> | <n> | <trend> | <action> |
| Time to confirmed fix | Reproduction → verified fix | <time> | <time> | <trend> | <action> |
| Manual release steps | Required manual steps still suitable for automation | <n> | <n> | <trend> | <action> |

## Rules

- Do not use LOC, commit count or test count as a standalone quality metric.
- Define every metric before using it.
- Keep the same measurement method across periods.
- Do not create a numeric release gate without an agreed reason and threshold.
- Never improve a metric by hiding FAILs or deleting difficult tests.
