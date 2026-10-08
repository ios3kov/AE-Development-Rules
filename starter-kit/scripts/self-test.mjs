#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { checkVersion } from './lib/version.mjs';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), "..", "..");
const dryRun = process.argv.includes("--dry-run");
const errors = [];
const warnings = [];

function fail(message) { errors.push(message); }
function warn(message) { warnings.push(message); }
function rel(p) { return path.relative(repoRoot, p).split(path.sep).join("/"); }
function run(cmd, args, options = {}) {
  return spawnSync(cmd, args, { cwd: repoRoot, encoding: "utf8", timeout: 120000, maxBuffer: 8 * 1024 * 1024, ...options });
}
function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if ([".git", "node_modules"].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const required = [
  "README.md",
  "AI_ENTRYPOINT.md",
  "docs/AI_BEHAVIOR_SCENARIOS.md",
  "docs/AI_PROTOCOL_UPDATE.md",
  "REFERENCE_AUDIT.md",
  "DEVELOPMENT_RULES.md",
  "WORKFLOW.md",
  "PRODUCT_DISCOVERY.md",
  "VERSION",
  "CHANGELOG.md",
  "LICENSE",
  "SOURCES.md",
  "rules-manifest.yaml",
  "core/PROCESS.md",
  "core/ENGINEERING.md",
  "profiles/TOOLS.md",
  "profiles/NATIVE.md",
  "profiles/RELEASE.md",
  "profiles/UXP.md",
  "profiles/JSX.md",
  "profiles/CEP.md",
  "profiles/HELPER.md",
  "starter-kit/README.md",
  "starter-kit/scripts/generate-applicability.mjs",
  "starter-kit/scripts/lib/vendor/js-tokens.mjs",
  "starter-kit/scripts/lib/vendor/js-tokens.LICENSE",
  "starter-kit/scripts/lib/vendor/README.md",
  "starter-kit/tests/behavioral-smoke.mjs",
  "starter-kit/tests/hardening.mjs",
  "starter-kit/tests/contracts.mjs",
  "starter-kit/tests/followup.mjs",
  "starter-kit/fixtures/ai/README.md",
  "starter-kit/fixtures/ai/cases.json",
  "starter-kit/scripts/prepare-ai-scenario.mjs",
  "starter-kit/scripts/inspect-ai-scenario.mjs",
  "starter-kit/templates/REQUIREMENT_TRACEABILITY.md",
  "starter-kit/schemas/rules-manifest.schema.json",
  "REQUIREMENTS.json",
  "CONTRIBUTING.md",
  "starter-kit/templates/REFERENCE_SPECIFICATION_TEMPLATE.md",
  "starter-kit/templates/PRODUCT_DISCOVERY_TEMPLATE.md",
  "starter-kit/templates/AI_TASK_STATE.md",
  "starter-kit/templates/VALIDATION_CHECKLIST.md",
  "starter-kit/templates/DEBUGGING_RECORD.md",
  "starter-kit/templates/RELEASE_CHECKLIST.md",
  "starter-kit/templates/UXP_ENGINEERING.md"
];

for (const p of required) {
  if (!fs.existsSync(path.join(repoRoot, p))) fail("missing required file: " + p);
}

const versionPath = path.join(repoRoot, "VERSION");
if (fs.existsSync(versionPath)) {
  try {
    checkVersion(fs.readFileSync(versionPath,'utf8'), fs.readFileSync(path.join(repoRoot,'README.md'),'utf8'), fs.readFileSync(path.join(repoRoot,'CHANGELOG.md'),'utf8'));
  } catch (e) { fail(e.message); }
}

const files = walk(repoRoot);

// Local Markdown links.
for (const file of files.filter((p) => p.endsWith(".md"))) {
  const body = fs.readFileSync(file, "utf8");
  const linkRe = /!?\[[^\]]*\]\(([^)]+)\)/g;
  let match;
  while ((match = linkRe.exec(body))) {
    let target = match[1].trim().replace(/^<|>$/g, "");
    if (!target || target.startsWith("#") || /^(https?:|mailto:)/i.test(target)) continue;
    target = target.split("#")[0].split("?")[0];
    try { target = decodeURIComponent(target); } catch {}
    if (!target) continue;
    const resolved = path.resolve(path.dirname(file), target);
    if (!fs.existsSync(resolved)) fail(rel(file) + " -> missing local link: " + target);
  }
}

// Canonical numbered sections must exist exactly once across modules.
const canonicalModules = files.filter((p) =>
  p.endsWith(".md") &&
  (p.startsWith(path.join(repoRoot, "core") + path.sep) || p.startsWith(path.join(repoRoot, "profiles") + path.sep))
);
const sectionOwners = new Map();
for (const file of canonicalModules) {
  const body = fs.readFileSync(file, "utf8");
  for (const match of body.matchAll(/^## (\d+)\./gm)) {
    const id = Number(match[1]);
    if (!sectionOwners.has(id)) sectionOwners.set(id, []);
    sectionOwners.get(id).push(rel(file));
  }
}
for (let id = 1; id <= 43; id++) {
  const owners = sectionOwners.get(id) || [];
  if (owners.length === 0) fail("missing canonical section §" + id);
  if (owners.length > 1) fail("duplicate canonical section §" + id + ": " + owners.join(", "));
}


// AI Smart Entry added in v3.1 must remain the user-facing routing contract.
const aiEntryPath = path.join(repoRoot, "AI_ENTRYPOINT.md");
if (fs.existsSync(aiEntryPath)) {
  const aiEntry = fs.readFileSync(aiEntryPath, "utf8");
  for (const requiredText of [
    "# AI Smart Entry",
    "Пользователь не обязан знать внутренние термины стандарта",
    "### 2.1. Приоритет решений и доверие к источникам",
    "### 2.2. Восстановление и сохранение состояния задачи",
    "### 2.3. Контракт должен покрывать текущий scope",
    "## 3. Внутренняя маршрутизация задачи",
    "### Конкретный внешний референс — conditional overlay",
    "## 4. Когда нужно задавать вопросы",
    "### 4.1. Продолжение работы и границы разрешений",
    "## 5. Как задавать вопросы пользователю",
    "## 8. Загружать только применимые правила",
    "Пользователь не должен управлять инженерным процессом вместо ИИ"
  ]) {
    if (!aiEntry.includes(requiredText)) fail("AI_ENTRYPOINT.md missing Smart Entry contract: " + requiredText);
  }
}

// Reference-driven contract added in v4 must remain conditional, evidence-based and parity-testable.
const referenceAuditPath = path.join(repoRoot, "REFERENCE_AUDIT.md");
const referenceTemplatePath = path.join(repoRoot, "starter-kit", "templates", "REFERENCE_SPECIFICATION_TEMPLATE.md");
if (fs.existsSync(referenceAuditPath)) {
  const referenceAudit = fs.readFileSync(referenceAuditPath, "utf8");
  for (const requiredText of [
    "## R0.1. Когда Reference Audit включается",
    "Reference Audit **не включается автоматически**",
    "## R0.5. Reference Claim Status",
    "## R0.6. Обязательная декомпозиция whole-product reference",
    "## R0.8. Coverage Map",
    "## R0.11. Exit criteria",
    "## R0.13. Parity Testing после реализации",
    "PROVEN",
    "OBSERVED",
    "INFERRED",
    "UNKNOWN"
  ]) {
    if (!referenceAudit.includes(requiredText)) fail("REFERENCE_AUDIT.md missing reference-driven contract: " + requiredText);
  }
}
if (fs.existsSync(referenceTemplatePath)) {
  const template = fs.readFileSync(referenceTemplatePath, "utf8");
  for (const requiredText of [
    "## 4. UI / control inventory",
    "## 7. Preset inventory",
    "## 15. Reference Coverage Map",
    "## 18. Parity acceptance tests",
    "## 20. Exit check"
  ]) {
    if (!template.includes(requiredText)) fail("REFERENCE_SPECIFICATION_TEMPLATE.md missing required section: " + requiredText);
  }
}

const adoptionTemplatePath = path.join(repoRoot, "starter-kit", "templates", "STANDARD_ADOPTION.md");
if (fs.existsSync(adoptionTemplatePath)) {
  const adoption = fs.readFileSync(adoptionTemplatePath, "utf8");
  if (!adoption.includes("Reference Audit status:")) fail("STANDARD_ADOPTION.md missing Reference Audit status");
  if (!adoption.includes("Reference Specification / reference baseline:")) fail("STANDARD_ADOPTION.md missing reference baseline");
}

// Stage 0 product discovery added in v3 must remain discoverable.
const discoveryPath = path.join(repoRoot, "PRODUCT_DISCOVERY.md");
const discoveryTemplatePath = path.join(repoRoot, "starter-kit", "templates", "PRODUCT_DISCOVERY_TEMPLATE.md");
if (fs.existsSync(discoveryPath)) {
  const discovery = fs.readFileSync(discoveryPath, "utf8");
  for (const requiredText of [
    "## 0. Product Discovery и Product Vision",
    "## 0.4. Классификация требований",
    "## 0.6. Product Vision",
    "## 0.8. User flows до архитектуры",
    "## 0.9. Success Criteria",
    "## 0.11. Exit criteria"
  ]) {
    if (!discovery.includes(requiredText)) fail("PRODUCT_DISCOVERY.md missing Stage 0 contract: " + requiredText);
  }
}
if (fs.existsSync(discoveryTemplatePath)) {
  const template = fs.readFileSync(discoveryTemplatePath, "utf8");
  for (const requiredText of ["## 2. Interview — first pass", "## 4. Requirement ledger", "## 5. Product Vision", "## 11. Stage 0 exit check"]) {
    if (!template.includes(requiredText)) fail("PRODUCT_DISCOVERY_TEMPLATE.md missing required section: " + requiredText);
  }
}

// Workflow/debugging guidance added in v2.1 must remain discoverable.
const workflowPath = path.join(repoRoot, "WORKFLOW.md");
const engineeringPath = path.join(repoRoot, "core", "ENGINEERING.md");
if (fs.existsSync(workflowPath)) {
  const workflow = fs.readFileSync(workflowPath, "utf8");
  for (const heading of ["## 9. Controlled initiative", "## 10. Представление ручных изменений"]) {
    if (!workflow.includes(heading)) fail("WORKFLOW.md missing required guidance: " + heading);
  }
}
if (fs.existsSync(engineeringPath)) {
  const engineering = fs.readFileSync(engineeringPath, "utf8");
  if (!engineering.includes("### Debugging Protocol")) fail("core/ENGINEERING.md missing Debugging Protocol");
}

// Applicability manifest must generate the exact checked-in table and point to real sections.
const generator = path.join(repoRoot, "starter-kit", "scripts", "generate-applicability.mjs");
if (fs.existsSync(generator)) {
  const r = run(process.execPath, [generator, "--check"]);
  if (r.status !== 0) fail("applicability manifest check failed: " + (r.stderr || r.stdout).trim());
}

// Source freshness registry.
const sourcesPath = path.join(repoRoot, "SOURCES.md");
if (fs.existsSync(sourcesPath)) {
  const body = fs.readFileSync(sourcesPath, "utf8");
  const heads = [...body.matchAll(/^### (SRC-[A-Z0-9-]+)/gm)];
  if (heads.length === 0) fail("SOURCES.md contains no registered sources");
  for (let i = 0; i < heads.length; i++) {
    const id = heads[i][1];
    const start = heads[i].index;
    const end = i + 1 < heads.length ? heads[i + 1].index : body.length;
    const text = body.slice(start, end);
    const dateMatch = text.match(/^- Last verified: (\d{4}-\d{2}-\d{2})$/m);
    const intervalMatch = text.match(/^- Refresh interval days: (\d+)$/m);
    const urlMatch = text.match(/^- URL: https:\/\//m);
    const claimMatch = text.match(/^- Claim: .+/m);
    if (!dateMatch || !intervalMatch || !urlMatch || !claimMatch) {
      fail(id + " is missing URL/date/refresh interval");
      continue;
    }
    const ageDays = Math.floor((Date.now() - Date.parse(dateMatch[1] + "T00:00:00Z")) / 86400000);
    const interval = Number(intervalMatch[1]);
    if (!Number.isFinite(ageDays) || interval <= 0 || new Date(dateMatch[1]).toISOString().slice(0,10) !== dateMatch[1]) { fail(id + " invalid date/interval"); continue; }
    if (ageDays < -1) fail(id + " Last verified date is in the future");
    if (ageDays > interval) fail(id + " source is stale: " + ageDays + " days > " + interval);
  }
}

// Shell syntax + executable mode.
const shellScripts = files.filter((p) => p.endsWith(".sh"));
if (process.platform !== "win32") {
  const zshProbe = run("zsh", ["--version"]);
  const shell = !zshProbe.error && zshProbe.status === 0 ? "zsh" : "bash";
  if (process.platform === "darwin" && shell !== "zsh") fail("zsh unavailable on macOS runner");
  for (const file of shellScripts) {
    const mode = fs.statSync(file).mode;
    if ((mode & 0o111) === 0) fail(rel(file) + " is not executable");
    const r = run(shell, ["-n", file]);
    if (r.status !== 0) fail(rel(file) + ": " + shell + " -n failed: " + (r.stderr || r.stdout).trim());
  }
}

// Node syntax.
for (const file of files.filter((p) => p.endsWith(".mjs"))) {
  const r = run(process.execPath, ["--check", file]);
  if (r.status !== 0) fail(rel(file) + ": node --check failed: " + (r.stderr || r.stdout).trim());
}

// PowerShell syntax when available.
const psFiles = files.filter((p) => p.endsWith(".ps1"));
let ps = null;
for (const candidate of ["pwsh", "powershell"]) {
  const probe = run(candidate, ["-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"]);
  if (!probe.error && probe.status === 0) { ps = candidate; break; }
}
if (ps) {
  for (const file of psFiles) {
    const escaped = file.replace(/'/g, "''");
    const code = "$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('" + escaped + "', [ref]$tokens, [ref]$errors) > $null; if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }";
    const r = run(ps, ["-NoLogo", "-NoProfile", "-Command", code]);
    if (r.status !== 0) fail(rel(file) + ": PowerShell parse failed: " + (r.stderr || r.stdout).trim());
  }
} else if (psFiles.length) {
  warn("PowerShell parser unavailable; .ps1 syntax check skipped");
}

// Fail closed on obviously destructive starter-kit shell patterns.
const scriptFiles = files.filter((p) =>
  p.startsWith(path.join(repoRoot, "starter-kit", "scripts")) && p !== __filename
);
const destructive = [
  { re: /\brm\s+-[^\n]*rf[^\n]*\s+\/(?:\s|$)/i, name: "rm -rf /" },
  { re: /\bgit\s+reset\s+--hard\b/i, name: "git reset --hard" },
  { re: /\bgit\s+clean\s+-[^\n]*f/i, name: "git clean -f" },
  { re: /\bmkfs(?:\.|\s)/i, name: "mkfs" },
  { re: /\bdiskutil\s+erase/i, name: "diskutil erase" },
  { re: /\bformat(?:\.com)?\s+[a-z]:/i, name: "format drive" }
];
for (const file of scriptFiles) {
  const body = fs.readFileSync(file, "utf8");
  for (const rule of destructive) {
    if (rule.re.test(body)) fail(rel(file) + " contains forbidden destructive pattern: " + rule.name);
  }
}

// Active docs, scripts and manifests must use current terminology.
// self-test itself is excluded because it intentionally contains the forbidden vocabulary below.
const terminologyFiles = files.filter((p) => {
  if (p === __filename) return false;
  if (p.endsWith(path.join("CHANGELOG.md")) || p.endsWith(path.join("SOURCES.md"))) return false;
  return /\.(md|mjs|sh|ps1|ya?ml)$/i.test(p);
});
const legacyTerms = [
  "API-COMPATIBLE",
  "RISK / UNKNOWN",
  "PROVEN / VERIFIED",
  "OBSERVED / RESEARCH",
  "UNKNOWN / NOT VERIFIED",
  "supported / verified",
  "Release / Critical",
  "Release-Critical"
];
for (const file of terminologyFiles) {
  const body = fs.readFileSync(file, "utf8");
  for (const term of legacyTerms) {
    if (body.includes(term)) fail(rel(file) + " contains legacy terminology: " + term);
  }
}

// Binary audit helpers are evidence collectors; successful execution must not masquerade as compatibility PASS.
for (const relativePath of [
  "starter-kit/scripts/macos-binary-audit.sh",
  "starter-kit/scripts/windows-binary-audit.ps1"
]) {
  const auditPath = path.join(repoRoot, relativePath);
  if (!fs.existsSync(auditPath)) continue;
  const body = fs.readFileSync(auditPath, "utf8");
  if (!body.includes("audit_verdict=NOT_ASSIGNED")) {
    fail(relativePath + " must declare audit_verdict=NOT_ASSIGNED");
  }
  if (!body.includes("exit code 0 means evidence collection completed")) {
    fail(relativePath + " must explain evidence-collection exit semantics");
  }
}

// CI should avoid redundant branch matrices while preserving full PR/main coverage.
const ciWorkflowPath = path.join(repoRoot, ".github", "workflows", "starter-kit-self-test.yml");
if (fs.existsSync(ciWorkflowPath)) {
  const workflow = fs.readFileSync(ciWorkflowPath, "utf8");
  for (const requiredText of [
    "branches: [main]",
    "pull_request:",
    "workflow_dispatch:",
    "concurrency:",
    "cancel-in-progress: true"
  ]) {
    if (!workflow.includes(requiredText)) fail("starter-kit self-test workflow missing CI optimization: " + requiredText);
  }
}

// GitHub Actions dependencies must be immutable.
for (const file of files.filter((p) => /\.ya?ml$/i.test(p))) {
  const body = fs.readFileSync(file, "utf8");
  for (const match of body.matchAll(/uses:\s*([^@\s]+)@([^\s#]+)/g)) {
    const action = match[1];
    const ref = match[2];
    if (action.startsWith("./")) continue;
    if (!/^[0-9a-f]{40}$/i.test(ref)) fail(rel(file) + " action is not pinned to full SHA: " + action + "@" + ref);
  }
}

// Behavioural tests exercise the starter-kit scripts against isolated temp fixtures.
const behavioral = path.join(repoRoot, "starter-kit", "tests", "behavioral-smoke.mjs");
if (fs.existsSync(behavioral)) {
  const r = run(process.execPath, [behavioral]);
  process.stdout.write(r.stdout || "");
  if (r.status !== 0) fail("starter-kit behavioral smoke failed: " + (r.stderr || r.stdout).trim());
}

// Conditional reference adapters are verified as standard tooling, with synthetic data only.
const python = ["python3", "python"].find(command => run(command, ["-c", "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"]).status === 0);
if (!python) fail("Python 3.11+ required for standard adapter contract tests");
else {
  const r = run(python, ["-m", "unittest", "discover", "-s", "starter-kit/tests", "-p", "test_*.py", "-v"]);
  process.stdout.write(r.stdout || "");
  process.stdout.write(r.stderr || "");
  if (r.status !== 0) fail("standard adapter contract tests failed");
}

// Required subset is explicit for each runner. Structural checks are not semantic proof.
const requirePosix = process.argv.includes("--require-posix");
const requirePowerShell = process.argv.includes("--require-powershell");
if (requirePosix && (process.platform === "win32" || run("zsh", ["--version"]).status !== 0)) fail("required POSIX runtime unavailable");
if (requirePowerShell && !ps) fail("required PowerShell runtime unavailable");
console.log("coverage: Node=RUN; POSIX=" + (process.platform !== "win32" && run("zsh", ["--version"]).status === 0 ? "RUN" : "NOT RUN") + "; PowerShell=" + (ps ? "RUN" : "NOT RUN"));
for (const suite of ["hardening.mjs", "contracts.mjs", "followup.mjs", "deep-audit.mjs"]) {
  const r = run(process.execPath, [path.join(repoRoot, "starter-kit/tests", suite)]);
  process.stdout.write(r.stdout || "");
  if (r.status !== 0) fail(suite + ": " + (r.stderr || r.stdout).trim());
}

if (!dryRun) warn("self-test does not mutate repository files; --dry-run documents release intent");

for (const message of warnings) console.warn("WARN: " + message);
if (errors.length) {
  for (const message of errors) console.error("FAIL: " + message);
  console.error("starter-kit self-test: " + errors.length + " failure(s)");
  process.exit(1);
}

console.log("starter-kit self-test: PASS (" + files.length + " files checked" + (dryRun ? ", dry-run" : "") + ")");
