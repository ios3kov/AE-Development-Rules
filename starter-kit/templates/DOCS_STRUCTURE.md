# Recommended Documentation Layout

```text
docs/
├── ARCHITECTURE.md
├── STATUS.md
├── COMPATIBILITY.md
├── USER_GUIDE.md
├── TEST_RECORDS/
│   └── <test-records>.md
├── RELEASES/
│   └── <release-records>.md
├── RETROSPECTIVE-<version>.md
└── AE_ENGINEERING_KNOWHOW.md   # when reusable AE knowledge exists
```

## Canonical source

Prefer Markdown or another text/diff-friendly format in Git as the engineering source of truth.

For continuing AI-assisted repository work, embed [AI task state](AI_TASK_STATE.md) in the existing `STATUS.md` or equivalent canonical record. Link product decisions, actual authorization sources and Evidence; restore current Git/environment state on resume. Do not create duplicate status/spec files solely to fit a template.

Sphinx, MkDocs, Wiki or a public site may render/publish the docs, but define which source is canonical and keep generated/public copies synchronized.

## Public vs internal

Keep secrets, personal data, private paths, crash dumps and sensitive evidence out of public documentation. Public user docs and internal engineering evidence do not have to live in the same publication surface.
