import fs from 'node:fs';
import path from 'node:path';
import { validate } from './schema.mjs';
import { safePath } from './files.mjs';
const overlays = {
  'DEBUGGING': ['core/ENGINEERING.md', '16'],
  'API-SOURCES': ['core/PROCESS.md', '3'],
  'PRODUCT-DISCOVERY': ['PRODUCT_DISCOVERY.md', '0'],
  'REFERENCE-AUDIT': ['REFERENCE_AUDIT.md', 'R0']
};
export const featureRules = {
  parallel: ['PARALLEL'],
  architecture: ['ARCHITECTURE', 'TESTABILITY'],
  'decision-grill': ['DECISION-GRILL'],
  workaround: ['TECH-DEBT'],
  quality: ['QUALITY'],
  testing: ['TEST-CASES', 'TEST-CONTROL'],
  adoption: ['ADOPTION', 'STANDARD-VERSION'],
  versioning: ['PRODUCT-VERSION'],
  updater: ['UPDATES', 'PRODUCT-VERSION', 'DEPSEC', 'CODE-SAFETY', 'TOOL-RUNTIME'],
  diagnostics: ['CRASH-DIAGNOSTICS', 'DEBUGGING'],
  ui: ['ACCESSIBILITY', 'TOOL-RUNTIME'],
  ipc: ['TOOL-RUNTIME', 'CODE-SAFETY'],
  performance: ['PERF', 'REPRO'],
  'mac-distribution': ['MAC-DIST'],
  'windows-distribution': ['WIN-DIST'],
  porting: ['PORTING']
};
function sections(value) {
  if (value === 'R0') return ['R0'];
  if (!/^(0|[1-9]\d*)(?:-(0|[1-9]\d*))?$/.test(value)) throw new Error('invalid section range');
  const [start, end = start] = value.split('-').map(Number);
  // Canonical headings are checked below; this bound prevents enormous allocations.
  if (![start,end].every(n => Number.isSafeInteger(n) && n <= 1000) || start > end) throw new Error('invalid section range');
  return Array.from({length:end-start+1}, (_,i) => String(start+i));
}
export function loadManifest(root) {
  root = path.resolve(root);
  if (fs.lstatSync(root).isSymbolicLink()) throw new Error('standard root is a symlink');
  root = fs.realpathSync(root);
  const read = relative => {
    const source = safePath(root, path.resolve(root, relative));
    if (!fs.lstatSync(source).isFile()) throw new Error('canonical source is not an ordinary file');
    return fs.readFileSync(source, 'utf8');
  };
  // JSON is a YAML 1.2 subset; this file deliberately uses only JSON notation.
  const m = validate(JSON.parse(read('rules-manifest.yaml')), JSON.parse(read('starter-kit/schemas/rules-manifest.schema.json')));
  const exact = (items, expected, name) => {
    const ids = items.map(x => x.id);
    if (new Set(ids).size !== ids.length || [...ids].sort().join() !== [...expected].sort().join()) throw new Error('invalid ' + name + ' IDs');
  };
  exact(m.risk_profiles, ['light','standard','critical'], 'risk');
  exact(m.delivery_gates, ['development','validation','release'], 'delivery');
  exact(m.artifact_profiles, ['native','jsx','cep','uxp','helper'], 'artifact');
  const ids = new Set();
  const mapped = new Set();
  for (const g of m.rule_groups) {
    if (ids.has(g.id)) throw new Error('duplicate rule group: ' + g.id);
    ids.add(g.id);
    const text = read(g.source);
    for (const section of sections(g.section)) {
      if (!new RegExp('^## ' + section + '\\.', 'm').test(text)) throw new Error('missing canonical section ' + section);
      mapped.add(g.source + ':' + section);
    }
    if (g.applicability === 'conditional' && !g.trigger) throw new Error('conditional trigger missing');
  }
  for (const [id, [source, section]] of Object.entries(overlays)) {
    const g = m.rule_groups.find(g => g.id === id);
    if (!g || g.source !== source || g.section !== section) throw new Error('task overlay contract missing/incorrect: ' + id);
  }
  for (const [feature, rules] of Object.entries(featureRules)) {
    for (const id of rules) if (!ids.has(id)) throw new Error('feature rule missing: ' + feature + '/' + id);
  }
  // Every numbered canonical section must have a reading-map entry; conditional
  // entries remain conditional, rather than loading every section for every edit.
  for (const source of ['core/PROCESS.md','core/ENGINEERING.md','profiles/TOOLS.md','profiles/NATIVE.md','profiles/RELEASE.md','profiles/UXP.md']) {
    for (const heading of read(source).matchAll(/^## (\d+)\./gm)) {
      if (!mapped.has(source + ':' + heading[1])) throw new Error('unmapped canonical section: ' + source + ':' + heading[1]);
    }
  }
  const ref = m.rule_groups.find(g => g.id === 'REFERENCE-AUDIT');
  if (ref?.trigger !== 'explicit_external_reference' || ref.source !== 'REFERENCE_AUDIT.md') throw new Error('reference trigger contract missing');
  for (const p of m.artifact_profiles) {
    if (p.light.inherit !== '' || p.standard.inherit !== 'light' || p.critical.inherit !== 'standard' || p.validation.inherit !== '' || p.release.inherit !== '') throw new Error('invalid profile inheritance');
    for (const key of ['light','standard','critical','validation','release']) {
      for (const rule of p[key].rules) if (!ids.has(rule)) throw new Error('unknown rule: ' + rule);
    }
    if (!p.light.rules.includes('CORE-SCOPE') || !p.validation.rules.includes('GATES') || !p.release.rules.includes('GATES')) throw new Error('profile is missing core/delivery requirements');
    if (p.id !== 'native' && !rulesFor(p,'light').includes('TOOL-RUNTIME')) throw new Error('tool runtime minimum missing: ' + p.id);
    if (!rulesFor(p,'critical').includes('CODE-SAFETY')) throw new Error('critical code safety missing: ' + p.id);
  }
  return m;
}
export function rulesFor(profile, risk) {
  const cell = profile[risk];
  return [...new Set([...(cell.inherit ? rulesFor(profile, cell.inherit) : []), ...cell.rules])];
}
export function route(manifest, context) {
  const allowed = ['audit','documentation','research','bugfix','improvement','new-product','major-feature'];
  if (!allowed.includes(context.task) || !['light','standard','critical'].includes(context.risk) || !['development','validation','release'].includes(context.delivery)) throw new Error('invalid routing context');
  if (!Array.isArray(context.components) || !context.components.length || new Set(context.components).size !== context.components.length) throw new Error('components required');
  for (let i = 0; i < context.components.length; i++) {
    if (!Object.hasOwn(context.components, i) || typeof context.components[i] !== 'string') throw new Error('dense component identifiers required');
  }
  if (!['none','feature','ui','behavior','whole-product'].includes(context.reference)) throw new Error('invalid reference context');
  for (const key of ['product_contract','contract_covers_scope','changes_product_contract']) {
    if (typeof context[key] !== 'boolean') throw new Error('invalid product context: ' + key);
  }
  if (!context.product_contract && context.contract_covers_scope) throw new Error('a missing product contract cannot cover the current scope');
  const features = Object.hasOwn(context, 'features') ? context.features : [];
  if (!Array.isArray(features) || new Set(features).size !== features.length) throw new Error('invalid feature context');
  for (let i = 0; i < features.length; i++) {
    if (!Object.hasOwn(features, i) || typeof features[i] !== 'string' || !Object.hasOwn(featureRules, features[i])) throw new Error('unknown/non-dense feature context');
  }
  const selected = context.components.map(id => {
    const p = manifest.artifact_profiles.find(p => p.id === id);
    if (!p) throw new Error('unknown component');
    return [...(context.task === "documentation" ? ["CORE-SCOPE","GIT","DOCS","EVIDENCE","STATE","WORKFLOW","STANDARD-VERSION"] : rulesFor(p, context.risk)), ...(context.delivery === 'development' ? [] : p[context.delivery].rules)];
  });
  const implementation = !['audit','documentation','research'].includes(context.task);
  const currentContract = context.product_contract && context.contract_covers_scope;
  const productChange = ['new-product','major-feature'].includes(context.task) || context.changes_product_contract;
  const discovery = implementation && productChange && !currentContract;
  const reference = context.reference !== 'none' && !['audit','documentation','research'].includes(context.task);
  const taskRules = [...(context.task === 'bugfix' ? ['DEBUGGING'] : []), ...(implementation || context.task === 'research' ? ['API-SOURCES'] : [])];
  const rules = [...new Set([...selected.flat(),...taskRules,...features.flatMap(feature => featureRules[feature]),...(discovery ? ['PRODUCT-DISCOVERY'] : []),...(reference ? ['REFERENCE-AUDIT'] : [])])];
  const defined = new Set(manifest.rule_groups.map(g => g.id));
  for (const id of rules) if (!defined.has(id)) throw new Error('selected rule is undefined: ' + id);
  return { risk:context.risk, delivery:context.delivery, product_discovery:discovery, reference_audit:reference, implementation_task:implementation, rules };
}
