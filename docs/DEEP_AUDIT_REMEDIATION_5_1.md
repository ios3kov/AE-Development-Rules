# Исправление глубокого аудита: 5.1.0

## Исторический этап локального исправления

Исходный published baseline: 5.0.0 / `8d88b19afea726b7c79988c5f6958f65d13995ba`. Начальная revision этой работы: `f3214a1f8447af54b156fe31d350b0753a4c112f`, clean. Отдельная ветка: `fix/deep-audit-5.1.0`. Разрешены изменения, локальные проверки и commit. Merge, push и публикация в этот этап не входят.

## Scope и совместимость

Исправить D01–D10 из [журнала](DEEP_AUDIT_BACKLOG.md), добавить I01–I04. Сохранять старые отчёты, published tag и принятые project baselines. Не добавлять обязательных AE проверок для каждого локального documentation edit и не выдавать подготовку fixtures за запуск модели/AE.

5.1.0 — minor candidate: исправления enforcement существующих правил и новые необязательные рекомендации/возможности. I01 поясняет уже существующую границу partial failure; reconcile/deduplication описываются как SHOULD, без нового универсального протокола. Новые форматы metadata snapshots требуют явной tooling migration; старые Evidence не переписываются. Новая версия не становится stable release до отдельной публикации.

## План и приёмка

| Пункт | Изменение / критерий приёмки | Статус |
| --- | --- | --- |
| D01 | JSX/helper выбирают runtime минимум, CEP/UXP Critical — code safety; все canonical sections доступны в карте, feature overlays сохраняют соразмерность. | LOCAL VERIFIED |
| D05/D06 | Отсутствующие/неправильные task overlays, undefined selected IDs и linked canonical sources отвергаются до чтения/генерации. | LOCAL VERIFIED |
| D03/D10 | Sparse/inherited items отвергаются; JSON structural uniqueness не зависит от порядка object keys, сохраняет array order. Проверить direct API и JSON CLI. | LOCAL VERIFIED |
| D02/D07 | Изменения metadata/types/empty directories наблюдаются; special POSIX bits включены или явно исключены; старые records не получают более сильного verdict. | LOCAL VERIFIED |
| D04/D08/D09 | Whitespace-only N/A блокируется; строгий UTF-8 decode принимает literal U+FFFD и сохраняет byte hashes; version check сопоставляет authoritative full field. | LOCAL VERIFIED |
| I01 | Unknown IPC outcome, recovery/retry guidance и выбор IPC feature overlay. | LOCAL VERIFIED |
| I02 | Errata с affected baseline, impact, temporary control и unpublished corrected version; frozen baseline сохраняется. | LOCAL VERIFIED |
| I03 | Пять AE-specific evaluation cases с held-out variants и observer isolation; actual model/AE NOT RUN. | LOCAL VERIFIED |
| I04 | Три кратких source-linked decision examples: JSX Undo, IPC, native render; declared target identity и Evidence limits. | LOCAL VERIFIED |
| Итог | Focused regressions, self-test доступных платформ, static scanner и review diff; окончательная clean revision и результаты связываются внешним verification record. | LOCAL VERIFIED |

## Проверки и передача

До выполнения результаты не объявляются PASS. Windows/PowerShell, actual model, AE runtime и новый remote CI остаются NOT RUN, пока нет соответствующих запусков. Исправления инструментов проверяются в owned temporary fixtures; macOS command stubs проверяют wrapper contract, а не notarization/Gatekeeper.

## Внесённые изменения и Evidence

- D01/D05/D06: §§1–41 представлены в generated reading map; JSX/helper runtime и Critical code-safety minima проверяются loader. Все task overlays обязаны иметь правильный canonical source/section; undefined selected IDs и linked source/ancestor/root отвергаются. Feature contexts необязательны, права не расширяют. Нормативный scope micro-helper остаётся соразмерным.
- D03/D10: dense own array validation и bounded structural uniqueness, независимая от object key order. Actual JSON CLI reject для обоих видов Evidence duplicate; single-item control сохраняет NOT_ASSESSED readiness. Path/hash/revision проверки не ослаблялись.
- D02/D07: новые metadata snapshots/records v2, POSIX mask 07777, Windows emulated scope. Forbidden chmod, empty directory/type change и special directory bit invalidate наблюдение. Старые records явно отвергаются новым verifier; не переписываются.
- D04/D08/D09: whitespace-only (включая Unicode spaces) N/A rejected до platform commands; literal U+FFFD/Unicode/BOM accepted, malformed UTF-8 rejected с original byte hashes. VERSION/authoritative README/current CHANGELOG проверяются полностью, corruption cases reject.
- I01/I02/I04: scoped IPC recovery SHOULD guidance и stable marker IPC-RECOVERY-001; errata с affected published baseline/control/unpublished correction; три source-linked decision examples, без выдуманных SDK revisions и runtime Evidence.
- I03: 25 scenarios / 31 states, пять development и пять held-out AE variants. В восьми pure/mock cases исходный defect вызывает failure, illustrative correction проходит неизменённые checks. Два loaded-identity cases проверяются observer rubric, не тестом реального AE. Permissions/oracle separation и `agent_behavior: NOT ASSESSED` сохранены.

Первый focused прогон: 29/29 PASS. После AE fixtures: 30/30 PASS (contracts 8 + follow-up 9 + deep-audit 13). Полный local self-test: PASS, доступные Node/POSIX/macOS checks; hardening 13 PASS и 2 Windows-only SKIPPED, contracts 8 PASS, follow-up 9 PASS, deep-audit 13 PASS. После review refinements affected regressions выполнены повторно. Полные logs и hashes сохраняются вне standard checkout; итоговый clean commit проверяется отдельным final record. Старые audit reports/reproduction JSON сохранены без изменений.

При добавлении parent-directory chmod case два review прогона выявили ошибку самого теста: снятие owner search bit мешало observation/cleanup и маскировало результат. Тест исправлен: менять group-write bit, восстанавливать исходный mode в finally. Только два собственных temporary workspace из этих logs восстановлены/удалены по точным путям. Последующий affected suite: 13/13 PASS; полный reviewed self-test: PASS, 131 файлов. Неудачные logs сохранены как superseded Evidence, не переписаны в PASS.

Precommit static code scan: exit 0, no findings in scanned scope, 121 текстовый файл, omissions пуст, release_readiness not_assessed. Это не проверка runtime/модели. Исторические отчёты/Evidence и SOURCES.md побайтно сверены с начальной revision; состояние ledger — 10 FIXED_LOCAL и 4 IMPLEMENTED. Сверка remote refs подтвердила неизменные main/peeled v5.0.0 `8d88b19afea726b7c79988c5f6958f65d13995ba` и tag object `9079bc267c3c0393b31ced116af192b43d2dc580`.

## Review и ограничения

Проверены actual diff и migration: не меняются Product Spec flags/route output keys, Risk/Delivery semantics, adopted-baseline/permission boundaries, pre-handoff phases и Evidence status taxonomy. Source files остаются canonical; schemas manifest 3/project-record 1 сохраняются, metadata v2 migration явная. Нет нового universal MUST/gate. Static scanner не устанавливает release readiness. PowerShell/Windows, remote candidate CI, actual model и AE runtime — NOT RUN. SOURCES.md и original vendor verification dates не изменены. Current main и published tag сохраняются; merge/push/release не выполнены.

## Переход к выпуску — 2026-10-02

После завершения локального этапа пользователь явно разрешил выпуск: «делай релиз». Для этого этапа разрешены push, PR/merge, tag и GitHub Release. Прежний main `8d88b19afea726b7c79988c5f6958f65d13995ba` сохранён отдельной remote/local backup-веткой и локальным Git bundle; published v5.0.0 не изменяется.

Текущие README/VERSION/CHANGELOG и migration notes подготовлены к 5.1.0. Публикация требует exact-head PR CI и exact-commit main CI на Linux/macOS/Windows, затем annotated tag, сверку архивов с Git tree и повторное скачивание uploaded assets. Итоговые SHA, runs, checksums и disposition записываются в `release-evidence.json` у [GitHub Release v5.1.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v5.1.0). Исторические результаты выше относятся к своему этапу и не заменяют эти проверки. Actual model/AE остаются NOT RUN.
