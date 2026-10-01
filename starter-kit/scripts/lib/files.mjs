import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
export function inside(root, target) {
  const rel = path.relative(root, target);
  return rel === '' || (!rel.startsWith('..' + path.sep) && rel !== '..' && !path.isAbsolute(rel));
}
// The caller supplies an existing canonical boundary. Every configured descendant
// is checked before creation. This is not a sandbox against concurrent path replacement.
export function safePath(boundary, target) {
  boundary = fs.realpathSync(boundary);
  target = path.resolve(target);
  if (!inside(boundary, target)) throw new Error('path is outside canonical boundary');
  let current = boundary;
  for (const part of path.relative(boundary, target).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try { if (fs.lstatSync(current).isSymbolicLink()) throw new Error('symlinked path component'); }
    catch (e) { if (e.code !== 'ENOENT') throw e; }
  }
  return target;
}
export function snapshot(input) {
  const absolute = path.resolve(input);
  if (fs.lstatSync(absolute).isSymbolicLink()) throw new Error('artifact root is a symlink');
  const root = fs.realpathSync(absolute);
  const entries = [];
  const isDirectory = fs.statSync(root).isDirectory();
  const boundary = isDirectory ? root : path.dirname(root);
  function visit(file, relative) {
    const stat = fs.lstatSync(file);
    const entry = { path: relative.split(path.sep).join('/'), mode: stat.mode & 0o777 };
    if (stat.isSymbolicLink()) {
      const target = fs.readlinkSync(file);
      if (path.isAbsolute(target) || !inside(boundary, fs.realpathSync(file))) throw new Error('external or dangling symlink');
      entries.push({ ...entry, type: 'symlink', target });
    } else if (stat.isDirectory()) {
      entries.push({ ...entry, type: 'directory' });
      for (const name of fs.readdirSync(file).sort()) visit(path.join(file, name), path.join(relative, name));
    } else if (stat.isFile()) {
      // Bounded per file; build/package files larger than 1 GiB need a project collector.
      if (stat.size > 1024 ** 3) throw new Error('artifact file exceeds collector limit');
      const contents = fs.readFileSync(file);
      const after = fs.lstatSync(file);
      if (stat.ino !== after.ino || stat.size !== after.size || stat.mtimeMs !== after.mtimeMs || stat.mode !== after.mode) throw new Error('artifact changed while hashing');
      entries.push({ ...entry, type: 'file', size: contents.length, sha256: sha256(contents) });
    } else throw new Error('unsupported artifact entry');
    if (entries.length > 100000) throw new Error('artifact entry limit exceeded');
  }
  visit(root, '.');
  return { schema_version: 1, platform: process.platform, entries };
}
