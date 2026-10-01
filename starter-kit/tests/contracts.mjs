import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {fileURLToPath} from 'node:url';import test from 'node:test';import assert from 'node:assert/strict';
import {loadManifest,route} from '../scripts/lib/applicability.mjs';
import {inspectRecord} from '../scripts/lib/project-record.mjs';
import {compare,fixtures} from '../scripts/lib/render.mjs';
import {sha256} from '../scripts/lib/files.mjs';
import {validate} from '../scripts/lib/schema.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const m=loadManifest(root),registry=read('REQUIREMENTS.json'),schema=read('starter-kit/schemas/project-record.schema.json');
test('A05 manifest rejects empty/missing profiles, fields, duplicate IDs and unknown rules',()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-manifest-'));
 try{
  for(const dir of ['core','profiles','starter-kit/schemas']) fs.cpSync(path.join(root,dir),path.join(tmp,dir),{recursive:true});
  for(const file of ['REFERENCE_AUDIT.md','PRODUCT_DISCOVERY.md']) fs.copyFileSync(path.join(root,file),path.join(tmp,file));
  const mutations=[x=>x.artifact_profiles=[],x=>x.artifact_profiles[0].light.rules=[],x=>x.artifact_profiles[0].release.rules=[],x=>x.artifact_profiles.pop(),x=>delete x.artifact_profiles[0].release,x=>x.artifact_profiles[0].id='jsx',x=>x.artifact_profiles[0].light.rules.push('INVALID'),x=>x.extra=true,x=>x.rule_groups[1].id=x.rule_groups[0].id,x=>x.risk_profiles[0].id='invalid',x=>x.artifact_profiles[1].standard.inherit='standard'];
  for(const mutate of mutations){const changed=structuredClone(m);mutate(changed);fs.writeFileSync(path.join(tmp,'rules-manifest.yaml'),JSON.stringify(changed));assert.throws(()=>loadManifest(tmp));}
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
test('A07/A09 routing scenarios keep milestone/risk/delivery and scoped reference independent',()=>{
 const common={components:['jsx'],risk:'light',delivery:'development',reference:'none',product_contract:true,contract_covers_scope:true,changes_product_contract:false};
 const cases=[
  [{task:'audit',reference:'whole-product'},false,false,false],
  [{task:'research'},false,false,false],
  [{task:'documentation',components:['native']},false,false,false],
  [{task:'bugfix'},false,false,true],
  [{task:'improvement',delivery:'release'},false,false,true],
  [{task:'improvement',components:['native'],risk:'critical'},false,false,true],
  [{task:'new-product',reference:'feature',product_contract:false,contract_covers_scope:false},true,true,true],
  [{task:'new-product',reference:'ui',product_contract:false,contract_covers_scope:false},true,true,true],
  [{task:'improvement',reference:'behavior'},false,true,true],
  [{task:'new-product',reference:'whole-product',product_contract:false,contract_covers_scope:false},true,true,true],
  [{task:'new-product',components:['uxp','helper'],risk:'standard',delivery:'validation',product_contract:false,contract_covers_scope:false},true,false,true]
 ];
 for(const [patch,discovery,reference,implementation] of cases){const context={...common,...patch};const result=route(m,context);assert.equal(result.risk,context.risk);assert.equal(result.delivery,context.delivery);assert.equal(result.product_discovery,discovery);assert.equal(result.reference_audit,reference);assert.equal(result.implementation_task,implementation);assert.equal(result.rules.includes('GATES'),context.delivery!=='development');}
 assert.throws(()=>route(m,{...common,task:'bugfix',components:['invalid']}));
 const process=fs.readFileSync(path.join(root,'core/PROCESS.md'),'utf8');assert.ok(!process.includes('Для milestone / Release Candidate дополнительно:'));assert.ok(!process.includes('распространяться публично или становиться частью production workflow'));
});
test('AI routing evaluates the confirmed current scope rather than contract existence or task label',()=>{
 const common={components:['jsx'],risk:'light',delivery:'development',reference:'none',product_contract:true,contract_covers_scope:false,changes_product_contract:true};
 for(const task of ['new-product','major-feature','improvement','bugfix']){
  const result=route(m,{...common,task});
  assert.equal(result.product_discovery,true,task+' must resolve changed scope');
  assert.ok(result.rules.includes('PRODUCT-DISCOVERY'));
  const confirmed=route(m,{...common,task,contract_covers_scope:true});
  assert.equal(confirmed.product_discovery,false,task+' must reuse an already confirmed current scope');
 }
 for(const task of ['new-product','major-feature']) assert.equal(route(m,{...common,task,changes_product_contract:false}).product_discovery,true,task+' uncovered by the old contract');
 for(const task of ['audit','documentation','research']) assert.equal(route(m,{...common,task,reference:'whole-product'}).product_discovery,false,task+' must not authorize implementation');
 assert.equal(route(m,{...common,task:'bugfix',changes_product_contract:false}).product_discovery,false,'a local bugfix does not need a discovery interview merely because documentation is incomplete');
 for(const key of ['product_contract','contract_covers_scope','changes_product_contract']){
  const missing={...common,task:'major-feature'};delete missing[key];assert.throws(()=>route(m,missing),key+' is required');
  for(const value of [null,'true',1]) assert.throws(()=>route(m,{...common,task:'major-feature',[key]:value}),key+' must be boolean');
 }
 assert.throws(()=>route(m,{...common,task:'new-product',product_contract:false,contract_covers_scope:true}),'a missing contract cannot cover the scope');
});
test('requirement registry resolves unique stable markers in canonical sources',()=>{
 const ids=new Set();for(const r of registry.requirements){assert.ok(!ids.has(r.id));ids.add(r.id);const text=fs.readFileSync(path.join(root,r.source),'utf8');assert.equal(text.split('<!-- REQ: '+r.id+' -->').length-1,1);}
});
test('project record blocks stale identity, changed/missing evidence, required failures and dirty handoff',()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-record-'));try{
  fs.writeFileSync(path.join(tmp,'evidence.txt'),'fixture evidence');
  const record={schema_version:1,standard:{version:'4.1.0',commit:'1'.repeat(40)},project:'fixture',components:['jsx'],risk:'light',delivery:'validation',candidate:{commit:'2'.repeat(40),build_id:'fixture-1',sha256:'3'.repeat(64),source_state:'CLEAN'},checks:[{id:'smoke',requirement:'EVD-001',required:true,revision:'2'.repeat(40),artifact_sha256:'3'.repeat(64),status:'PASS',reason:'',evidence:[{path:'evidence.txt',sha256:sha256('fixture evidence')}]}]};
  assert.equal(inspectRecord(record,schema,tmp,registry).recorded_policy,'PASS');
  for(const mutate of [x=>x.checks[0].revision='4'.repeat(40),x=>x.checks[0].evidence=[],x=>x.checks[0].evidence[0].sha256='5'.repeat(64),x=>x.checks[0].requirement='INVALID',x=>x.checks[0].status='N/A',x=>x.checks.push(x.checks[0])]){const changed=structuredClone(record);mutate(changed);assert.throws(()=>inspectRecord(changed,schema,tmp,registry));}
  for(const status of ['FAIL','BLOCKED','NOT RUN']){const changed=structuredClone(record);changed.checks[0].status=status;assert.equal(inspectRecord(changed,schema,tmp,registry).recorded_policy,'BLOCKED');}
  for(const delivery of ['development','validation','release']) for(const source_state of ['CLEAN','DIRTY']){
   const candidate=structuredClone(record);candidate.delivery=delivery;candidate.candidate.source_state=source_state;
   const expected=source_state==='DIRTY' && delivery!=='development' ? 'BLOCKED' : 'PASS';
   assert.equal(inspectRecord(candidate,schema,tmp,registry).recorded_policy,expected,delivery+'/'+source_state);
  }
  fs.writeFileSync(path.join(tmp,'evidence.txt'),'changed');assert.throws(()=>inspectRecord(record,schema,tmp,registry));
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
test('strict schema rejects prototype-named unknown keys and inherited required fields',()=>{
 const strict={type:'object',properties:{safe:{type:'boolean'}},required:['safe'],additionalProperties:false};
 assert.deepEqual(validate({safe:true},strict),{safe:true});
 for(const key of ['unexpected','constructor','toString','__proto__']){
  const value=JSON.parse('{"safe":true,"'+key+'":true}');
  assert.throws(()=>validate(value,strict),/unknown key/,key);
 }
 assert.throws(()=>validate(Object.create({safe:true}),strict),/missing safe/);
});
test('render comparator detects alpha/extended range errors and rejects context/tolerance mismatch',()=>{
 const reference=fixtures()['float-range'];assert.equal(compare(reference,reference,0).status,'PASS');
 const altered=structuredClone(reference);altered.pixels[3]+=0.01;assert.equal(compare(reference,altered,0.001).status,'FAIL');assert.equal(compare(reference,altered,0.02).status,'PASS');
 altered.alpha='premultiplied';assert.throws(()=>compare(reference,altered,0));assert.throws(()=>compare(reference,reference,NaN));
 const nan=structuredClone(reference);nan.pixels[0]=NaN;assert.throws(()=>compare(reference,nan,0));
 for(const [name,value] of Object.entries(fixtures())) assert.deepEqual(read('starter-kit/examples/render/'+name+'.json'),value);
});
test('filled adoption records have valid declared checks and deliberately unexecuted AE runtime',()=>{
 for(const name of ['native','jsx','cep']){
  const record=read('starter-kit/examples/adoption/'+name+'.json');
  assert.equal(inspectRecord(record,schema,path.join(root,'starter-kit/examples/adoption'),registry).recorded_policy,'BLOCKED');
  assert.ok(record.checks.some(c=>c.required && c.status==='NOT RUN'));
 }
});
