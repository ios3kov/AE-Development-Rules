// Deliberately narrow docs-only scope; no build, host or Markdown correctness claim.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

function git(cwd, ...args) {
  const r = spawnSync('git', args, {cwd, encoding: 'utf8', timeout: 15000, maxBuffer: 8 * 1024 * 1024});
  if (r.error || r.status !== 0) throw new Error('Git scope unavailable: ' + (r.error?.message || r.stderr.trim()));
  return r.stdout;
}
const names = text => text.split('\0').filter(Boolean);
export function checkDocsScope(cwd, baseRef = process.env.AE_PREFLIGHT_BASE_REF) {
  // Git for Windows uses forward slashes; compare canonical native paths.
  const root = fs.realpathSync(git(cwd, 'rev-parse', '--show-toplevel').trim());
  const changed = new Set([
    ...names(git(root, 'diff', '--name-only', '--no-renames', '-z')),
    ...names(git(root, 'diff', '--cached', '--name-only', '--no-renames', '-z')),
    ...names(git(root, 'ls-files', '--others', '--exclude-standard', '-z'))
  ]);
  const refs = ['HEAD'];
  if (baseRef) {
    // Resolve first; pass only an object identity, never an option from input.
    const base = git(root, 'rev-parse', '--verify', '--end-of-options', baseRef + '^{commit}').trim();
    names(git(root, 'diff', '--name-only', '--no-renames', '-z', base + '...HEAD')).forEach(p => changed.add(p));
    refs.push(base);
  }
  const special = new Set();
  for (const ref of refs) {
    for (const entry of names(git(root, 'ls-tree', '-r', '-z', ref))) {
      const tab = entry.indexOf('\t');
      if (!entry.startsWith('100644 blob ')) special.add(entry.slice(tab + 1));
    }
  }
  for (const entry of names(git(root, 'ls-files', '--stage', '-z'))) {
    const tab = entry.indexOf('\t');
    if (!entry.startsWith('100644 ')) special.add(entry.slice(tab + 1));
  }
  const rejected = [];
  for (const name of changed) {
    const documentation = /\.(md|rst)$/i.test(name) || /(^|\/)(LICENSE|COPYING|NOTICE)(\.txt)?$/.test(name);
    if (!documentation || special.has(name)) { rejected.push(name); continue; }
    const absolute = path.resolve(root, name);
    const relative = path.relative(root, absolute);
    if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative)) { rejected.push(name); continue; }
    try {
      const stat = fs.lstatSync(absolute);
      if (!stat.isFile() || (process.platform !== 'win32' && (stat.mode & 0o111))) rejected.push(name);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error; // A deleted ordinary document is allowed.
    }
  }
  if (rejected.length) throw new Error('docs-only includes non-documentation, executable or special paths: ' + rejected.join(', '));
  return [...changed].sort();
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { console.log('[preflight] documentation paths checked: ' + checkDocsScope(process.cwd()).length); }
  catch (error) { console.error('[preflight] BLOCKED: ' + error.message); process.exitCode = 2; }
}
