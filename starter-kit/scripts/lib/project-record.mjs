import fs from 'node:fs';
import path from 'node:path';
import { validate } from './schema.mjs';
import { inside, sha256 } from './files.mjs';
export function inspectRecord(record, schema, root, registry) {
  validate(record, schema);
  const ids = new Set(registry.requirements.map(r => r.id));
  const checks = new Set();
  let blocked = false;
  for (const check of record.checks) {
    if (checks.has(check.id)) throw new Error('duplicate check ID');
    checks.add(check.id);
    if (!ids.has(check.requirement)) throw new Error('unknown requirement ID');
    if (check.revision !== record.candidate.commit || check.artifact_sha256 !== record.candidate.sha256) throw new Error('stale check identity');
    if (check.status === 'N/A' && !check.reason) throw new Error('N/A requires reason');
    if (check.status === 'PASS' && !check.evidence.length) throw new Error('PASS requires evidence');
    if (check.required && !['PASS','N/A'].includes(check.status)) blocked = true;
    for (const e of check.evidence) {
      if (path.isAbsolute(e.path)) throw new Error('evidence paths must be relative');
      const file = fs.realpathSync(path.resolve(root, e.path));
      if (!inside(fs.realpathSync(root), file) || !fs.statSync(file).isFile()) throw new Error('evidence escapes project/is not a file');
      if (sha256(fs.readFileSync(file)) !== e.sha256) throw new Error('evidence hash mismatch');
    }
  }
  if (!record.checks.some(c => c.required)) throw new Error('record has no required checks');
  if (record.delivery === 'release' && record.candidate.source_state !== 'CLEAN') blocked = true;
  return { recorded_policy: blocked ? 'BLOCKED' : 'PASS', release_readiness: 'NOT_ASSESSED', checks:checks.size };
}
