#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..", "..");
const manifestPath = path.join(root, "rules-manifest.yaml");
const rulesPath = path.join(root, "DEVELOPMENT_RULES.md");
const checkOnly = process.argv.includes("--check");

function parseManifest(text) {
  const result = { rule_groups: [], artifact_profiles: [], risk_profiles: [], delivery_gates: [] };
  let section = null;
  let current = null;

  for (const raw of text.split(/\r?\n/)) {
    const line = raw.replace(/\s+$/, "");
    if (!line || line.trim().startsWith("#")) continue;
    const top = line.match(/^([a-z_]+):\s*$/);
    if (top) {
      section = top[1];
      current = null;
      continue;
    }
    const item = line.match(/^  - ([a-z_]+):\s*(.*)$/);
    if (item && result[section]) {
      current = {};
      result[section].push(current);
      current[item[1]] = strip(item[2]);
      continue;
    }
    const prop = line.match(/^    ([a-z_]+):\s*(.*)$/);
    if (prop && current) current[prop[1]] = strip(prop[2]);
  }
  return result;
}

function strip(value) {
  return value.trim().replace(/^"(.*)"$/, "$1");
}

function render(manifest) {
  const groupMap = new Map(manifest.rule_groups.map((g) => [g.id, g.section]));
  const expand = (value) => value.replace(/\b([A-Z][A-Z-]+)\b/g, (id) => groupMap.has(id) ? id + " (§" + groupMap.get(id) + ")" : id);

  const riskRows = manifest.artifact_profiles.map((p) =>
    "| " + p.label + " | " + expand(p.light) + " | " + expand(p.standard) + " | " + expand(p.critical) + " |"
  );
  const gateRows = manifest.artifact_profiles.map((p) =>
    "| " + p.label + " | " + expand(p.validation) + " | " + expand(p.release) + " |"
  );

  return [
    "<!-- APPLICABILITY_TABLE:START -->",
    "### Risk Profile × artifact",
    "",
    "| Тип проекта | Light | Standard | Critical |",
    "|---|---|---|---|",
    ...riskRows,
    "",
    "### Delivery Gate × artifact",
    "",
    "| Тип проекта | Validation | Release |",
    "|---|---|---|",
    ...gateRows,
    "<!-- APPLICABILITY_TABLE:END -->"
  ].join("\n");
}

const manifest = parseManifest(fs.readFileSync(manifestPath, "utf8"));
const generated = render(manifest);
const rules = fs.readFileSync(rulesPath, "utf8");
const re = /<!-- APPLICABILITY_TABLE:START -->[\s\S]*?<!-- APPLICABILITY_TABLE:END -->/;

if (!re.test(rules)) {
  console.error("FAIL: applicability table markers missing in DEVELOPMENT_RULES.md");
  process.exit(1);
}

if (checkOnly) {
  const current = rules.match(re)[0];
  if (current !== generated) {
    console.error("FAIL: applicability table is out of sync with rules-manifest.yaml");
    process.exit(1);
  }
  console.log("applicability manifest: PASS");
  process.exit(0);
}

fs.writeFileSync(rulesPath, rules.replace(re, generated));
console.log("Updated applicability table from rules-manifest.yaml");
