#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), "..", "..");
const dryRun = process.argv.includes("--dry-run");
const errors = [];
const warnings = [];

function fail(message) { errors.push(message); }
function warn(message) { warnings.push(message); }
function rel(p) { return path.relative(repoRoot, p).split(path.sep).join("/"); }
function run(cmd, args, options = {}) {
  return spawnSync(cmd, args, { cwd: repoRoot, encoding: "utf8", ...options });
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
  "DEVELOPMENT_RULES.md",
  "WORKFLOW.md",
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
  "starter-kit/tests/behavioral-smoke.mjs",
  "starter-kit/templates/VALIDATION_CHECKLIST.md",
  "starter-kit/templates/RELEASE_CHECKLIST.md",
  "starter-kit/templates/UXP_ENGINEERING.md"
];

for (const p of required) {
  if (!fs.existsSync(path.join(repoRoot, p))) fail("missing required file: " + p);
}

const versionPath = path.join(repoRoot, "VERSION");
if (fs.existsSync(versionPath)) {
  const version = fs.readFileSync(versionPath, "utf8").trim();
  if (!/^\d+\.\d+\.\d+$/.test(version)) fail("VERSION is not semver: " + version);
  const readme = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");
  if (!readme.includes("v" + version)) fail("README baseline does not match VERSION " + version);
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
for (let id = 1; id <= 41; id++) {
  const owners = sectionOwners.get(id) || [];
  if (owners.length === 0) fail("missing canonical section §" + id);
  if (owners.length > 1) fail("duplicate canonical section §" + id + ": " + owners.join(", "));
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
    if (!dateMatch || !intervalMatch || !urlMatch) {
      fail(id + " is missing URL/date/refresh interval");
      continue;
    }
    const ageDays = Math.floor((Date.now() - Date.parse(dateMatch[1] + "T00:00:00Z")) / 86400000);
    const interval = Number(intervalMatch[1]);
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

// Active docs must use current terminology.
const activeDocs = files.filter((p) =>
  p.endsWith(".md") &&
  !p.endsWith(path.join("CHANGELOG.md")) &&
  !p.endsWith(path.join("SOURCES.md"))
);
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
for (const file of activeDocs) {
  const body = fs.readFileSync(file, "utf8");
  for (const term of legacyTerms) {
    if (body.includes(term)) fail(rel(file) + " contains legacy terminology: " + term);
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
  if (r.status !== 0) fail("starter-kit behavioral smoke failed: " + (r.stderr || r.stdout).trim());
}

if (!dryRun) warn("self-test does not mutate repository files; --dry-run documents release intent");

for (const message of warnings) console.warn("WARN: " + message);
if (errors.length) {
  for (const message of errors) console.error("FAIL: " + message);
  console.error("starter-kit self-test: " + errors.length + " failure(s)");
  process.exit(1);
}

console.log("starter-kit self-test: PASS (" + files.length + " files checked" + (dryRun ? ", dry-run" : "") + ")");
