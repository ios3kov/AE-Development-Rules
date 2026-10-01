#!/usr/bin/env node
import { prepareScenario } from './lib/ai-fixtures.mjs';
try {
  if (process.argv.length!==4) throw new Error('usage: prepare-ai-scenario.mjs AI-EVAL-ID NEW_DIRECTORY (existing parent, outside standard repo)');
  console.log(JSON.stringify(prepareScenario(process.argv[2],process.argv[3]),null,2));
} catch (error) { console.error(error.message);process.exitCode=1; }
