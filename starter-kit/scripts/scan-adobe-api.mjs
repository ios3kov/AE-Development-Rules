import fs from 'node:fs';
import path from 'node:path';
import { sha256 } from './lib/files.mjs';
try {
  const [input, destination = '.artifacts/compatibility-api', ...rest] = process.argv.slice(2);
  if (!input || rest.length || !fs.statSync(input).isDirectory()) throw new Error('Usage: node scan-adobe-api.mjs SOURCE_DIR [NEW_OUTPUT_DIR]');
  if (fs.lstatSync(input).isSymbolicLink()) throw new Error('source root is a symlink');
  const source = fs.realpathSync(input), out = path.resolve(destination);
  const candidates = [], usages = [], symbols = new Set();
  function walk(dir) {
    for (const name of fs.readdirSync(dir).sort()) {
      if (['.git','node_modules','build','target'].includes(name)) continue;
      const file = path.join(dir, name), stat = fs.lstatSync(file);
      if (stat.isSymbolicLink()) throw new Error('symlink omitted from source inventory: ' + path.relative(source, file));
      if (stat.isDirectory()) walk(file);
      else if (/\.(c|cc|cpp|cxx|h|hpp|hxx|inl|ixx|r|m|mm)$/.test(name)) {
        if (!stat.isFile() || stat.size > 2 * 1024 ** 2) throw new Error('unsupported/oversized candidate');
        const text = fs.readFileSync(file, 'utf8');
        if (text.includes('\uFFFD')) throw new Error('non UTF-8 candidate');
        const relative = path.relative(source, file).split(path.sep).join('/');
        candidates.push({ path: relative, sha256: sha256(text) });
        text.split(/\r?\n/).forEach((line, i) => {
          if (/(PF_|AEGP_|SmartFX|SmartPreRender|SmartRender|kPF|kAEGP)/.test(line)) usages.push(`${relative}:${i + 1}:${line}`);
          for (const m of line.matchAll(/\b(PF_[A-Za-z0-9_]+|AEGP_[A-Za-z0-9_]+|kPF[A-Za-z0-9_]*|kAEGP[A-Za-z0-9_]*)\b/g)) symbols.add(m[0]);
        });
        if (candidates.length > 10000) throw new Error('inventory limit exceeded');
      }
    }
  }
  walk(source);
  if (!candidates.length) throw new Error('empty candidate scope');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.mkdirSync(out);
  fs.writeFileSync(path.join(out, 'adobe-api-usage.txt'), usages.join('\n') + '\n', { flag: 'wx' });
  fs.writeFileSync(path.join(out, 'adobe-api-symbols.txt'), [...symbols].sort().join('\n') + '\n', { flag: 'wx' });
  fs.writeFileSync(path.join(out, 'inventory.json'), JSON.stringify({ schema_version: 1, utc: new Date().toISOString(), collection_status: 'COMPLETE', audit_verdict: 'NOT_ASSIGNED', candidates }, null, 2) + '\n', { flag: 'wx' });
  console.log(`Collection: COMPLETE (${candidates.length} candidate files)\nEvidence: ${out}\nNOTE: lexical inventory only; map suite revisions/Min Versions separately; excluded generated/build dependencies need separate audit`);
} catch (e) { console.error('INCOMPLETE: ' + e.message); process.exit(2); }
