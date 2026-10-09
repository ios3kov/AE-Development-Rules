#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..", "..");
const scripts = path.join(root, "starter-kit", "scripts");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ae-rules-smoke-"));
const errors = [];

function run(cmd, args, opts = {}) {
  return spawnSync(cmd, args, { encoding: "utf8", timeout: 30000, ...opts });
}
function expect(condition, message) {
  if (!condition) errors.push(message);
}
function setupGit(dir) {
  fs.mkdirSync(dir, { recursive: true });
  run("git", ["init", "-q"], { cwd: dir });
  run("git", ["config", "user.email", "ci@example.invalid"], { cwd: dir });
  run("git", ["config", "user.name", "AE Rules CI"], { cwd: dir });
  fs.writeFileSync(path.join(dir, "README.md"), "fixture\n");
  run("git", ["add", "."], { cwd: dir });
  run("git", ["commit", "-qm", "fixture"], { cwd: dir });
}

try {
  const jsxGood = path.join(tmp, "good.jsx");
  const jsxBad = path.join(tmp, "bad.jsx");
  fs.writeFileSync(jsxGood, "var x = 1;\n");
  fs.writeFileSync(jsxBad, "var = ;\n");
  let r = run(process.execPath, [path.join(scripts, "check-extendscript.mjs"), jsxGood]);
  expect(r.status === 0, "check-extendscript should accept valid JSX");
  r = run(process.execPath, [path.join(scripts, "check-extendscript.mjs"), jsxBad]);
  expect(r.status !== 0, "check-extendscript should reject invalid JSX");

  const repo = path.join(tmp, "repo");
  setupGit(repo);

  if (process.platform !== "win32") {
    const zsh = run("zsh", ["--version"]);
    if (!zsh.error && zsh.status === 0) {
      const src = path.join(repo, "src");
      const apiOut = path.join(tmp, "api-out");
      fs.mkdirSync(src);
      fs.writeFileSync(path.join(src, "effect.cpp"), "void f(){ int x = PF_Cmd_RENDER; }\n");
      r = run("zsh", [path.join(scripts, "scan-adobe-api.sh"), src, apiOut], { cwd: repo });
      expect(r.status === 0, "scan-adobe-api should run on fixture source");
      expect(fs.readFileSync(path.join(apiOut, "adobe-api-symbols.txt"), "utf8").includes("PF_Cmd_RENDER"), "scan-adobe-api should capture PF_Cmd_RENDER");

      const artifact = path.join(repo, "artifact.txt");
      const evidence = path.join(tmp, "artifact-evidence");
      fs.writeFileSync(artifact, "artifact\n");
      r = run("zsh", [path.join(scripts, "record-artifact.sh"), artifact, evidence], { cwd: repo });
      expect(r.status === 0, "record-artifact should produce evidence");
      expect(fs.existsSync(path.join(evidence, "SHA256.txt")), "record-artifact should write SHA256 evidence");

      const ownedRoot = path.join(fs.realpathSync(tmp), "owned-workspaces");
      r = run("zsh", [path.join(scripts, "create-owned-test-workspace.sh")], { cwd: repo, env: { ...process.env, AE_TEST_WORKSPACE_ROOT: ownedRoot } });
      expect(r.status === 0, "create-owned-test-workspace should create owned workspace");
      const workspace = (r.stdout || "").trim().split(/\r?\n/)[0];
      expect(workspace.startsWith(ownedRoot + path.sep), "owned workspace must stay inside configured root");
      expect(fs.existsSync(path.join(workspace, "OWNERSHIP.txt")), "owned workspace should contain ownership proof");

      const realRoot = path.join(tmp, "real-owned-root");
      const symlinkRoot = path.join(tmp, "symlink-owned-root");
      fs.mkdirSync(realRoot);
      fs.symlinkSync(realRoot, symlinkRoot, "dir");
      r = run("zsh", [path.join(scripts, "create-owned-test-workspace.sh")], { cwd: repo, env: { ...process.env, AE_TEST_WORKSPACE_ROOT: symlinkRoot } });
      expect(r.status !== 0, "create-owned-test-workspace should refuse symlink root");

      r = run("zsh", [path.join(scripts, "preflight.sh")], { cwd: repo });
      expect(r.status === 2, "preflight.sh must block when no project checks are configured");

      for (const script of ["macos-binary-audit.sh", "macos-bundle-verify.sh", "verify-native-effect-bundle-macos.sh"]) {
        r = run("zsh", [path.join(scripts, script)], { cwd: repo });
        expect(r.status !== 0, script + " should fail closed when required target is missing");
      }
    }
  }

  const pwshCandidates = ["pwsh", "powershell"];
  let pwsh = null;
  for (const candidate of pwshCandidates) {
    const probe = run(candidate, ["-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"]);
    if (!probe.error && probe.status === 0) { pwsh = candidate; break; }
  }
  if (pwsh) {
    r = run(pwsh, ["-NoLogo", "-NoProfile", "-File", path.join(scripts, "preflight.ps1")], { cwd: repo });
    expect(r.status === 2, "preflight.ps1 must block when no project checks are configured");

    fs.writeFileSync(path.join(repo, "package.json"), "{\"name\":\"fixture\",\"version\":\"1.0.0\"}\n");
    const depOut = path.join(tmp, "dep-evidence");
    r = run(pwsh, ["-NoLogo", "-NoProfile", "-File", path.join(scripts, "collect-dependency-evidence.ps1"), "-OutputDir", depOut], { cwd: repo });
    expect(r.status === 0, "collect-dependency-evidence.ps1 should run on fixture repository");
    const reports = fs.readdirSync(depOut).filter((n) => n.endsWith(".txt"));
    expect(reports.length > 0, "collect-dependency-evidence.ps1 should write a report");

    for (const script of ["windows-binary-audit.ps1", "windows-release-verify.ps1"]) {
      const missingOutput = path.join(tmp, script + "-missing-evidence");
      const args = ["-NoLogo", "-NoProfile", "-File", path.join(scripts, script), "-Target", path.join(tmp, "missing.exe"),
        script === "windows-release-verify.ps1" ? "-EvidenceDirectory" : "-Output", missingOutput];
      r = run(pwsh, args, { cwd: repo });
      expect(r.status !== 0, script + " should fail closed for missing target");
      expect(!fs.existsSync(missingOutput), script + " should not create evidence for missing target");
    }
  }
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}

if (errors.length) {
  for (const e of errors) console.error("FAIL: " + e);
  process.exit(1);
}
console.log("starter-kit behavioral smoke: PASS");
