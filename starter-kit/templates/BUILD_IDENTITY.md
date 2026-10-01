# Build Identity Contract

Цель: доказуемая цепочка

`source state → Build ID → packaged artifact → installed artifact → actually loaded code`.

## Source record

Фиксировать:

- Git commit;
- clean/dirty;
- digest релевантных source files;
- target architecture;
- build profile/configuration;
- compiler/toolchain versions;
- значимые build flags/environment.

Build ID должен меняться, если меняется релевантный source state, target, profile, toolchain или значимые build flags.

## Dirty builds

Dirty build:

- явно маркируется;
- допустим только для внутренних экспериментов;
- не считается release candidate;
- не должен получать release PASS.

## Artifact seal

После всех post-processing steps:

- hash production payload;
- hash final package/archive;
- сохранить manifest;
- проверить permissions/executable bits;
- запретить изменение signed/tested candidate in place.

## Runtime identity

Где возможно, runtime должен сообщать Build ID/commit. Для native plugin полезно дополнительно фиксировать loaded image path/UUID/PID.

Installed file на диске не доказывает loaded identity.

## Required negative tests

Автоматизация Build Identity должна по возможности иметь тесты, доказывающие, что она отвергает:

- modified payload after sealing;
- modified package;
- stale metadata;
- dirty release metadata;
- mismatched binary/manifest;
- unexpected extra source file;
- symlink/path traversal в source snapshot;
- ambiguous/stale build output.
