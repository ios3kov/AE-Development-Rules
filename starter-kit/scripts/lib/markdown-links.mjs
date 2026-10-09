// Repository Markdown link checks, not a general Markdown renderer or web crawler.
// Supported: ATX/setext headings, inline/reference links, HTML id/name anchors,
// duplicate heading suffixes, Unicode/percent escapes; code/comments are inert.
import fs from 'node:fs';
import path from 'node:path';

const blank = s => s.replace(/[^\n]/g, ' ');
export function prose(source) {
  let fence = null;
  return source.replace(/<!--[\s\S]*?-->/g, blank).split('\n').map(line => {
    const m = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if (fence) {
      if (m && m[1][0] === fence[0] && m[1].length >= fence.length && !m[2].trim()) fence = null;
      return blank(line);
    }
    if (m) { fence = m[1]; return blank(line); }
    if (/^( {4}|\t)/.test(line)) return blank(line);
    return line;
  }).join('\n');
}
function withoutCode(source) {
  return source.replace(/(`+)([\s\S]*?)\1(?!`)/g, blank);
}
function entities(text) {
  const named = {amp:'&', lt:'<', gt:'>', quot:'"', apos:"'", nbsp:' '};
  return text.replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (all, name) => {
    if (!name.startsWith('#')) return named[name.toLowerCase()];
    const n = name[1].toLowerCase() === 'x' ? parseInt(name.slice(2), 16) : Number(name.slice(1));
    return n > 0 && n <= 0x10ffff ? String.fromCodePoint(n) : '\ufffd';
  });
}
export function slug(heading) {
  const codes = [];
  let text = heading.replace(/(`+)([\s\S]*?)\1/g, (_, marks, code) => {
    codes.push(code); return '\ue000' + (codes.length - 1) + '\ue001';
  });
  text = text.replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/<[^>]*>/g, '')
    .replace(/\*+/g, '').replace(/~~/g, '')
    .replace(/(?<![\p{L}\p{N}])(_{1,2})(\S[\s\S]*?)\1(?![\p{L}\p{N}])/gu, '$2')
    .replace(/\\([!"#$%&'()*+,\-./:;<=>?@[\]\\^_`{|}~])/g, '$1')
    .replace(/\ue000(\d+)\ue001/g, (_, index) => codes[Number(index)]);
  return entities(text).trim().toLowerCase().replace(/[^\p{L}\p{N}\p{M}_ -]/gu, '').replace(/ /g, '-');
}
export function anchors(source) {
  const body = prose(source), result = new Set(), generated = new Set();
  for (const match of withoutCode(body).matchAll(/<[a-z][^>]*\s(?:id|name)\s*=\s*["']([^"']+)["'][^>]*>/gi)) result.add(entities(match[1]));
  const lines = body.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const atx = lines[i].match(/^ {0,3}#{1,6}(?:[ \t]+(.*?)\s*#*\s*|\s*)$/);
    const setext = !atx && lines[i].trim() && /^ {0,3}(?:=+|-+)\s*$/.test(lines[i + 1] || '');
    if (!atx && !setext) continue;
    const base = slug(atx ? atx[1] || '' : lines[i]);
    let id = base, n = 0;
    while (generated.has(id)) id = base + '-' + (++n);
    generated.add(id); result.add(id);
    if (setext) i++;
  }
  return result;
}
const unescape = s => entities(s.replace(/\\([!"#$%&'()*+,\-./:;<=>?@[\]\\^_`{|}~])/g, '$1'));
function destination(text, start) {
  let i = start;
  while (/\s/.test(text[i] || '') && i < text.length) i++;
  if (text[i] === '<') {
    const end = text.indexOf('>', i + 1);
    return end < 0 ? null : {url: unescape(text.slice(i + 1, end)), end: end + 1};
  }
  const begin = i; let depth = 0;
  while (i < text.length) {
    if (text[i] === '\\' && i + 1 < text.length) { i += 2; continue; }
    if (text[i] === '(') depth++;
    else if (text[i] === ')') { if (!depth) break; depth--; }
    if (/\s/.test(text[i]) && !depth) break;
    i++;
  }
  return {url: unescape(text.slice(begin, i)), end: i};
}
export function links(source) {
  const body = withoutCode(prose(source)), definitions = new Map(), found = [];
  const key = s => s.trim().replace(/\s+/g, ' ').toLowerCase();
  for (const match of body.matchAll(/^ {0,3}\[([^\]]+)\]:[ \t]*(.*)$/gm)) {
    const d = destination(match[2], 0);
    if (d && !definitions.has(key(match[1]))) definitions.set(key(match[1]), d.url);
  }
  for (let i = 0; i < body.length; i++) {
    if (body[i] === '\\') { i++; continue; }
    if (body[i] !== '[') continue;
    const start = i; let depth = 1, j = i + 1;
    for (; j < body.length && depth; j++) {
      if (body[j] === '\\') { j++; continue; }
      if (body[j] === '[') depth++;
      if (body[j] === ']') depth--;
    }
    if (depth) continue;
    const label = body.slice(i + 1, j - 1); let url;
    if (body[j] === '(') {
      const d = destination(body, j + 1);
      if (d) {
        const tail = body.slice(d.end).match(/^\s*(?:"[^"\n]*"|'[^'\n]*'|\([^\n)]*\))?\s*\)/);
        if (tail) { url = d.url; j = d.end + tail[0].length; }
      }
    } else if (body[j] === '[') {
      const end = body.indexOf(']', j + 1);
      if (end >= 0) { url = definitions.get(key(body.slice(j + 1, end) || label)); j = end + 1; }
    } else if (body[j] !== ':') url = definitions.get(key(label));
    if (url !== undefined) found.push({url, line: body.slice(0, start).split('\n').length});
    i = j - 1;
  }
  return found;
}
export function markdownFiles(root) {
  const result = [];
  function visit(dir) {
    for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
      if (['.git', 'node_modules'].includes(entry.name)) continue;
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) visit(file);
      else if (entry.isFile() && /\.md$/i.test(entry.name)) result.push(file);
    }
  }
  visit(root); return result;
}
export function checkLinks(root, files = markdownFiles(root)) {
  root = fs.realpathSync(root);
  const errors = [], cache = new Map();
  for (const file of files) {
    for (const link of links(fs.readFileSync(file, 'utf8'))) {
      const url = link.url;
      if (!url || /^[a-z][a-z\d+.-]*:/i.test(url) || url.startsWith('//')) continue;
      const label = path.relative(root, file) + ':' + link.line + ' -> ' + url;
      try {
        const hash = url.indexOf('#'), rawPath = (hash < 0 ? url : url.slice(0, hash)).split('?')[0];
        const fragment = hash < 0 ? '' : decodeURIComponent(url.slice(hash + 1));
        let target = rawPath ? path.resolve(rawPath.startsWith('/') ? root : path.dirname(file), decodeURIComponent(rawPath).replace(/^\//, '')) : file;
        target = fs.realpathSync(target);
        if (target !== root && !target.startsWith(root + path.sep)) throw new Error('target outside repository');
        if (!fragment) continue;
        if (fs.statSync(target).isDirectory()) target = path.join(target, 'README.md');
        if (!/\.md$/i.test(target)) continue; // Non-Markdown fragments are outside this check.
        if (!cache.has(target)) cache.set(target, anchors(fs.readFileSync(target, 'utf8')));
        if (!cache.get(target).has(fragment)) throw new Error('missing Markdown anchor');
      } catch (error) { errors.push(label + ': ' + error.message); }
    }
  }
  return errors;
}
