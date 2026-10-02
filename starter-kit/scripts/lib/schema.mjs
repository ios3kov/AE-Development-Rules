// Deliberately small JSON Schema subset used by the checked-in schemas.
// Unsupported schema keywords fail closed rather than being silently ignored.
// Object member order is irrelevant in JSON; array order remains significant.
function jsonKey(value, active = new Set(), depth = 0, budget = { nodes: 0 }) {
  if (depth > 64 || ++budget.nodes > 100000) throw new Error('JSON comparison limit exceeded');
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'number' && Number.isFinite(value)) return JSON.stringify(value);
  if (!value || typeof value !== 'object') throw new Error('non-JSON comparison value');
  if (active.has(value)) throw new Error('cyclic JSON comparison value');
  active.add(value);
  try {
    if (Array.isArray(value)) {
      const parts = [];
      for (let i = 0; i < value.length; i++) {
        if (!Object.hasOwn(value, i)) throw new Error('dense own array items required');
        parts.push(jsonKey(value[i], active, depth + 1, budget));
      }
      return '[' + parts.join(',') + ']';
    }
    const proto = Object.getPrototypeOf(value);
    if (proto !== Object.prototype && proto !== null) throw new Error('plain JSON object required');
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + jsonKey(value[key], active, depth + 1, budget)).join(',') + '}';
  } finally { active.delete(value); }
}
export function validate(value, schema, at = '$', depth = 0, budget = { nodes: 0 }) {
  if (depth > 64 || ++budget.nodes > 100000) throw new Error(at + ': validation limit exceeded');
  const allowed = new Set(['$schema','title','description','type','required','properties','additionalProperties','items','minItems','uniqueItems','enum','const','pattern','minimum','minLength']);
  for (const key of Object.keys(schema)) if (!allowed.has(key)) throw new Error('unsupported schema keyword: ' + key);
  const type = Array.isArray(value) ? 'array' : value === null ? 'null' : Number.isInteger(value) ? 'integer' : typeof value;
  if (schema.type && type !== schema.type && !(schema.type === 'number' && type === 'integer')) throw new Error(at + ': expected ' + schema.type);
  if ('const' in schema && jsonKey(value) !== jsonKey(schema.const)) throw new Error(at + ': incorrect constant');
  if (schema.enum && !schema.enum.includes(value)) throw new Error(at + ': invalid enum');
  if (typeof value === 'string') {
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) throw new Error(at + ': invalid pattern');
    if (value.length < (schema.minLength || 0)) throw new Error(at + ': empty string');
  }
  if (typeof value === 'number' && schema.minimum !== undefined && value < schema.minimum) throw new Error(at + ': below minimum');
  if (Array.isArray(value)) {
    if (value.length < (schema.minItems || 0)) throw new Error(at + ': insufficient items');
    const keys = new Set();
    const comparisonBudget = { nodes: 0 };
    for (let i = 0; i < value.length; i++) {
      if (!Object.hasOwn(value, i)) throw new Error(at + ': dense own array items required');
      validate(value[i], schema.items || {}, `${at}[${i}]`, depth + 1, budget);
      if (schema.uniqueItems) {
        const key = jsonKey(value[i], new Set(), 0, comparisonBudget);
        if (keys.has(key)) throw new Error(at + ': duplicate item');
        keys.add(key);
      }
    }
  } else if (value && typeof value === 'object') {
    for (const key of schema.required || []) if (!Object.hasOwn(value, key)) throw new Error(at + ': missing ' + key);
    for (const [key, v] of Object.entries(value)) {
      if (schema.properties && Object.hasOwn(schema.properties, key)) validate(v, schema.properties[key], at + '.' + key, depth + 1, budget);
      else if (schema.additionalProperties === false) throw new Error(at + ': unknown key ' + key);
    }
  }
  return value;
}
