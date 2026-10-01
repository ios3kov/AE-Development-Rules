#!/usr/bin/env node
import fs from "node:fs";
import { loadManifest, rulesFor } from "./lib/applicability.mjs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..", "..");
const manifestPath = path.join(root, "rules-manifest.yaml");
const rulesPath = path.join(root, "DEVELOPMENT_RULES.md");
const checkOnly = process.argv.includes("--check");

function render(manifest) {
  const groupMap = new Map(manifest.rule_groups.map(g => [g.id, g]));
  const expand = (value) => String(value).replace(/\b([A-Z][A-Z-]+)\b/g, (id) => {
    const group = groupMap.get(id);
    if (!group) return id;
    return id + " ([§" + group.section + "](" + group.source + "))";
  });

  const riskRows = manifest.artifact_profiles.map((profile) =>
    "| " + profile.label + " | " + expand(rulesFor(profile, "light").join(", ")) + " | " + expand(rulesFor(profile, "standard").join(", ")) + " | " + expand(rulesFor(profile, "critical").join(", ")) + " |"
  );
  const gateRows = manifest.artifact_profiles.map((profile) =>
    "| " + profile.label + " | " + expand(profile.validation.rules.join(", ")) + " / Validation Gate" + " | " + expand(profile.release.rules.join(", ")) + " / Release Gate; apply actual platform/format gates" + " |"
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

const manifest = loadManifest(root);
const generated = render(manifest);
const rules = fs.readFileSync(rulesPath, "utf8");
const markers = /<!-- APPLICABILITY_TABLE:START -->[\s\S]*?<!-- APPLICABILITY_TABLE:END -->/;

if (!markers.test(rules)) {
  console.error("FAIL: applicability table markers missing in DEVELOPMENT_RULES.md");
  process.exit(1);
}

if (checkOnly) {
  const current = rules.match(markers)[0].replace(/\r\n/g, "\n");
  if (current !== generated) {
    console.error("FAIL: applicability table is out of sync with rules-manifest.yaml");
    process.exit(1);
  }
  console.log("applicability manifest: PASS");
  process.exit(0);
}

fs.writeFileSync(rulesPath, rules.replace(markers, generated));
console.log("Updated applicability table from rules-manifest.yaml");
