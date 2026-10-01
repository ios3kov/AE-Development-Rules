// Deliberately small JSON Schema subset used by the checked-in schemas.
// Unsupported schema keywords fail closed rather than being silently ignored.
export function validate(value, schema, at = '$') {
  const allowed = new Set(['$schema','title','description','type','required','properties','additionalProperties','items','minItems','uniqueItems','enum','const','pattern','minimum','minLength']);
  for (const key of Object.keys(schema)) if (!allowed.has(key)) throw new Error('unsupported schema keyword: ' + key);
  const type = Array.isArray(value) ? 'array' : value === null ? 'null' : Number.isInteger(value) ? 'integer' : typeof value;
  if (schema.type && type !== schema.type && !(schema.type === 'number' && type === 'integer')) throw new Error(at + ': expected ' + schema.type);
  if ('const' in schema && JSON.stringify(value) !== JSON.stringify(schema.const)) throw new Error(at + ': incorrect constant');
  if (schema.enum && !schema.enum.includes(value)) throw new Error(at + ': invalid enum');
  if (typeof value === 'string') {
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) throw new Error(at + ': invalid pattern');
    if (value.length < (schema.minLength || 0)) throw new Error(at + ': empty string');
  }
  if (typeof value === 'number' && schema.minimum !== undefined && value < schema.minimum) throw new Error(at + ': below minimum');
  if (Array.isArray(value)) {
    if (value.length < (schema.minItems || 0)) throw new Error(at + ': insufficient items');
    if (schema.uniqueItems && new Set(value.map(v => JSON.stringify(v))).size !== value.length) throw new Error(at + ': duplicate item');
    value.forEach((v, i) => validate(v, schema.items || {}, `${at}[${i}]`));
  } else if (value && typeof value === 'object') {
    for (const key of schema.required || []) if (!(key in value)) throw new Error(at + ': missing ' + key);
    for (const [key, v] of Object.entries(value)) {
      if (schema.properties?.[key]) validate(v, schema.properties[key], at + '.' + key);
      else if (schema.additionalProperties === false) throw new Error(at + ': unknown key ' + key);
    }
  }
  return value;
}
