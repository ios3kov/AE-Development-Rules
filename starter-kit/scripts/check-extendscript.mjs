import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, join, resolve, isAbsolute } from "node:path";

const input = process.argv[2];
if (!input) {
  console.error("Usage: node check-extendscript.mjs <file.jsx>");
  process.exit(2);
}

// Documented subset: Node-parseable JavaScript with top-level ExtendScript
// directives. This is NOT an ES3/E4X/host semantic validator.
const active = new Set();
let total = 0;
async function preprocess(file, depth = 0) {
  file = resolve(file);
  if (depth > 32 || active.has(file)) throw new Error("include cycle/depth limit");
  active.add(file);
  try {
    const text = await readFile(file, "utf8");
    total += Buffer.byteLength(text);
    if (total > 8 * 1024 * 1024) throw new Error("include byte limit");
    const out = [];
    let block = false, quote = null;
    for (const line of text.split(/\r?\n/)) {
      const directive = !block && !quote && line.match(/^\s*#(\w+)\s*(.*?)\s*;?\s*$/);
      if (directive) {
        const [, name, raw] = directive;
        if (name === "include") {
          const m = raw.match(/^["']([^"']+)["']\s*;?$/);
          if (!m || isAbsolute(m[1])) throw new Error("include requires a literal relative path");
          out.push(await preprocess(resolve(dirname(file), m[1]), depth + 1));
        } else if (["target", "targetengine", "script", "strict"].includes(name)) {
          if (!raw) throw new Error("empty directive");
          out.push("");
        } else throw new Error("unsupported directive: " + name + "; resolve its semantics in the project checker");
        continue;
      }
      out.push(line);
      // Keep directives inside comments/strings as source, never execute JSX.
      for (let i = 0; i < line.length; i++) {
        const c = line[i], n = line[i + 1];
        if (block) { if (c === '*' && n === '/') { block = false; i++; } }
        else if (quote) { if (c === '\\') i++; else if (c === quote) quote = null; }
        else if (c === '/' && n === '/') break;
        else if (c === '/' && n === '*') { block = true; i++; }
        else if (c === '"' || c === "'") quote = c;
      }
      if (!line.endsWith("\\")) quote = null;
    }
    return out.join('\n');
  } finally { active.delete(file); }
}
let source;
try { source = await preprocess(input); }
catch (e) { console.error("BLOCKED: " + e.message); process.exit(2); }
const directory = await mkdtemp(join(tmpdir(), "ae-extendscript-check-"));
const temporaryFile = join(directory, basename(input).replace(/\.jsx$/i, "") + ".js");

try {
  await writeFile(temporaryFile, source);
  execFileSync(process.execPath, ["--check", temporaryFile], { stdio: "inherit", timeout: 10000 });
  console.log("PASS: JavaScript parser sanity-check");
  console.log("NOTE: directive/include preprocessing + Node syntax subset only; ES3/E4X and AE runtime compatibility require a target checker.");
} finally {
  await rm(directory, { recursive: true, force: true });
}
