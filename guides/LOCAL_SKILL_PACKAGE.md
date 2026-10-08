# Проверка локального исполняемого skill-пакета

Подключается для executable package, не для закрытого remote MCP и не для простого чтения текста. Требования находятся в [§43](../core/AGENT_SKILLS.md); здесь — ограничения текущего adapter.

- Parser читает распространённые scalar/multiline формы стандартного SKILL.md; неподдержанный валидный YAML означает BLOCKED для этого parser. Не создавать собственный обязательный dialect. Registry/policy — внешний adapter.
- Import принимает уже полученный owned ZIP: limits archive bytes/entries/unpacked bytes, новая staging область, запрет traversal/absolute/backslash/drive paths, links/special types/duplicates/case collisions. Download и исполнение отсутствуют.
- Inventory включает файлы и empty/nonempty directory paths; ACL/xattrs/ownership/directory permissions не аттестуются. Если они нужны операции, проверять отдельно.
- Source checkout/export Evidence устанавливает provenance; source SHA внутри metadata этого не доказывает. Hash одного SKILL.md/lockfile/Git tree не заменяет полный byte inventory.
- Index/pointer разных агентов ссылается на один canonical package/registry; не создавать второго manager тех же files. Удаление указателя не удаляет shared package.
- Raw scan report хранится вне sealed package. Current admission, scan, lifecycle history и redacted summary связываются existing Evidence ID. Защищённые policy/pins не берутся из candidate.

Пример использования и CLI: [AGENT_SKILLS_TOOLS](../docs/AGENT_SKILLS_TOOLS.md). Ограничение инструмента не становится универсальным условием для всех MCP/API.
