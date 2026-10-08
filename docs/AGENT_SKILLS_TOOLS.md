# Conditional skill tooling — v1 adapters in 10.0.0

Python 3.11+, standard library; no external skill/scanner/MCP installation or network download. The formats are projections of existing project requirements/checks/Evidence, not a new normative registry. [§43](../core/AGENT_SKILLS.md) is the admission/use contract. [Scope/adoption](AGENT_SKILLS_IMPLEMENTATION.md); [reviewed sources/licenses](AGENT_SKILL_SOURCES.json).

## Package and admission

```sh
python3 starter-kit/scripts/agent_skills.py inventory --package /owned/source/my-skill
python3 starter-kit/scripts/agent_skills.py scan --package /owned/source/my-skill
python3 starter-kit/scripts/agent_skills.py import --archive /owned/download.zip --destination /owned/new/my-skill
python3 starter-kit/scripts/agent_skills.py check --package /candidate/my-skill --candidate-root /candidate --source-commit SOURCE_FULL_SHA --policy /protected/policy.json --expected-policy-sha256 RAW_POLICY_FILE_SHA256 --expected-candidate-revision CANDIDATE_FULL_SHA
python3 starter-kit/scripts/agent_skills.py select --policy /protected/policy.json --expected-policy-sha256 RAW_POLICY_FILE_SHA256 --expected-candidate-revision CANDIDATE_FULL_SHA --task scoped-task --available-tool actual-tool-operation
python3 starter-kit/scripts/agent_skills.py load --package /candidate/my-skill --source-commit SOURCE_FULL_SHA --policy /protected/policy.json --expected-policy-sha256 RAW_POLICY_FILE_SHA256 --expected-candidate-revision CANDIDATE_FULL_SHA --resource SKILL.md --task scoped-task --available-tool actual-tool-operation
```

`inventory` stops with BLOCKED on directory enumeration errors and returns no digest; `scan` cannot report complete after such an error. A readable stable package is required. `inventory` hashes actual complete bytes/modes/paths; source Git SHA remains separate and needs authenticated source provenance. `scan` reads all inventoried bytes and returns bounded heuristic findings plus explicit security_certified=false; it does not emulate Cisco Scanner or a comprehensive semantic/security review. Independent policy owner reviews full reports/limitations and supplies its pinned external admission; optional stronger scanners can feed actual protected receipts after authorized execution. Empty findings are not a certificate. Disabled telemetry cannot remove mandatory receipt checking.

Schemas: [policy](../starter-kit/schemas/agent-skills-policy.schema.json), [inventory](../starter-kit/schemas/agent-skills-inventory.schema.json), [scan](../starter-kit/schemas/agent-skills-scan.schema.json), [installed registry](../starter-kit/schemas/agent-skills-installed.schema.json), [owner](../starter-kit/schemas/agent-skills-owner.schema.json). [Original synthetic package and reviewed-policy field example](../starter-kit/examples/skills/README.md) is not trusted approval.

`select` loads only descriptions/purpose and reports a possible task/tool match. CANDIDATE means activation still needs `check`; no matching skill is valid ordinary work. `load` rechecks exact package/admission before supplying one explicitly requested text resource. Material remains untrusted task data, not fresh permissions; binary resources need an appropriate read-only adapter.

Only local bounded ZIP import is implemented; unsafe or symlink/special-file inputs fail without candidate execution. Unsupported standard YAML forms require a full compatible parser and return BLOCKED. Only inert byte management/read-only admission is supported; execution isolation requests BLOCKED until the appropriate runner enforces them.

Managed `install`, `update`, `rollback`, `remove` require an explicit owned installation root/owner; use `--help` for typed arguments. Policy/pin is supplied outside candidate/install scope. Modified/foreign/colliding files are preserved by rejection. Updates retain recovery history; rollback checks current policy and cannot reactivate a revoked version. Removal changes owned installed bytes only; external historic Evidence/backup retention requires separate decisions. Tool commands are available capabilities, not automatic authorization to install into user directories.

Enforced review reuses [trusted-reference-evidence.yml](../.github/workflows/trusted-reference-evidence.yml) skills mode with current candidate SHA, package path/source SHA and independently protected policy pin. It uses pinned main verifier and candidate data-only checkout; no candidate scan scripts run with secrets. Reference mode remains default. [Operational protection gaps](AGENT_SKILLS_PROTECTION.md) block enforcement claims until separately resolved.

## Evaluation and native/process checks

Extend [existing actual-agent protocol](REFERENCE_AGENT_EVALUATION.md), not a second scoring system. The adapter uses broker-observed actions and independent objectives in separate tune/select/final trials. Its tests exercise only the adapter. Actual model trials, authenticated usage and comprehensive outside-broker audit must be recorded separately before claiming skill efficacy.

`check_task_execution.py` evaluates declared dependencies/readiness, file/resource overlap, delegation result and exact merged-candidate checks, plus separate spec/quality conclusions. Cache/output paths share one filesystem namespace: same/ancestor overlaps conflict if either active claim is exclusive; read/read and disjoint claims are allowed. Device keys have their own namespace. Inputs and selected required checks remain independent reviewer decisions; consistency alone is not authorization, lock acquisition or a real-agent result.

`check_native_examples.py` compiles/runs original C++17 offline examples, deterministic properties/fuzz and an intentionally defective variant proving the regression catches the source defect. Dimensional misuse must fail compilation. No Adobe SDK is impersonated; real selected SDK/header and host checks remain canonical Native §23 and Process §3.

## Migration and verification

New adapter schema v1 records are new formats; preserve old project/reference formats and Evidence. Copy complete tool/import dependencies plus matched schemas/tests, not a lone script. Pin exact tooling revision; recreate observations after new package/rules/runner/config bytes and retain older raw results unchanged. Python suite and full self-test are the executable contract entry points:

```sh
python3 -m unittest discover -s starter-kit/tests -p 'test_*.py' -v
node starter-kit/scripts/self-test.mjs --dry-run --require-posix
python3 starter-kit/scripts/check_native_examples.py --sanitizers
```

Tool success establishes only the named scope. Missing tools/AE/isolation are BLOCKED/NOT_RUN, never fabricated PASS. Final exact-candidate results and remaining pilot limitations are recorded in the implementation report.
