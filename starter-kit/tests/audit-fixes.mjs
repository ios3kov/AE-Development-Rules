import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {anchors, links, slug, checkLinks} from '../scripts/lib/markdown-links.mjs';
import {checkDocsScope} from '../scripts/lib/preflight-docs.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ae-audit-fixes-'));
let checks = 0;
const test = (name, fn) => { fn(); checks++; console.log('PASS: ' + name); };
function run(cmd, args, cwd = tmp, env = process.env) {
  return spawnSync(cmd, args, {cwd, env, encoding:'utf8', timeout:30000});
}
function git(...args) {
  const r = run('git', args); assert.equal(r.status, 0, r.stderr); return r.stdout.trim();
}
try {
  test('Unicode, formatting, code identifiers and punctuation', () => {
    assert.equal(slug('23. Дополнительные проверки Native Effects / Render Plugins'), '23-дополнительные-проверки-native-effects--render-plugins');
    assert.equal(slug('**Bold** _words_ `PF_Cmd_RENDER`'), 'bold-words-pf_cmd_render');
  });
  test('Duplicate collision order and explicit anchors', () => {
    assert.deepEqual([...anchors('# A\n# A\n# A-1\n# A\n<a name="legacy"></a>')], ['legacy','a','a-1','a-1-1','a-2']);
    assert(anchors('Name\n====\n\nOther\n-----').has('other'));
  });
  test('Code and comments cannot manufacture anchors or links', () => {
    const source = '<!-- # Fake -->\n```md\n# Fake\n[x](missing.md)\n```\n    # Fake\n`[x](missing.md)`\n# Real';
    assert.deepEqual([...anchors(source)], ['real']); assert.equal(links(source).length, 0);
  });
  test('Inline, angle, balanced parentheses and reference destinations', () => {
    assert.deepEqual(links('[a](a(b).md#ok "title") [b](<a b.md#ok>) [c][id]\n[id]: file.md#ok\n[id][]\n[id]').map(x=>x.url), ['a(b).md#ok','a b.md#ok','file.md#ok','file.md#ok','file.md#ok']);
  });
  test('Existing file with missing anchor is rejected; encoded and local anchors work', () => {
    fs.writeFileSync(path.join(tmp, 'a.md'), '# Якорь\n[a](b.md#missing)\n[local](#%D1%8F%D0%BA%D0%BE%D1%80%D1%8C)');
    fs.writeFileSync(path.join(tmp, 'b.md'), '# Other');
    const errors = checkLinks(tmp); assert.equal(errors.length, 1); assert.match(errors[0], /missing Markdown anchor/);
    fs.writeFileSync(path.join(tmp, 'b.md'), '# Other\n<a id="missing"></a>'); assert.deepEqual(checkLinks(tmp), []);
  });
  git('init','-q'); git('config','user.name','Audit Fixture'); git('config','user.email','audit@example.invalid');
  git('add','.'); git('commit','-qm','fixture');
  const base = git('rev-parse','HEAD');
  test('Docs-only recognizes ordinary modified documentation', () => {
    fs.appendFileSync(path.join(tmp, 'a.md'), '\nMore\n'); assert.deepEqual(checkDocsScope(tmp, ''), ['a.md']);
  });
  test('Docs-only blocks untracked and committed code, including deleted code', () => {
    fs.writeFileSync(path.join(tmp,'broken.jsx'), 'var = ;\n'); assert.throws(()=>checkDocsScope(tmp, ''), /non-documentation/);
    git('add','.'); git('commit','-qm','code'); assert.throws(()=>checkDocsScope(tmp, base), /non-documentation/);
    fs.unlinkSync(path.join(tmp,'broken.jsx')); assert.throws(()=>checkDocsScope(tmp, ''), /non-documentation/);
    git('add','.'); git('commit','-qm','remove fixture code');
  });
  test('Docs-only blocks staged executable documents and invalid base', () => {
    git('update-index','--chmod=+x','a.md'); assert.throws(()=>checkDocsScope(tmp, ''), /special/);
    git('update-index','--chmod=-x','a.md'); assert.throws(()=>checkDocsScope(tmp, 'not-a-ref'), /Git scope unavailable/);
  });
  const runners = [];
  if (run('zsh',['--version']).status === 0) runners.push(['zsh',[path.join(root,'starter-kit/scripts/preflight.sh')], '--docs-only']);
  for (const shell of ['pwsh','powershell']) {
    if (run(shell,['-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()']).status === 0) {
      runners.push([shell,['-NoProfile','-File',path.join(root,'starter-kit/scripts/preflight.ps1')], '-DocsOnly']); break;
    }
  }
  for (const [cmd,args,docs] of runners) {
    const env = {...process.env, AE_PREFLIGHT_BASE_REF:''};
    test(cmd + ': missing code checks block, never PASS', () => {
      fs.writeFileSync(path.join(tmp,'broken.jsx'),'var = ;\n');
      fs.writeFileSync(path.join(tmp,'package.json'),'{"scripts":{}}');
      const r=run(cmd,args,tmp,env); assert.equal(r.status,2,r.stderr+r.stdout); assert.doesNotMatch(r.stdout,/\[preflight\] PASS/);
      assert.notEqual(run(cmd,[...args,docs],tmp,env).status,0);
      fs.unlinkSync(path.join(tmp,'broken.jsx')); fs.unlinkSync(path.join(tmp,'package.json'));
    });
    test(cmd + ': docs-only is explicit and narrow', () => {
      const r=run(cmd,[...args,docs],tmp,env); assert.equal(r.status,0,r.stderr+r.stdout); assert.match(r.stdout,/code\/AE checks: NOT RUN/);
    });
    test(cmd + ': real project check pass/fail propagates', () => {
      fs.writeFileSync(path.join(tmp,'verify.cjs'),'process.exit(0);\n');
      fs.writeFileSync(path.join(tmp,'package.json'),JSON.stringify({scripts:{check:'node verify.cjs'}}));
      let r=run(cmd,args,tmp,env); assert.equal(r.status,0,r.stderr+r.stdout); assert.match(r.stdout,/1 configured project check/);
      fs.writeFileSync(path.join(tmp,'verify.cjs'),'process.exit(7);\n');
      r=run(cmd,args,tmp,env); assert.notEqual(r.status,0); assert.doesNotMatch(r.stdout,/\[preflight\] PASS/);
      fs.unlinkSync(path.join(tmp,'verify.cjs')); fs.unlinkSync(path.join(tmp,'package.json'));
    });
  }
  if (!runners.length) console.log('NOT RUN: supported zsh/PowerShell wrapper execution unavailable');
  if (process.argv.includes('--repository')) test('All repository Markdown destinations and anchors', () => {
    const errors=checkLinks(root); assert.deepEqual(errors, [], errors.join('\n'));
  });
} finally { fs.rmSync(tmp, {recursive:true, force:true}); }
console.log('audit-fixes: PASS ('+checks+' checks)');
