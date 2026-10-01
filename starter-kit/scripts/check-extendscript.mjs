import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";

const input = process.argv[2];
if (!input) {
  console.error("Usage: node check-extendscript.mjs <file.jsx>");
  process.exit(2);
}

const source = await readFile(input, "utf8");
const directory = await mkdtemp(join(tmpdir(), "ae-extendscript-check-"));
const temporaryFile = join(directory, basename(input).replace(/\.jsx$/i, "") + ".js");

try {
  await writeFile(temporaryFile, source);
  execFileSync(process.execPath, ["--check", temporaryFile], { stdio: "inherit" });
  console.log("PASS: JavaScript parser sanity-check");
  console.log("NOTE: this does not prove ExtendScript runtime compatibility inside After Effects.");
} finally {
  await rm(directory, { recursive: true, force: true });
}
