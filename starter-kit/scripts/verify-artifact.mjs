import fs from 'node:fs';
import path from 'node:path';
import { snapshot, sha256 } from './lib/files.mjs';
try {
  const [input, recordPath, ...rest] = process.argv.slice(2);
  if (!input || !recordPath || rest.length) throw new Error('Usage: node verify-artifact.mjs ARTIFACT RECORD.json');
  if (fs.existsSync(path.join(path.dirname(recordPath), 'INCOMPLETE'))) throw new Error('record is incomplete');
  const record = JSON.parse(fs.readFileSync(recordPath, 'utf8'));
  const actual = snapshot(input);
  if (record.schema_version !== 1 || record.manifest_sha256 !== sha256(JSON.stringify(record.manifest)) || record.manifest_sha256 !== sha256(JSON.stringify(actual))) throw new Error('artifact/record mismatch');
  console.log('PASS: artifact entries, contents and modes match record; authenticity is not established by this comparison');
} catch (e) { console.error('FAIL: ' + e.message); process.exit(1); }
