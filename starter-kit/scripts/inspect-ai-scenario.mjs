#!/usr/bin/env node
import { inspectScenario } from './lib/ai-fixtures.mjs';
try {
  if (process.argv.length!==3) throw new Error('usage: inspect-ai-scenario.mjs PREPARED_DIRECTORY');
  const result=inspectScenario(process.argv[2]);console.log(JSON.stringify(result,null,2));
  if (result.file_scope==='FAIL') process.exitCode=1;
} catch (error) { console.error(error.message);process.exitCode=1; }
