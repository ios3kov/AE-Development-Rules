import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { inspectRecord } from './lib/project-record.mjs';
try {
  const [recordPath, ...rest] = process.argv.slice(2);
  if (!recordPath || rest.length) throw new Error('Usage: node validate-project-record.mjs RECORD.json (relative Evidence uses record directory)');
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
  const verdict = inspectRecord(read(recordPath), read(path.join(root,'starter-kit/schemas/project-record.schema.json')), path.dirname(path.resolve(recordPath)), read(path.join(root,'REQUIREMENTS.json')));
  console.log(JSON.stringify(verdict, null, 2));
  if (verdict.recorded_policy !== 'PASS') process.exitCode = 1;
} catch (e) { console.error('INCOMPLETE: ' + e.message); process.exit(2); }
