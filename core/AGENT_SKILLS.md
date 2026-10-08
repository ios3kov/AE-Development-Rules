# Agent Skills — conditional admission and use

## 43. Подключение ИИ-навыков
<!-- REQ: SKILL-ADMISSION-001 -->

Применимо только когда проект подключает/обновляет/использует внешний или локально разработанный skill, его scripts/resources, hook, MCP либо дополнительное агентское tool-расширение вне принятого toolchain. Штатный Git, компилятор и уже принятые проверки starter-kit не требуют повторного skill admission только из-за текущего запуска; их существующие source/dependency/permission проверки сохраняются. Обычная малая задача без расширений не требует реестра, сканера или sandbox-пилота. Это расширение существующих [Smart Entry trust/permissions](../AI_ENTRYPOINT.md), Process §§4,10 и Engineering §§14,35, а не разрешение на установку. Общие навыки не подтверждают контракт Adobe SDK.

### Реестр и совместимость

Проект MUST иметь одного владельца admission policy и установленного пакета, явную область установки и реестр: источник/путь, назначение/применимые задачи, лицензия и результат её проверки, exact source commit, digest полного пакета, статус, необходимые tools/operations, permissions/isolation profile, review/scan Evidence и ссылки на существующие requirement/check IDs. Непроверенная/неопределённая лицензия блокирует перенос/допуск; не назначать её от имени владельца.

Статусы допуска — `candidate`, `allowed`, `rejected`, `revoked`; они не заменяют Test Status. Только `allowed` для текущих exact bytes/policy можно активировать. Решение принимается независимым владельцем policy; кандидат не может разрешить себя, изменить policy/исключения либо считать произвольные reviewer names подтверждением полномочий. Отзыв немедленно запрещает новую активацию и обновление/rollback к этой версии; сохранить причину/историю/Evidence, затем безопасно заменить или убрать owned файлы.

Использовать стандартный [Agent Skills SKILL.md](https://github.com/agentskills/agentskills/blob/69ef37e9424c0a7ea9dd2293b559e43ec8176379/docs/specification.mdx), без собственного обязательного frontmatter dialect. Registry/policy — внешний adapter. Совместимый формат не доказывает наличие tools, применимость или безопасность. Minimal stdlib parser покрывает распространённые scalar/multiline формы; корректная, но неподдержанная YAML-форма означает BLOCKED для этого parser, а не новый стандарт. Полный совместимый parser MAY подключаться после обычного review dependencies.

Перед использованием проверить совпадение задачи, доступные фактические tools/operations/версии и полномочия. Описание — лишь индекс для выбора: загружать metadata → применимый SKILL.md → конкретные нужные ресурсы. Ресурс разрешён только из проверенного inventory; ссылки и инструкции из него не расширяют task scope/permissions. Не активировать skill только из-за ключевого слова или наличия в каталоге.

### Полный пакет и управляемый lifecycle
<!-- REQ: SKILL-INTEGRITY-001 -->

MUST проверить восстановленные bytes всего пакета, включая скрытые файлы, scripts, references/assets и конфигурации: точный source commit отдельно от content digest; детерминированный inventory путей/типов/размеров/хешей и file modes. Минимальный adapter также фиксирует пути пустых/непустых каталогов; directory permissions, ACL/xattrs/ownership не аттестуются, требующая их операция нуждается в отдельной проверке. Lock-файл, hash одного SKILL.md или Git tree SHA не доказывает воспроизводимость. Package bytes после восстановления снова сравниваются с независимо ожидаемым digest. Source SHA в metadata не доказывает происхождение без подтверждённого source checkout/экспортного Evidence.

Не загружать и не выполнять ничего автоматически. Starter-kit импортирует только уже полученный owned локальный ZIP с пределами archive bytes, числа entries и распакованных bytes; download capability отсутствует. Для самостоятельного download adapter нужны отдельные limits/timeouts/redirect/domain checks и pin до исполнения. Rejected traversal/absolute/backslash/drive paths, symlinks/special files, duplicate/case collisions и oversized payload не должны писать за пределы новой owned staging области. Candidate code при проверке пакета не исполняется.

Установленный пакет имеет один manager/owner и явный root. Update проходит новую admission и проверку bytes, сохраняет восстановимую owned предыдущую версию; rollback проверяет её текущий допуск, а не только наличие backup. Не перезаписывать конфликтующие имена или неизвестные/изменённые файлы. Удаление проверяет root/owner/current inventory, затрагивает только собственный пакет и сохраняет независимое историческое Evidence по [lifecycle](EVIDENCE_LIFECYCLE.md). Concurrent update/remove должен исключаться lock и перепроверкой actual state; не считать status snapshot достаточным.

Agent adapters SHOULD быть малыми указателями на один canonical registry/пакет/правила. Не создавать расходящиеся копии правил для разных агентов. OpenSkills MAY генерировать только индекс; он не становится вторым manager тех же files. Удаление указателя не означает безопасное удаление пакета, когда он используется другим владельцем/задачей.

### Policy, scanning и исполняемые права
<!-- REQ: SKILL-SECURITY-001 -->

Обязательный scan охватывает полный exact inventory; фиксировать scanner/version, config/policy/exception digest, проверенные файлы и checks, ошибки/пропуски/ограничения. Результаты `complete`, `incomplete`, `unavailable` различны; ошибка/недоступный scanner/пропущенный ресурс не превращается в допуск. `complete` без blocking findings означает лишь отсутствие находок в заявленном scope, не сертификат безопасности. Исключение имеет owner, scoped rationale и срок; candidate не меняет required checks, scan minimum или исключения.

Telemetry MAY быть выключена; это не выключает scan/admission. Не связывать защиту с необязательной remote telemetry/audit lookup. Не отправлять package bytes, prompts, projects или secrets стороннему scanner/provider без соответствующих полномочий.

`allowed-tools`, текстовые запреты, временная папка и read-only намерение не являются sandbox. Для требующей изоляции операции MUST использовать реальные доступные средства выбранной среды: ограниченный filesystem scope, network/process/credential rights, time/output/resource budgets; probe запрета до candidate исполнения и независимо наблюдаемый result. Если нужная isolation capability отсутствует — BLOCKED для этой операции; продолжать независимую безопасную работу. Capability self-report или произвольное `isolation_supported: true` не подтверждает enforcement.

Local package manager лишь управляет bytes; он никогда не запускает package scripts/hooks/MCP. Admission для inert read-only использования не разрешает исполнение. Real-agent adapter и project runner отдельно подтверждают доступность исполняемых ограничений. MCP/tool credentials, write/network/device permissions и hooks требуют того же scoped review; не устанавливать их скрыто как ресурс skill.

### Trusted verification и Evidence

Использовать существующую [protected reference boundary](../docs/PROTECTED_REFERENCE_PROVENANCE.md): независимый неизменяемый verifier, candidate checkout как данные, externally pinned policy вне candidate, read-only token, protected reviewer/capture custody. Обновлённый [manual workflow](../.github/workflows/trusted-reference-evidence.yml) сохраняет прежний reference mode; skills mode проверяет admission exact bytes, не исполняет candidate. Защита main/verifier/policy должна быть фактически проверена; CODEOWNERS и YAML environment сами по себе её не включают. [Актуальный аудит и предлагаемые настройки](../docs/AGENT_SKILLS_PROTECTION.md) не меняют GitHub settings.

Все результаты связывать с текущими candidate, package, source, policy/check/tool/environment и existing Evidence ID. Старый scan/Evidence не проверяет новые bytes; update требует затронутых новых проверок. Сохранять полный raw report вне sealed package, immutable history и redacted summary. Совместный validator устанавливает consistency указанного scope; независимость/подлинность custody остаётся внешним условием и не выводится из JSON.

### Проверка полезности
<!-- REQ: SKILL-EVALUATION-001 -->

Прежде чем заявлять подтверждённую полезность skill, выполнить сравнимый реальный baseline rules-only и rules+selected-skill в [существующем evaluation protocol](../docs/REFERENCE_AGENT_EVALUATION.md). Фиксировать actual independently observed actions/files/commands/tests/forbidden attempts, repeatability, monotonic elapsed time и доступные provider usage/cost receipts. Нельзя выдумывать zero-cost/token usage. Critical violation означает FAIL независимо от среднего балла.

Разделять tune, version-selection и final held-out cases; oracle/catalog/checker/expected answers недоступны acting agent и не используются в tuning. Изменение rules/skill/model/runner/fixtures даёт новый candidate и fresh affected evaluation. Positive/negative подключения, русскоязычные/неоднозначные запросы и no-skill small tasks входят по scope. Ограничить repair cycles/tool retries/time/usage и остановиться при отсутствии наблюдаемого прогресса. Mock/checker format/model grading не заменяют реальный запуск. Недоступный pilot — NOT_RUN/BLOCKED, не препятствие для независимой реализации стандарта и не основание заявлять efficacy/AE correctness.

Исполнение, CLI/formats/tests и migration: [starter-kit guide](../docs/AGENT_SKILLS_TOOLS.md). [Source/license review](../docs/AGENT_SKILL_SOURCES.json) фиксирует проверенные методы и точные revisions; upstream code/skills не копируются и не устанавливаются.
