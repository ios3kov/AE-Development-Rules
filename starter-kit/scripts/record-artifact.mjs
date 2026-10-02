import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { inside, snapshot, sha256 } from './lib/files.mjs';

try {
  const [input, destination, ...rest] = process.argv.slice(2);
  if (!input || rest.length) throw new Error('Usage: node record-artifact.mjs ARTIFACT [NEW_EVIDENCE_DIR]');
  const git = (...args) => execFileSync('git', args, { encoding: 'utf8', timeout: 10000 }).trim();
  const root = fs.realpathSync(git('rev-parse', '--show-toplevel'));
  const artifact = fs.realpathSync(input);
  const before = snapshot(input);
  const id = 'AE-ARTIFACT-' + new Date().toISOString().replace(/[:.]/g, '-') + '-' + crypto.randomUUID();
  const output = path.resolve(destination || path.join(root, '.artifacts/evidence', id));
  // Resolve existing ancestors, including a symlinked output parent, before testing overlap.
  let parent = path.dirname(output), suffix = [];
  while (!fs.existsSync(parent)) { suffix.unshift(path.basename(parent)); parent = path.dirname(parent); }
  const canonicalOutput = path.join(fs.realpathSync(parent), ...suffix, path.basename(output));
  if (inside(artifact, canonicalOutput) || inside(canonicalOutput, artifact)) throw new Error('Evidence and artifact paths overlap');
  if (fs.existsSync(output) || (() => { try { fs.lstatSync(output); return true; } catch (e) { if (e.code !== 'ENOENT') throw e; return false; } })()) throw new Error('Evidence destination already exists');
  const commit = git('-C', root, 'rev-parse', 'HEAD');
  const state = git('-C', root, 'status', '--porcelain');
  const record = { schema_version: 2, run_id: id, utc: new Date().toISOString(), source_commit: commit, source_state: state ? 'DIRTY' : 'CLEAN', artifact, platform: process.platform, node: process.version, manifest_sha256: sha256(JSON.stringify(before)), manifest: before };
  // Reserve outside the payload and keep INCOMPLETE until all record files are written.
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.mkdirSync(output); // Exclusive reservation; never reuse history.
  try {
    fs.writeFileSync(path.join(output, 'INCOMPLETE'), 'recording\n', { flag: 'wx' });
    if (JSON.stringify(before) !== JSON.stringify(snapshot(input))) throw new Error('artifact changed during recording');
    for (const [name, data] of Object.entries({
      'artifact-record.json': JSON.stringify(record, null, 2) + '\n',
      'source-commit.txt': commit + '\n', 'source-state.txt': state + '\n',
      'source-cleanliness.txt': record.source_state + '\n', 'test-run-id.txt': id + '\n',
      'artifact-path.txt': artifact + '\n',
      'SHA256-files.txt': before.entries.filter(e => e.type === 'file').map(e => `${e.sha256}  ${e.path}`).join('\n') + '\n',
      'SHA256.txt': record.manifest_sha256 + '  canonical-manifest\n'
    })) fs.writeFileSync(path.join(output, name), data, { flag: 'wx' });
    fs.unlinkSync(path.join(output, 'INCOMPLETE'));
  } catch (e) { throw new Error('Incomplete record retained; do not use it: ' + e.message); }
  console.log(`Test Run ID: ${id}\nCommit: ${commit}\nEvidence: ${output}`);
} catch (e) { console.error('ERROR: ' + e.message); process.exit(2); }
