import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import test from 'node:test';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const scripts=path.join(root,'starter-kit/scripts');
const tmp=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'ae-hardening-')));
const repo=path.join(tmp,'repo');fs.mkdirSync(repo);
const run=(cmd,args,options={})=>spawnSync(cmd,args,{cwd:repo,encoding:'utf8',timeout:30000,...options});
const node=(name,args=[],options={})=>run(process.execPath,[path.join(scripts,name),...args],options);
for(const args of [['init','-q'],['config','user.email','test@example.invalid'],['config','user.name','Test']]) assert.equal(run('git',args).status,0);
fs.writeFileSync(path.join(repo,'README.md'),'fixture\n');
assert.equal(run('git',['add','.']).status,0);assert.equal(run('git',['commit','-qm','fixture']).status,0);
process.on('exit',()=>fs.rmSync(tmp,{recursive:true,force:true}));

test('A02/A03 artifact detects modes/content and refuses overwrite/overlap',()=>{
 const artifact=path.join(tmp,'artifact');fs.mkdirSync(artifact);const payload=path.join(artifact,'payload');fs.writeFileSync(payload,'one');
 const out=path.join(tmp,'evidence');let r=node('record-artifact.mjs',[artifact,out]);assert.equal(r.status,0,r.stderr);
 const record=path.join(out,'artifact-record.json');assert.equal(node('verify-artifact.mjs',[artifact,record]).status,0);
 assert.notEqual(node('record-artifact.mjs',[artifact,out]).status,0);
 assert.notEqual(node('record-artifact.mjs',[artifact,path.join(artifact,'evidence')]).status,0);
 if(process.platform!=='win32'){fs.chmodSync(payload,0o755);assert.notEqual(node('verify-artifact.mjs',[artifact,record]).status,0);fs.chmodSync(payload,0o644);}
 fs.writeFileSync(payload,'two');assert.notEqual(node('verify-artifact.mjs',[artifact,record]).status,0);
 const internal=path.join(tmp,'internal');fs.mkdirSync(internal);fs.writeFileSync(path.join(internal,'file'),'x');
 if(process.platform!=='win32'){
  fs.symlinkSync('file',path.join(internal,'link'));assert.equal(node('record-artifact.mjs',[internal,path.join(tmp,'internal-record')]).status,0);
  fs.unlinkSync(path.join(internal,'link'));fs.symlinkSync(payload,path.join(internal,'link'));assert.notEqual(node('record-artifact.mjs',[internal,path.join(tmp,'external-record')]).status,0);
 }
});
test('A06 JSX directives, include cycles and missing/invalid includes',()=>{
 const inc=path.join(tmp,'part.jsxinc'),source=path.join(tmp,'main.jsx');fs.writeFileSync(inc,'var value=1;\n');
 fs.writeFileSync(source,'#target aftereffects\n#include "part.jsxinc"\nvalue++;\n');assert.equal(node('check-extendscript.mjs',[source]).status,0);
 fs.writeFileSync(inc,'var = ;');assert.notEqual(node('check-extendscript.mjs',[source]).status,0);
 fs.writeFileSync(inc,'#include "main.jsx"');assert.notEqual(node('check-extendscript.mjs',[source]).status,0);
 fs.unlinkSync(inc);assert.notEqual(node('check-extendscript.mjs',[source]).status,0);
});
test('A10 API scan rejects invalid scope and records complete candidate inventory',()=>{
 const src=path.join(tmp,'source');fs.mkdirSync(src);
 assert.notEqual(node('scan-adobe-api.mjs',[src,path.join(tmp,'empty-api')]).status,0);
 const file=path.join(src,'effect.cpp');fs.writeFileSync(file,'int x = PF_Cmd_RENDER;');
 const out=path.join(tmp,'api');assert.equal(node('scan-adobe-api.mjs',[src,out]).status,0);assert.match(fs.readFileSync(path.join(out,'adobe-api-symbols.txt'),'utf8'),/PF_Cmd_RENDER/);
 assert.notEqual(node('scan-adobe-api.mjs',[src,out]).status,0);
 if(process.platform!=='win32' && process.getuid?.()!==0){fs.chmodSync(file,0);try{assert.notEqual(node('scan-adobe-api.mjs',[src,path.join(tmp,'unreadable-api')]).status,0);}finally{fs.chmodSync(file,0o644);}}
});
const posix=process.platform!=='win32'&&run('zsh',['--version']).status===0;
test('A04 preflight rejects staged errors, failing project checks and non-executable hooks',{skip:!posix},()=>{
 const script=path.join(scripts,'preflight.sh'),readme=path.join(repo,'README.md');
 fs.writeFileSync(readme,'bad   \n');run('git',['add','README.md']);assert.notEqual(run('zsh',[script]).status,0);
 fs.writeFileSync(readme,'fixture\n');run('git',['add','README.md']);
 fs.writeFileSync(path.join(repo,'package.json'),JSON.stringify({scripts:{check:'node -e "process.exit(23)"'}}));assert.notEqual(run('zsh',[script]).status,0);
 // Portable missing-tool fixture uses a PATH containing only git and zsh.
 const bin=path.join(tmp,'limited');fs.mkdirSync(bin);for(const tool of ['git','zsh']){const p=run('which',[tool]).stdout.trim();fs.symlinkSync(p,path.join(bin,tool));}
 assert.notEqual(run('zsh',[script],{env:{...process.env,PATH:bin}}).status,0);
 fs.unlinkSync(path.join(repo,'package.json'));fs.mkdirSync(path.join(repo,'scripts'));fs.writeFileSync(path.join(repo,'scripts/project-preflight.sh'),'#!/bin/sh\nexit 0\n');assert.notEqual(run('zsh',[script]).status,0);
 fs.chmodSync(path.join(repo,'scripts/project-preflight.sh'),0o755);assert.equal(run('zsh',[script]).status,0);
});
test('A11 rejects symlink root and configured ancestor',{skip:!posix},()=>{
 const real=path.join(tmp,'workspace-real'),alias=path.join(tmp,'workspace-alias');fs.mkdirSync(real);fs.symlinkSync(real,alias,'dir');
 for(const base of [alias,path.join(alias,'child')]) assert.notEqual(node('create-owned-test-workspace.mjs',[],{env:{...process.env,AE_TEST_WORKSPACE_ROOT:base}}).status,0);
 const ok=node('create-owned-test-workspace.mjs',[],{env:{...process.env,AE_TEST_WORKSPACE_ROOT:path.join(real,'child')}});assert.equal(ok.status,0,ok.stderr);assert.ok(fs.existsSync(path.join(ok.stdout.trim(),'OWNERSHIP.txt')));
});
test('A08 invalid Mach-O never collects COMPLETE',{skip:process.platform!=='darwin'},()=>{
 const plain=path.join(tmp,'plain.txt');fs.writeFileSync(plain,'not binary');assert.notEqual(run('zsh',[path.join(scripts,'macos-binary-audit.sh'),plain,path.join(tmp,'plain-audit')]).status,0);
});
test('A08 valid Mach-O with a failed required probe reports PARTIAL',{skip:process.platform!=='darwin'},()=>{
 const bin=path.join(tmp,'binary-stubs');fs.mkdirSync(bin);const code=path.join(bin,'codesign');fs.writeFileSync(code,'#!/bin/sh\nexit 7\n');fs.chmodSync(code,0o755);
 const output=path.join(tmp,'partial-macho.txt');const r=run('zsh',[path.join(scripts,'macos-binary-audit.sh'),process.execPath,output],{env:{...process.env,PATH:bin+path.delimiter+process.env.PATH}});
 assert.equal(r.status,2,r.stderr);const report=fs.readFileSync(output,'utf8');assert.match(report,/probe_exit=7/);assert.match(report,/collection_status=PARTIAL/);assert.ok(!report.includes('collection_status=COMPLETE'));
});
test('A12 required stapling failure blocks; explicit N/A needs a reason',{skip:!posix},()=>{
 const bin=path.join(tmp,'stubs');fs.mkdirSync(bin);
 for(const [name,body] of Object.entries({codesign:'exit 0',spctl:'exit 0',xattr:'exit 0',xcrun:'exit 65'})){const p=path.join(bin,name);fs.writeFileSync(p,'#!/bin/sh\n'+body+'\n');fs.chmodSync(p,0o755);}
 const app=path.join(tmp,'fixture.app');fs.mkdirSync(app);const env={...process.env,PATH:bin+path.delimiter+process.env.PATH};
 const script=path.join(scripts,'macos-bundle-verify.sh');
 assert.notEqual(run('zsh',[script,app,path.join(tmp,'staple-fail'),'public','required'],{env}).status,0);
 assert.notEqual(run('zsh',[script,app,path.join(tmp,'staple-na'),'local','na'],{env}).status,0);
 assert.equal(run('zsh',[script,app,path.join(tmp,'staple-na-reason'),'local','na'],{env:{...env,AE_STAPLING_NA_REASON:'project format excludes stapling'}}).status,0);
});
test('A01 empty resource cannot pass structural bundle check',{skip:process.platform!=='darwin'},()=>{
 const bundle=path.join(tmp,'Fake.plugin'),contents=path.join(bundle,'Contents');fs.mkdirSync(path.join(contents,'MacOS'),{recursive:true});fs.mkdirSync(path.join(contents,'Resources'));
 fs.writeFileSync(path.join(contents,'Info.plist'),'<?xml version="1.0"?><plist version="1.0"><dict><key>CFBundleIdentifier</key><string>invalid.fixture</string><key>CFBundleExecutable</key><string>Fake</string></dict></plist>');
 const c=path.join(tmp,'fake.c');fs.writeFileSync(c,'void EffectMain(void){}\nvoid PluginDataEntryFunction2(void){}\n');assert.equal(run('clang',['-dynamiclib',c,'-o',path.join(contents,'MacOS/Fake')]).status,0);
 fs.writeFileSync(path.join(contents,'Resources/Fake.rsrc'),'');
 const r=run('zsh',[path.join(scripts,'verify-native-effect-bundle-macos.sh'),bundle]);assert.notEqual(r.status,0);assert.match(r.stdout+r.stderr,/empty resource/);
});
const ps=['pwsh','powershell'].find(cmd=>run(cmd,['-NoLogo','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()']).status===0);
test('A13 Windows timestamp and failing dumpbin contracts',{skip:!ps||process.platform!=='win32'},()=>{
 const target=path.join(tmp,'fake.exe');fs.writeFileSync(target,'fixture');const harness=path.join(tmp,'windows-fixture.ps1');
 const dumpbin=path.join(tmp,'dumpbin.cmd');fs.writeFileSync(dumpbin,'@echo off\r\necho fixture probe failure\r\nexit /b 7\r\n');
 fs.writeFileSync(harness,`param([string]$Script,[string]$Target,[string]$Output,[string]$Kind,[string]$Dumpbin)\nfunction Get-AuthenticodeSignature { [pscustomobject]@{ Status='Valid'; StatusMessage='fixture'; SignerCertificate=$null; TimeStamperCertificate=$null } }\nif ($Kind -eq 'timestamp') { & $Script -Target $Target -Output $Output }\nelse { function Get-Command { [CmdletBinding()]param([string]$Name); if ($Name -eq 'dumpbin.exe') { [pscustomobject]@{ Source=$Dumpbin } } else { Microsoft.PowerShell.Core\\Get-Command $Name } }; & $Script -Target $Target -Output $Output }\nif ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n`);
 const timestampOutput=path.join(tmp,'timestamp.txt');
 const timestamp=run(ps,['-NoProfile','-File',harness,path.join(scripts,'windows-release-verify.ps1'),target,timestampOutput,'timestamp',dumpbin]);assert.notEqual(timestamp.status,0);assert.match(fs.readFileSync(timestampOutput,'utf8'),/timestamp=BLOCKED/);
 const binaryOutput=path.join(tmp,'dumpbin.txt');
 const binary=run(ps,['-NoProfile','-File',harness,path.join(scripts,'windows-binary-audit.ps1'),target,binaryOutput,'binary',dumpbin]);const report=fs.readFileSync(binaryOutput,'utf8');assert.notEqual(binary.status,0,binary.stdout+binary.stderr+report);assert.match(report,/headers_exit=7/);assert.match(report,/collection_status=PARTIAL/);
});
console.log(`coverage: hardening POSIX=${posix?'RUN':'NOT RUN'}; macOS native=${process.platform==='darwin'?'RUN':'NOT RUN'}; Windows contracts=${ps&&process.platform==='win32'?'RUN':'NOT RUN'}`);

test('A04 PowerShell preflight rejects staged errors and failing project hook',{skip:!ps||process.platform!=='win32'},()=>{
 const readme=path.join(repo,'README.md'),script=path.join(scripts,'preflight.ps1');
 fs.writeFileSync(readme,'bad   \n');assert.equal(run('git',['add','README.md']).status,0);assert.notEqual(run(ps,['-NoProfile','-File',script]).status,0);
 fs.writeFileSync(readme,'fixture\n');assert.equal(run('git',['add','README.md']).status,0);fs.mkdirSync(path.join(repo,'scripts'),{recursive:true});const hook=path.join(repo,'scripts/project-preflight.ps1');
 fs.writeFileSync(hook,'exit 23');assert.notEqual(run(ps,['-NoProfile','-File',script]).status,0);fs.writeFileSync(hook,'Write-Host "fixture success"');assert.equal(run(ps,['-NoProfile','-File',script]).status,0);
});
