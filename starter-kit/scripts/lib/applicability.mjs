import fs from 'node:fs';
import path from 'node:path';
import { validate } from './schema.mjs';
function sections(value) {
  if (value === 'R0') return ['R0'];
  if (!/^(0|[1-9]\d*)(?:-(0|[1-9]\d*))?$/.test(value)) throw new Error('invalid section range');
  const [start, end = start] = value.split('-').map(Number);
  // Canonical headings are checked below; this bound prevents enormous allocations.
  if (![start,end].every(n => Number.isSafeInteger(n) && n <= 1000) || start > end) throw new Error('invalid section range');
  return Array.from({length:end-start+1}, (_,i) => String(start+i));
}
export function loadManifest(root) {
  // JSON is a YAML 1.2 subset; this file deliberately uses only JSON notation.
  const m = validate(JSON.parse(fs.readFileSync(path.join(root, 'rules-manifest.yaml'), 'utf8')), JSON.parse(fs.readFileSync(path.join(root, 'starter-kit/schemas/rules-manifest.schema.json'), 'utf8')));
  const exact = (items, expected, name) => {
    const ids = items.map(x => x.id);
    if (new Set(ids).size !== ids.length || [...ids].sort().join() !== [...expected].sort().join()) throw new Error('invalid ' + name + ' IDs');
  };
  exact(m.risk_profiles, ['light','standard','critical'], 'risk');
  exact(m.delivery_gates, ['development','validation','release'], 'delivery');
  exact(m.artifact_profiles, ['native','jsx','cep','uxp','helper'], 'artifact');
  const ids = new Set();
  for (const g of m.rule_groups) {
    if (ids.has(g.id)) throw new Error('duplicate rule group: ' + g.id);
    ids.add(g.id);
    const source = path.resolve(root, g.source);
    if (!source.startsWith(root + path.sep)) throw new Error('canonical source escapes root');
    const text = fs.readFileSync(source, 'utf8');
    for (const section of sections(g.section)) {
      if (!new RegExp('^## ' + section + '\\.', 'm').test(text)) throw new Error('missing canonical section ' + section);
    }
    if (g.applicability === 'conditional' && !g.trigger) throw new Error('conditional trigger missing');
  }
  const ref = m.rule_groups.find(g => g.id === 'REFERENCE-AUDIT');
  if (ref?.trigger !== 'explicit_external_reference' || ref.source !== 'REFERENCE_AUDIT.md') throw new Error('reference trigger contract missing');
  for (const p of m.artifact_profiles) {
    for (const key of ['light','standard','critical','validation','release']) {
      for (const rule of p[key].rules) if (!ids.has(rule)) throw new Error('unknown rule: ' + rule);
    }
    if (!p.light.rules.includes('CORE-SCOPE') || !p.validation.rules.includes('GATES') || !p.release.rules.includes('GATES')) throw new Error('profile is missing core/delivery requirements');
    if (p.light.inherit !== '' || p.standard.inherit !== 'light' || p.critical.inherit !== 'standard' || p.validation.inherit !== '' || p.release.inherit !== '') throw new Error('invalid profile inheritance');
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
  const selected = context.components.map(id => {
    const p = manifest.artifact_profiles.find(p => p.id === id);
    if (!p) throw new Error('unknown component');
    return [...(context.task === "documentation" ? ["CORE-SCOPE","GIT","DOCS","EVIDENCE"] : rulesFor(p, context.risk)), ...(context.delivery === 'development' ? [] : p[context.delivery].rules)];
  });
  const implementation = !['audit','documentation','research'].includes(context.task);
  const currentContract = context.product_contract && context.contract_covers_scope;
  const productChange = ['new-product','major-feature'].includes(context.task) || context.changes_product_contract;
  const discovery = implementation && productChange && !currentContract;
  const reference = context.reference !== 'none' && !['audit','documentation','research'].includes(context.task);
  const taskRules = [...(context.task === 'bugfix' ? ['DEBUGGING'] : []), ...(implementation || context.task === 'research' ? ['API-SOURCES'] : [])];
  return { risk:context.risk, delivery:context.delivery, product_discovery:discovery, reference_audit:reference, implementation_task:implementation, rules:[...new Set([...selected.flat(),...taskRules,...(discovery ? ['PRODUCT-DISCOVERY'] : []),...(reference ? ['REFERENCE-AUDIT'] : [])])] };
}
