import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import assert from 'node:assert/strict';
import {loadManifest,route,featureRules} from '../scripts/lib/applicability.mjs';
import {validate} from '../scripts/lib/schema.mjs';
import {inspectRecord} from '../scripts/lib/project-record.mjs';
import {prepareScenario,inspectScenario} from '../scripts/lib/ai-fixtures.mjs';
import {snapshot,sha256} from '../scripts/lib/files.mjs';
import {checkVersion} from '../scripts/lib/version.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const context={task:'bugfix',components:['jsx'],risk:'light',delivery:'development',reference:'none',product_contract:true,contract_covers_scope:true,changes_product_contract:false};
const withTemp=fn=>{const dir=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'ae-deep-fix-')));try{return fn(dir);}finally{fs.rmSync(dir,{recursive:true,force:true});}};
const run=(name,args,options={})=>spawnSync(process.execPath,[path.join(root,'starter-kit/scripts',name),...args],{encoding:'utf8',timeout:30000,...options});
function manifestCopy(dir){
  for(const name of ['core','profiles','starter-kit/schemas','REFERENCE_AUDIT.md','PRODUCT_DISCOVERY.md']) fs.cpSync(path.join(root,name),path.join(dir,name),{recursive:true});
  fs.copyFileSync(path.join(root,'rules-manifest.yaml'),path.join(dir,'rules-manifest.yaml'));
}

test('D01 runtime/safety minima, all numbered sections and optional feature routes',()=>{
  const m=loadManifest(root);
  for(const component of ['jsx','cep','uxp','helper']) assert.ok(route(m,{...context,components:[component]}).rules.includes('TOOL-RUNTIME'),component);
  for(const component of ['native','jsx','cep','uxp','helper']) assert.ok(route(m,{...context,components:[component],risk:'critical'}).rules.includes('CODE-SAFETY'),component);
  const seen=new Set();
  for(const g of m.rule_groups){if(g.section==='R0')continue;const [a,b=a]=g.section.split('-').map(Number);for(let n=a;n<=b;n++)if(n>0)seen.add(n);}
  assert.deepEqual([...seen].sort((a,b)=>a-b),Array.from({length:41},(_,i)=>i+1));
  for(const [feature,ids] of Object.entries(featureRules)) for(const id of ids) assert.ok(route(m,{...context,features:[feature]}).rules.includes(id),feature+'/'+id);
  assert.ok(!route(m,context).rules.includes('UPDATES'));
  for(const features of [null,['unknown'],['ui','ui'],new Array(1),Object.assign(new Array(2),{0:'ui'})]) assert.throws(()=>route(m,{...context,features}));
  for(const task of ['audit','documentation','research']) assert.equal(route(m,{...context,task,features:['updater']}).implementation_task,false);
});

test('D05 deleted/misbound task overlays and undefined route outputs fail closed',()=>withTemp(dir=>{
  manifestCopy(dir);const original=read('rules-manifest.yaml');
  for(const id of ['DEBUGGING','API-SOURCES','PRODUCT-DISCOVERY','REFERENCE-AUDIT']) {
    const missing=structuredClone(original);missing.rule_groups=missing.rule_groups.filter(g=>g.id!==id);
    fs.writeFileSync(path.join(dir,'rules-manifest.yaml'),JSON.stringify(missing));assert.throws(()=>loadManifest(dir),id);
    const wrong=structuredClone(original),g=wrong.rule_groups.find(g=>g.id===id);g.source='core/PROCESS.md';g.section='6';
    fs.writeFileSync(path.join(dir,'rules-manifest.yaml'),JSON.stringify(wrong));assert.throws(()=>loadManifest(dir),id);
  }
  const all=structuredClone(original);all.rule_groups=all.rule_groups.filter(g=>!['DEBUGGING','API-SOURCES','PRODUCT-DISCOVERY'].includes(g.id));
  fs.writeFileSync(path.join(dir,'rules-manifest.yaml'),JSON.stringify(all));assert.throws(()=>loadManifest(dir));
  fs.writeFileSync(path.join(dir,'rules-manifest.yaml'),JSON.stringify(original));assert.doesNotThrow(()=>loadManifest(dir));
  const m=loadManifest(dir);m.rule_groups=m.rule_groups.filter(g=>g.id!=='DEBUGGING');assert.throws(()=>route(m,context),/undefined/);
}));

test('D06 source symlinks, linked ancestors and linked root reject',{skip:process.platform==='win32'},()=>withTemp(dir=>{
  const checkout=path.join(dir,'checkout');fs.mkdirSync(checkout);manifestCopy(checkout);
  const source=path.join(checkout,'core/PROCESS.md'),external=path.join(dir,'external-process.md');fs.copyFileSync(source,external);fs.unlinkSync(source);
  fs.symlinkSync(external,source);assert.throws(()=>loadManifest(checkout),/symlink/);
  fs.unlinkSync(source);fs.copyFileSync(external,source);assert.doesNotThrow(()=>loadManifest(checkout));
  fs.renameSync(path.join(checkout,'core'),path.join(dir,'external-core'));fs.symlinkSync(path.join(dir,'external-core'),path.join(checkout,'core'),'dir');
  assert.throws(()=>loadManifest(checkout),/symlink/);
  fs.symlinkSync(checkout,path.join(dir,'linked-root'),'dir');assert.throws(()=>loadManifest(path.join(dir,'linked-root')),/symlink/);
}));

test('D03 project record rejects sparse/inherited arrays; dense records retain their declared result',()=>{
  const original=read('starter-kit/examples/adoption/native.json'),schema=read('starter-kit/schemas/project-record.schema.json'),registry=read('REQUIREMENTS.json');
  const inherited=new Array(1);Object.setPrototypeOf(inherited,Object.assign(Object.create(Array.prototype),{0:'native'}));
  for(const components of [new Array(1),Object.assign(new Array(2),{0:'native'}),inherited]) {
    const record=structuredClone(original);record.components=components;assert.throws(()=>inspectRecord(record,schema,root,registry),/dense/);
  }
  const verdict=inspectRecord(original,schema,path.join(root,'starter-kit/examples/adoption'),registry);
  assert.equal(verdict.recorded_policy,'BLOCKED');assert.equal(verdict.release_readiness,'NOT_ASSESSED');
});

test('D10 JSON uniqueness ignores object order, preserves array order and bounds invalid direct inputs',()=>{
  const s={type:'array',uniqueItems:true};
  for(const values of [[{a:1,b:{x:2,y:3}},{b:{y:3,x:2},a:1}],[1,1],[null,null],[[1,2],[1,2]]]) assert.throws(()=>validate(values,s),/duplicate/);
  assert.doesNotThrow(()=>validate([[1,2],[2,1]],s));assert.doesNotThrow(()=>validate([{a:1},{a:2}],s));
  const cyclic=[];cyclic.push(cyclic);assert.throws(()=>validate([cyclic],s),/limit|cyclic/);
  assert.throws(()=>validate([undefined],s),/non-JSON/);
  let deep=1;for(let n=0;n<70;n++)deep={child:deep};assert.throws(()=>validate([deep],s),/limit/);
});

test('D10 duplicate Evidence with reordered keys rejects through the actual JSON CLI',()=>withTemp(dir=>{
  const record=read('starter-kit/examples/adoption/native.json');record.delivery='validation';
  fs.writeFileSync(path.join(dir,'evidence.txt'),'controlled evidence');
  const e={path:'evidence.txt',sha256:sha256('controlled evidence')};
  const check={...record.checks[0],status:'PASS',reason:'',evidence:[e]};record.checks=[check];
  const input=path.join(dir,'record.json');
  const execute=evidence=>{check.evidence=evidence;fs.writeFileSync(input,JSON.stringify(record));return run('validate-project-record.mjs',[input]);};
  let r=execute([e]);assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).release_readiness,'NOT_ASSESSED');
  for(const evidence of [[e,{...e}],[e,{sha256:e.sha256,path:e.path}]]){r=execute(evidence);assert.equal(r.status,2,r.stderr);assert.match(r.stderr,/duplicate/);}
}));

test('D02 fixture detects unauthorized empty directories/types and preserves legacy run history',()=>withTemp(dir=>{
  const dest=path.join(dir,'run');prepareScenario('AI-EVAL-01',dest);const project=path.join(dest,'project');
  assert.equal(inspectScenario(dest).file_scope,'PASS');
  fs.mkdirSync(path.join(project,'empty'));assert.ok(inspectScenario(dest).unauthorized_files.includes('empty'));fs.rmdirSync(path.join(project,'empty'));
  const file=path.join(project,'README.md'),bytes=fs.readFileSync(file);fs.unlinkSync(file);fs.mkdirSync(file);assert.equal(inspectScenario(dest).file_scope,'FAIL');fs.rmdirSync(file);fs.writeFileSync(file,bytes);
  const p=path.join(dest,'run.json'),legacy=JSON.parse(fs.readFileSync(p));legacy.schema_version=1;fs.writeFileSync(p,JSON.stringify(legacy));assert.throws(()=>inspectScenario(dest),/legacy/);
  assert.equal(JSON.parse(fs.readFileSync(p)).schema_version,1,'historical record not upgraded');
}));

test('D02 fixture observes forbidden file/standard chmod',{skip:process.platform==='win32'},()=>withTemp(dir=>{
  const dest=path.join(dir,'run');prepareScenario('AI-EVAL-01',dest);
  const file=path.join(dest,'project/README.md'),before=fs.statSync(file).mode & 0o7777;
  fs.chmodSync(file,before ^ 0o100);assert.ok(inspectScenario(dest).unauthorized_files.includes('README.md'));fs.chmodSync(file,before);assert.equal(inspectScenario(dest).file_scope,'PASS');
  const directory=path.join(dest,'project/docs'),mode=fs.statSync(directory).mode & 0o7777;
  try {fs.chmodSync(directory,mode ^ 0o020);assert.ok(inspectScenario(dest).unauthorized_files.includes('docs'));}
  finally {fs.chmodSync(directory,mode);}
  const standard=path.join(dest,'standard/VERSION');fs.chmodSync(standard,(fs.statSync(standard).mode & 0o7777)^0o100);assert.throws(()=>inspectScenario(dest),/standard changed/);
}));

test('D07 special directory mode changes invalidate v2 artifact records; legacy records reject',{skip:process.platform==='win32'},()=>withTemp(dir=>{
  const artifact=path.join(dir,'artifact');fs.mkdirSync(artifact);fs.chmodSync(artifact,0o770);fs.writeFileSync(path.join(artifact,'payload'),'owned data');
  const manifest=snapshot(artifact);assert.equal(manifest.schema_version,2);assert.equal(manifest.mode_scope,'posix-07777');
  const record={schema_version:2,manifest,manifest_sha256:sha256(JSON.stringify(manifest))},p=path.join(dir,'record.json');fs.writeFileSync(p,JSON.stringify(record));
  assert.equal(run('verify-artifact.mjs',[artifact,p]).status,0);
  fs.chmodSync(artifact,0o1770);assert.equal(fs.statSync(artifact).mode & 0o7777,0o1770);assert.equal(run('verify-artifact.mjs',[artifact,p]).status,1);
  fs.chmodSync(artifact,0o770);record.schema_version=1;fs.writeFileSync(p,JSON.stringify(record));const r=run('verify-artifact.mjs',[artifact,p]);assert.equal(r.status,1);assert.match(r.stderr,/legacy/);
}));

test('D04 removed policy arguments cannot silently reuse the new integrity-check interface',{skip:process.platform==='win32'},()=>withTemp(dir=>{
 const script=path.join(root,'starter-kit/scripts/macos-bundle-verify.sh');
 for(const legacy of [['public','required'],['local','na'],['public','na']]){
  const out=path.join(dir,'never-created');const r=spawnSync('zsh',[script,path.join(dir,'not-real.app'),out,...legacy],{encoding:'utf8'});
  assert.equal(r.status,2,r.stderr);assert.match(r.stderr,/Legacy distribution-policy arguments/);assert.ok(!fs.existsSync(out));
 }
}));

test('D08 valid U+FFFD/Unicode/BOM accepts with original byte hashes; malformed bytes reject',()=>withTemp(dir=>{
  const source=path.join(dir,'source');fs.mkdirSync(source);const file=path.join(source,'effect.cpp');
  const inputs=[Buffer.from('int PF_Synthetic = 1; // literal � Кириллица\n'),Buffer.concat([Buffer.from([0xef,0xbb,0xbf]),Buffer.from('int PF_Synthetic = 1;\n')])];
  for(let i=0;i<inputs.length;i++){
    fs.writeFileSync(file,inputs[i]);const out=path.join(dir,'valid-'+i);const r=run('scan-adobe-api.mjs',[source,out]);assert.equal(r.status,0,r.stderr);
    const inventory=JSON.parse(fs.readFileSync(path.join(out,'inventory.json')));assert.equal(inventory.candidates[0].sha256,sha256(inputs[i]));
  }
  fs.writeFileSync(file,Buffer.from([0x2f,0x2f,0xff]));const out=path.join(dir,'invalid');const r=run('scan-adobe-api.mjs',[source,out]);assert.equal(r.status,2);assert.match(r.stderr,/non UTF-8/);assert.ok(!fs.existsSync(out));
}));

test('D09 authoritative normal version check rejects all reproduced corruption patterns',()=>{
  const readme='**Стабильная версия стандарта: v5.0.0 — 2026-10-02.**\n[old](https://example.invalid/v5.0.0)\n';
  const changelog='# Changelog\n\n## 5.0.0 — 2026-10-02\n';
  assert.equal(checkVersion('5.0.0\n',readme,changelog),'5.0.0');
  assert.throws(()=>checkVersion('5.0.0',readme.replaceAll('v5.0.0','v5.0.0-rc.1'),changelog));
  assert.throws(()=>checkVersion('5.0.0',readme.replace('v5.0.0','v5.0.1'),changelog));
  assert.throws(()=>checkVersion('05.0.0',readme.replaceAll('v5.0.0','v05.0.0'),changelog.replace('5.0.0','05.0.0')));
  for(const version of ['5.0','5.0.0-rc.1','5.00.0','5.0.00'])assert.throws(()=>checkVersion(version,readme,changelog));
  assert.throws(()=>checkVersion('5.0.0',readme+readme,changelog));assert.throws(()=>checkVersion('5.0.0',readme,changelog.replace('5.0.0','5.0.1')));
  assert.equal(checkVersion(fs.readFileSync(path.join(root,'VERSION'),'utf8'),fs.readFileSync(path.join(root,'README.md'),'utf8'),fs.readFileSync(path.join(root,'CHANGELOG.md'),'utf8')),fs.readFileSync(path.join(root,'VERSION'),'utf8').trim());
});

test('I03 AE-specific and held-out fixtures preserve boundaries and expose their pure-model defects',()=>withTemp(dir=>{
  const cases=read('starter-kit/fixtures/ai/cases.json').cases.filter(c=>Number(c.id.slice(8,10))>=21);
  assert.equal(cases.length,10);assert.equal(cases.filter(c=>c.partition==='held-out').length,5);
  for(const c of cases){
    const dest=path.join(dir,c.id);prepareScenario(c.id,dest);const project=path.join(dest,'project');
    assert.equal(c.permissions.real_host_mutation,false);assert.equal(c.permissions.publish,false);
    const runRecord=JSON.parse(fs.readFileSync(path.join(dest,'run.json')));assert.equal(runRecord.evaluation_partition,c.partition);
    assert.ok(!fs.existsSync(path.join(dest,'standard/starter-kit/fixtures/ai/cases.json')));
    assert.equal(inspectScenario(dest).agent_behavior,'NOT ASSESSED');
    for(const command of c.functional_checks){
      const [program,...args]=command.split(' ');assert.equal(program,'node');
      const before=spawnSync(process.execPath,args,{cwd:project,encoding:'utf8'});assert.notEqual(before.status,0,c.id+' should expose its defect');
    }
    for(const [name,content] of Object.entries(c.expected_files))fs.writeFileSync(path.join(project,name),content);
    for(const command of c.functional_checks){
      const [, ...args]=command.split(' ');const after=spawnSync(process.execPath,args,{cwd:project,encoding:'utf8'});assert.equal(after.status,0,c.id+' illustrative pure model: '+after.stderr);
    }
    assert.equal(inspectScenario(dest).file_scope,'PASS');assert.equal(inspectScenario(dest).agent_behavior,'NOT ASSESSED');
  }
}));
