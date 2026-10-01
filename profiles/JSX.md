# JSX / ScriptUI Profile

Этот файл — навигатор, а не дубликат нормативных правил.

Для JSX / ScriptUI применяются:

- [Process Core](../core/PROCESS.md) — выбранный Risk Profile и Evidence/Regression rules;
- [Engineering Core](../core/ENGINEERING.md) — safety, compatibility, documentation, dependencies по scope;
- [Tools / Panels Runtime Profile](TOOLS.md) — lifecycle/UI/Undo/state/file-system checks;
- [Release / Distribution Profile](RELEASE.md) — только для Validation/Release delivery gates;
- [Micro-helper template](../starter-kit/templates/MICRO_HELPER_PROFILE.md) — минимальный профиль, если eligibility соблюдена.

Source-only JSX не получает OS signing requirement без executable installer/helper.
