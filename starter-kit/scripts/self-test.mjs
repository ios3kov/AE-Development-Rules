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

function run(cmd, args) {
  return spawnSync(cmd, args, { cwd: repoRoot, encoding: "utf8" });
}

const required = [
  "README.md",
  "DEVELOPMENT_RULES.md",
  "WORKFLOW.md",
  "VERSION",
  "CHANGELOG.md",
  "starter-kit/README.md",
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

const shellScripts = files.filter((p) => p.endsWith(".sh"));
if (process.platform !== "win32") {
  for (const file of shellScripts) {
    const mode = fs.statSync(file).mode;
    if ((mode & 0o111) === 0) fail(rel(file) + " is not executable");
    const r = run("bash", ["-n", file]);
    if (r.status !== 0) fail(rel(file) + ": bash -n failed: " + (r.stderr || r.stdout).trim());
  }
}

for (const file of files.filter((p) => p.endsWith(".mjs"))) {
  const r = run(process.execPath, ["--check", file]);
  if (r.status !== 0) fail(rel(file) + ": node --check failed: " + (r.stderr || r.stdout).trim());
}

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

const scriptFiles = files.filter((p) => p.startsWith(path.join(repoRoot, "starter-kit", "scripts")));
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

const taxonomyFiles = files.filter((p) =>
  p.endsWith(".md") &&
  (p === path.join(repoRoot, "DEVELOPMENT_RULES.md") || p.includes(path.join("starter-kit", "templates")))
);
const legacyTerms = [
  "API-COMPATIBLE",
  "RISK / UNKNOWN",
  "PROVEN / VERIFIED",
  "OBSERVED / RESEARCH",
  "UNKNOWN / NOT VERIFIED",
  "supported / verified"
];
for (const file of taxonomyFiles) {
  const body = fs.readFileSync(file, "utf8");
  for (const term of legacyTerms) {
    if (body.includes(term)) fail(rel(file) + " contains legacy status term: " + term);
  }
}

if (!dryRun) {
  warn("self-test is read-only; --dry-run is recommended in CI to make that intent explicit");
}

for (const message of warnings) console.warn("WARN: " + message);
if (errors.length) {
  for (const message of errors) console.error("FAIL: " + message);
  console.error("starter-kit self-test: " + errors.length + " failure(s)");
  process.exit(1);
}

console.log("starter-kit self-test: PASS (" + files.length + " files checked" + (dryRun ? ", dry-run" : "") + ")");
