import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { safePath } from './lib/files.mjs';
try {
  const git = (...args) => execFileSync('git', args, { encoding: 'utf8', timeout: 10000 }).trim();
  const repo = fs.realpathSync(git('rev-parse', '--show-toplevel'));
  const requested = path.resolve(process.env.AE_TEST_WORKSPACE_ROOT || path.join(repo, '.ae-test-workspace'));
  // /tmp and /var may be system aliases on macOS. Normalize only those known
  // aliases, then reject symlinks in all remaining configured components.
  const normalizeSystemAlias = p => process.platform === 'darwin' ? p.replace(/^\/tmp(?=\/|$)/, '/private/tmp').replace(/^\/var(?=\/|$)/, '/private/var') : p;
  const base = safePath(path.parse(requested).root, normalizeSystemAlias(requested));
  fs.mkdirSync(base, { recursive: true });
  const id = 'AE-TEST-' + crypto.randomUUID();
  const work = path.join(base, id);
  fs.mkdirSync(work);
  fs.writeFileSync(path.join(work, 'OWNERSHIP.txt'), `run_id=${id}\ncanonical_workspace=${fs.realpathSync(work)}\nrepo=${repo}\ncommit=${git('rev-parse', 'HEAD')}\npid=${process.pid}\nutc=${new Date().toISOString()}\n`, { flag: 'wx' });
  console.log(fs.realpathSync(work));
  console.error('NOTE: revalidate ownership before cleanup; this script does not delete or control AE');
} catch (e) { console.error('BLOCKED: ' + e.message); process.exit(4); }
