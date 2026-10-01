# AE Runtime Test Safety

Любой автоматический тест, который может открыть/закрыть проект, изменить composition, запустить render или управлять After Effects, должен быть fail-closed.

## Ownership before mutation

До первого destructive/mutating действия тест обязан доказать, что состояние принадлежит тесту.

Допустимые признаки ownership:

- специально созданный test project/fixture;
- уникальный Test Run ID;
- уникальный test workspace;
- явно подтверждённый пустой/несохранённый test host state;
- известный test-owned output path.

Если ownership не доказан — **BLOCKED**, без попытки «починить» состояние.

## Refuse when user work may exist

Тест не должен автоматически:

- закрывать сохранённый или dirty пользовательский project;
- заменять текущий project новым;
- убивать After Effects при timeout;
- удалять неизвестные файлы;
- очищать общие caches/preferences;
- использовать фиксированный общий `/tmp` путь;
- продолжать после неизвестного результата dirty-state/ownership query.

## Workspace

Использовать уникальный script-owned workspace, например через:

```sh
./starter-kit/scripts/create-owned-test-workspace.sh
```

Не использовать symlinked workspace root. Автоочистка разрешена только внутри доказанно принадлежащего текущему Test Run каталога.

## Cleanup

Cleanup может закрывать/удалять только то состояние, которое тест создал и продолжает однозначно идентифицировать как своё.

Если current project/state неожиданно изменился — оставить его нетронутым и завершить тест как BLOCKED/FAIL.

## Timeout

Timeout:

- не является PASS;
- не разрешает kill host;
- не разрешает закрытие неизвестного project;
- должен сохранить логи/evidence и завершиться как BLOCKED или FAIL согласно сценарию.

## Test oracle

Перед pixel/visual acceptance доказать корректность capture path. Успешное создание PNG/файла не доказывает корректность изображения.
