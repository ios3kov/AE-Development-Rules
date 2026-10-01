import fs from 'node:fs';
import { compare } from './lib/render.mjs';
try {
  const [reference,actual,tolerance,output,...rest] = process.argv.slice(2);
  if (!reference || !actual || tolerance === undefined || tolerance.trim() === '' || rest.length) throw new Error('Usage: node compare-render.mjs REFERENCE.json ACTUAL.json MAX_ABS_ERROR [NEW_DIFF.json]');
  const result = compare(JSON.parse(fs.readFileSync(reference,'utf8')),JSON.parse(fs.readFileSync(actual,'utf8')),Number(tolerance));
  if (output) fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  const {differences,...summary} = result;
  console.log(JSON.stringify(summary,null,2));
  if (result.status === 'FAIL') process.exitCode=1;
} catch (e) { console.error('INCOMPLETE: '+e.message); process.exit(2); }
