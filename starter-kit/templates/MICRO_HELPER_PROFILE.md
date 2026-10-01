# Micro-helper Profile

Для однофайлового/малого AE helper с низким риском.

## Scope check

Все пункты должны быть true, иначе использовать Standard или Release-Critical:

- [ ] Небольшой локальный script/helper
- [ ] Нет network
- [ ] Нет helper/background process
- [ ] Нет installer/update mechanism
- [ ] Нет project-data migration
- [ ] Нет массовых destructive filesystem operations
- [ ] Нет performance-critical render path
- [ ] Ошибка не может повредить пользовательские файлы/проекты beyond ordinary Undo-safe mutation

## Minimum checks

- [ ] Source сохранён в Git / однозначно versioned
- [ ] Syntax/parser sanity-check
- [ ] Реальный AE smoke test основного сценария
- [ ] Негативный/safe case для отсутствующего или неверного context, где применимо
- [ ] Короткий Test Record / status
- [ ] Известные ограничения записаны

## Escalation triggers

Перевести в Standard / Release-Critical при появлении state, files/network/helpers, installer, публичного distribution, сложной async logic или существенного user-data risk.
