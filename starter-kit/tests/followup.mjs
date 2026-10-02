import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadManifest, route } from '../scripts/lib/applicability.mjs';
import { compare, fixtures } from '../scripts/lib/render.mjs';
import { inspectRecord } from '../scripts/lib/project-record.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const context = { task:'bugfix', components:['native'], risk:'standard', delivery:'development', reference:'none', product_contract:true, contract_covers_scope:true, changes_product_contract:false };

test('F01 bugfix selects diagnostics; API sources and Light minimum remain discoverable', () => {
  const m = loadManifest(root);
  for (const component of ['native','jsx','cep','uxp','helper']) {
    const result = route(m, {...context, components:[component], risk:'light'});
    for (const id of ['DEBUGGING','API-SOURCES','GIT','IDENTITY','REGRESSION','EVIDENCE']) assert.ok(result.rules.includes(id), component + '/' + id);
  }
  for (const task of ['audit','documentation','research']) assert.equal(route(m, {...context, task}).implementation_task, false);
  assert.ok(!route(m, {...context, task:'documentation'}).rules.includes('DEBUGGING'));
});

test('F08 reversed/unbounded/missing section ranges reject; valid ranges and R0 work', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ae-range-'));
  try {
    for (const name of ['core','profiles','starter-kit/schemas','REFERENCE_AUDIT.md','PRODUCT_DISCOVERY.md']) fs.cpSync(path.join(root,name),path.join(tmp,name),{recursive:true});
    const m = read('rules-manifest.yaml');
    const write = section => { const changed=structuredClone(m); changed.rule_groups.find(g=>g.id==='PERF').section=section; fs.writeFileSync(path.join(tmp,'rules-manifest.yaml'),JSON.stringify(changed)); };
    for (const section of ['19-17','17-1000000000','9007199254740992','17-22','00']) { write(section); assert.throws(()=>loadManifest(tmp),section); }
    write('17-19'); assert.doesNotThrow(()=>loadManifest(tmp));
    write('17'); assert.doesNotThrow(()=>loadManifest(tmp));
  } finally { fs.rmSync(tmp,{recursive:true,force:true}); }
});

test('F09 dense own pixels and finite metrics are required, including the JSON CLI', () => {
  const reference=fixtures().gradient;
  for (const side of ['actual','reference']) {
    const hole=structuredClone(reference); hole.pixels=new Array(reference.pixels.length);
    assert.throws(()=>side==='actual'?compare(reference,hole,0):compare(hole,reference,0));
    hole.pixels=reference.pixels.slice(); delete hole.pixels[1]; assert.throws(()=>compare(reference,hole,0));
  }
  const large=structuredClone(reference),zero=structuredClone(reference);large.pixels.fill(1e200);zero.pixels.fill(0);
  const result=compare(large,zero,1e201);assert.equal(result.status,'PASS');assert.equal(result.rmse,1e200);
  large.pixels.fill(Number.MAX_VALUE);zero.pixels.fill(-Number.MAX_VALUE);assert.throws(()=>compare(large,zero,Number.MAX_VALUE));
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-render-metrics-'));
  try {
    large.pixels.fill(1e200);zero.pixels.fill(0);
    fs.writeFileSync(path.join(tmp,'ref.json'),JSON.stringify(large));fs.writeFileSync(path.join(tmp,'actual.json'),JSON.stringify(zero));
    const cli=spawnSync(process.execPath,[path.join(root,'starter-kit/scripts/compare-render.mjs'),path.join(tmp,'ref.json'),path.join(tmp,'actual.json'),'1e201'],{encoding:'utf8'});
    assert.equal(cli.status,0,cli.stderr);assert.equal(JSON.parse(cli.stdout).rmse,1e200);
  } finally { fs.rmSync(tmp,{recursive:true,force:true}); }
});

test('F10 blank N/A explanations reject; a recorded rationale does not certify readiness', () => {
  const record=read('starter-kit/examples/adoption/native.json'),schema=read('starter-kit/schemas/project-record.schema.json'),registry=read('REQUIREMENTS.json');
  for (const reason of ['', ' \t\n ', '\u00a0']) {
    record.checks.forEach(c=>Object.assign(c,{status:'N/A',reason,evidence:[]}));
    assert.throws(()=>inspectRecord(record,schema,root,registry));
  }
  record.checks.forEach(c=>c.reason='Not applicable to this controlled fixture');
  assert.equal(inspectRecord(record,schema,root,registry).release_readiness,'NOT_ASSESSED');
});

test('F12 sparse/mixed/inherited/duplicate component lists reject', () => {
  const m=loadManifest(root);
  const inherited=new Array(1);Object.setPrototypeOf(inherited,Object.assign(Object.create(Array.prototype),{0:'native'}));
  for (const components of [[],new Array(1),Object.assign(new Array(2),{0:'native'}),inherited,['native','native'],[null],['unknown']]) assert.throws(()=>route(m,{...context,components}));
  assert.ok(route(m,{...context,components:['native','helper']}).rules.includes('CORE-SCOPE'));
});

test('F06 Validation separates prerequisites from user-only questions; Release and legacy records still block', () => {
  const schema=read('starter-kit/schemas/project-record.schema.json'),registry=read('REQUIREMENTS.json');
  const record=read('starter-kit/examples/adoption/native.json'); record.delivery='validation';
  const prerequisite={...record.checks[0],id:'prerequisite',phase:'pre-handoff',status:'N/A',reason:'Synthetic fixture has no executable payload',evidence:[]};
  const question={...prerequisite,id:'user-question',phase:'user-validation',status:'NOT RUN',reason:'Unique user environment is the explicit validation question'};
  record.checks=[prerequisite,question];
  assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'PASS');
  prerequisite.status='BLOCKED';assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'BLOCKED');prerequisite.status='N/A';
  question.status='FAIL';assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'BLOCKED');question.status='NOT RUN';
  record.delivery='release';assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'BLOCKED');record.delivery='validation';
  delete question.phase;assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'BLOCKED');question.phase='user-validation';
  record.candidate.source_state='DIRTY';assert.equal(inspectRecord(record,schema,root,registry).recorded_policy,'BLOCKED');record.candidate.source_state='CLEAN';
  record.checks=[question];assert.throws(()=>inspectRecord(record,schema,root,registry));
});

import { prepareScenario, inspectScenario } from '../scripts/lib/ai-fixtures.mjs';
test('F05 fixtures cover every scenario; preparation preserves resume state and inspection observes unauthorized changes', () => {
  const catalog=read('starter-kit/fixtures/ai/cases.json');
  assert.equal(new Set(catalog.cases.map(c=>c.id)).size,21);
  for (let n=1;n<=20;n++) assert.ok(catalog.cases.some(c=>c.id===`AI-EVAL-${String(n).padStart(2,'0')}`));
  for (const c of catalog.cases) {assert.ok(c.rubric.expected.length);assert.ok(c.rubric.forbidden.length);}
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-agent-fixture-'));
  try {
    const dest=path.join(tmp,'resume');prepareScenario('AI-EVAL-09',dest);
    assert.throws(()=>prepareScenario('AI-EVAL-09',dest));assert.throws(()=>prepareScenario('unknown',path.join(tmp,'unknown')));
    const project=path.join(dest,'project');
    assert.ok(!fs.existsSync(path.join(dest,'standard/starter-kit/fixtures/ai/cases.json')));
    const checkpoint=fs.readFileSync(path.join(project,'docs/STATUS.md'),'utf8').match(/HEAD: ([a-f0-9]{40})/)[1];
    assert.notEqual(checkpoint,JSON.parse(fs.readFileSync(path.join(dest,'run.json'),'utf8')).project_head);
    assert.equal(inspectScenario(dest).agent_behavior,'NOT ASSESSED');assert.equal(inspectScenario(dest).file_scope,'PASS');
    assert.match(fs.readFileSync(path.join(project,'user-notes.txt'),'utf8'),/User-owned local edit/);
    const status=spawnSync('git',['status','--porcelain'],{cwd:project,encoding:'utf8'});assert.equal(status.status,0);assert.match(status.stdout,/user-notes.txt/);
    fs.writeFileSync(path.join(project,'src/product.mjs'),catalog.cases.find(c=>c.id==='AI-EVAL-09').expected_files['src/product.mjs']);
    assert.equal(inspectScenario(dest).file_scope,'PASS');
    fs.writeFileSync(path.join(project,'user-notes.txt'),'Overwritten');assert.equal(inspectScenario(dest).file_scope,'FAIL');
    fs.writeFileSync(path.join(project,'unauthorized.txt'),'New');assert.ok(inspectScenario(dest).unauthorized_files.includes('unauthorized.txt'));
    fs.writeFileSync(path.join(project,'__proto__'),'New');assert.ok(inspectScenario(dest).unauthorized_files.includes('__proto__'));
    fs.writeFileSync(path.join(dest,'standard/VERSION'),'tampered');assert.throws(()=>inspectScenario(dest));
    if (process.platform!=='win32') {fs.symlinkSync(tmp,path.join(tmp,'existing-link'),'dir');assert.throws(()=>prepareScenario('AI-EVAL-02',path.join(tmp,'existing-link')));}
  } finally {fs.rmSync(tmp,{recursive:true,force:true});}
});

test('F05 supplied bugfix/feature outcomes satisfy unchanged acceptance tests; missing work cannot be inferred from scope PASS', () => {
  const catalog=read('starter-kit/fixtures/ai/cases.json');
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-agent-outcome-'));
  try {
    for (const id of ['AI-EVAL-02','AI-EVAL-04']) {
      const c=catalog.cases.find(c=>c.id===id),dest=path.join(tmp,id);prepareScenario(id,dest);
      const project=path.join(dest,'project'),check=id==='AI-EVAL-02'?'tests/export.mjs':'tests/choose.mjs';
      assert.notEqual(spawnSync(process.execPath,[check],{cwd:project,encoding:'utf8'}).status,0);
      assert.equal(inspectScenario(dest).file_scope,'PASS');assert.equal(inspectScenario(dest).agent_behavior,'NOT ASSESSED');
      for (const [file,content] of Object.entries(c.expected_files)) fs.writeFileSync(path.join(project,file),content);
      const result=spawnSync(process.execPath,[check],{cwd:project,encoding:'utf8'});assert.equal(result.status,0,result.stderr);
      assert.equal(inspectScenario(dest).file_scope,'PASS');
    }
  } finally {fs.rmSync(tmp,{recursive:true,force:true});}
});

test('release packaging: a nested source archive cannot borrow the parent repository identity', () => {
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-archive-source-'));
  try {
    for (const args of [['init','--initial-branch=main'],['-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','--allow-empty','-m','Parent repository']]) {
      const r=spawnSync('git',args,{cwd:tmp,encoding:'utf8'});assert.equal(r.status,0,r.stderr);
    }
    const archive=path.join(tmp,'archive');
    for (const file of ['starter-kit/scripts/prepare-ai-scenario.mjs','starter-kit/scripts/lib/ai-fixtures.mjs','starter-kit/fixtures/ai/cases.json']) {
      fs.mkdirSync(path.dirname(path.join(archive,file)),{recursive:true});fs.copyFileSync(path.join(root,file),path.join(archive,file));
    }
    const dest=path.join(tmp,'new-run');
    const r=spawnSync(process.execPath,[path.join(archive,'starter-kit/scripts/prepare-ai-scenario.mjs'),'AI-EVAL-02',dest],{encoding:'utf8'});
    assert.equal(r.status,1,r.stderr);assert.match(r.stderr,/own Git checkout/);assert.ok(!fs.existsSync(dest));
  } finally {fs.rmSync(tmp,{recursive:true,force:true});}
});
