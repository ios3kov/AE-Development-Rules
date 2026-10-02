// The standard currently supports normal SemVer only, without prerelease/build suffixes.
const normal = '(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)';
export function checkVersion(versionText, readme, changelog) {
  const version = versionText.trim();
  if (!new RegExp('^' + normal + '$').test(version)) throw new Error('VERSION is not normal semver: ' + version);
  // Read the one authoritative field, never an incidental release link or substring.
  const fields = [...readme.matchAll(/^\*\*(?:Стабильная версия стандарта|Версия текущего checkout): (.+)\*\*\r?$/gm)];
  if (fields.length !== 1) throw new Error('README must have one authoritative version field');
  const field = fields[0][1].match(new RegExp('^v(' + normal + ') — (.+)\\.$'));
  if (!field || field[1] !== version) throw new Error('README baseline does not match VERSION ' + version);
  const current = changelog.match(/^## ([^\s]+) — .+\r?$/m);
  if (!current || current[1] !== version) throw new Error('CHANGELOG current version does not match VERSION ' + version);
  return version;
}
