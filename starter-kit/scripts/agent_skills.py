#!/usr/bin/env python3
"""Bounded skill-package byte manager. No downloaded/candidate code is executed.

Policy custody and its expected digest belong to an independent verifier (not
candidate arguments). PASS means integrity/admission consistency, not safety,
effectiveness, identity authentication, or Adobe host correctness.
"""
import argparse
from contextlib import contextmanager
import uuid
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
import zipfile

MAX_FILES = 1000
MAX_FILE = 4 * 1024 * 1024
MAX_BYTES = 20 * 1024 * 1024
STATES = {'candidate', 'allowed', 'rejected', 'revoked'}
FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
SHA = re.compile(r'^[0-9a-f]{64}$')
COMMIT = re.compile(r'^[0-9a-f]{40}$')
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

class SkillError(ValueError):
    def __init__(self, message, status='FAIL'):
        super().__init__(message)
        self.status = status

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(value):
    return hashlib.sha256(value).hexdigest()

def strict_json(path):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise SkillError('duplicate JSON key')
            result[key] = value
        return result
    try:
        return json.loads(read_regular(Path(path), MAX_FILE), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(SkillError('non-finite JSON')))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SkillError('invalid JSON') from exc

def exact(obj, required, optional=()):
    if not isinstance(obj, dict) or not set(required) <= set(obj) or set(obj) - set(required) - set(optional):
        raise SkillError('missing or unsupported fields')

def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise SkillError('unsafe package path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise SkillError('unsafe package path')
    if any(ord(c) < 32 for c in value) or any(p.rstrip(' .') != p for p in path.parts):
        raise SkillError('ambiguous package path')
    if any(p.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))} for p in path.parts):
        raise SkillError('platform-reserved package path')
    return path

def unlinked(path):
    path = Path(path).absolute()
    if '..' in path.parts:
        raise SkillError('parent traversal in filesystem argument denied')
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise SkillError('symlink path denied')
    return path

def read_regular(path, limit=MAX_FILE):
    path = unlinked(path)
    try:
        before = path.stat()
        if before.st_mode & 0o7000:
            raise SkillError('special permission bits denied')
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit or before.st_nlink != 1:
            raise SkillError('non-regular, hardlinked, or oversized file')
        # O_NOFOLLOW prevents replacement of final component on supported hosts.
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        with os.fdopen(fd, 'rb') as handle:
            opened = os.fstat(handle.fileno())
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise SkillError('file changed during inspection')
            data = handle.read(limit + 1)
            after = os.fstat(handle.fileno())
        if len(data) > limit or (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise SkillError('file changed or exceeds size limit')
        return data
    except OSError as exc:
        raise SkillError('file unavailable') from exc

def skill_metadata(data, directory_name=None):
    """Read the standard Agent Skills fields, not a new frontmatter dialect.

Portable stdlib parser handles common plain/quoted/block strings and metadata
maps. YAML constructs needing a full YAML parser yield BLOCKED; users may use a
standard YAML parser in an adapter without rewriting compatible skills.
"""
    try:
        text = data.decode('utf-8')
    except UnicodeError as exc:
        raise SkillError('SKILL.md must be UTF-8') from exc
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise SkillError('SKILL.md requires YAML frontmatter')
    try:
        end = lines.index('---', 1)
    except ValueError as exc:
        raise SkillError('unterminated SKILL.md frontmatter') from exc
    values = {}
    i = 1
    while i < end:
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'([a-z][a-z-]*):(?:\s+(.*))?', line)
        if not match:
            raise SkillError('frontmatter needs a full YAML parser', 'BLOCKED')
        key, raw = match.group(1), (match.group(2) or '')
        if key not in FIELDS or key in values:
            raise SkillError('unknown or duplicate standard frontmatter field')
        if key == 'metadata':
            if raw not in ('', '{}'):
                raise SkillError('metadata needs a full YAML parser', 'BLOCKED')
            metadata = {}
            while i < end and (lines[i].startswith('  ') or not lines[i].strip()):
                nested = lines[i].strip()
                i += 1
                if not nested or nested.startswith('#'):
                    continue
                m = re.fullmatch(r'([A-Za-z0-9_.-]+):\s+(.+)', nested)
                if not m or m.group(1) in metadata:
                    raise SkillError('metadata needs a full YAML parser', 'BLOCKED')
                metadata[m.group(1)] = yaml_string(m.group(2))
            values[key] = metadata
        elif raw in ('|', '|-', '|+', '>', '>-', '>+'):
            block = []
            while i < end and (lines[i].startswith('  ') or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith('  ') else '')
                i += 1
            values[key] = ('\n' if raw[0] == '|' else ' ').join(block).strip()
        else:
            values[key] = yaml_string(raw)
    if 'name' not in values or 'description' not in values:
        raise SkillError('name and description required by Agent Skills')
    name = values['name']
    if not NAME.fullmatch(name) or len(name) > 64 or (directory_name is not None and name != directory_name):
        raise SkillError('invalid name or directory-name mismatch')
    if not 1 <= len(values['description']) <= 1024:
        raise SkillError('description must be 1..1024 characters')
    if 'compatibility' in values and not 1 <= len(values['compatibility']) <= 500:
        raise SkillError('compatibility must be 1..500 characters')
    return values

def yaml_string(raw):
    # Plain YAML non-string scalars must not silently become strings. Ambiguous
    # YAML 1.1/1.2 types are delegated to a full parser rather than reinterpreted.
    if (not raw or raw.startswith(('&','*','!','[','{')) or
            raw.lower() in ('null','~','true','false','yes','no','on','off','.nan','.inf','+.inf','-.inf') or
            re.fullmatch(r'[+-]?(?:[0-9][0-9A-Za-z_.:+-]*|\.[0-9][0-9eE+-]*)', raw)):
        raise SkillError('scalar needs a full YAML parser', 'BLOCKED')
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
            if isinstance(value, str):
                return value
        except json.JSONDecodeError:
            pass
        raise SkillError('quoted scalar needs a full YAML parser', 'BLOCKED')
    if raw.startswith("'"):
        if re.fullmatch(r"'(?:[^']|'')*'", raw):
            return raw[1:-1].replace("''", "'")
        raise SkillError('quoted scalar needs a full YAML parser', 'BLOCKED')
    if ': ' in raw or ' #' in raw:
        raise SkillError('scalar needs a full YAML parser', 'BLOCKED')
    return raw

def inventory(package, check_name=True):
    package = unlinked(package)
    if not package.is_dir():
        raise SkillError('package directory unavailable')
    records = []
    seen = set()
    total = 0
    directories = []
    def walk_error(exc):
        # os.walk otherwise silently omits unreadable directories and can seal
        # a partial package as complete. No digest/admission may use that result.
        raise SkillError('package directory unavailable', 'BLOCKED') from exc
    for root, dirs, files in os.walk(package, followlinks=False, onerror=walk_error):
        for name in dirs:
            if (Path(root)/name).stat(follow_symlinks=False).st_mode & 0o7000:
                raise SkillError('special directory permission bits denied')
            if (Path(root)/name).is_symlink():
                raise SkillError('package directory symlink denied')
            relative = (Path(root)/name).relative_to(package).as_posix()
            safe_relative(relative)
            folded = unicodedata.normalize('NFC', relative).casefold()
            if folded in seen:
                raise SkillError('case/unicode path collision')
            seen.add(folded)
            directories.append(relative)
            if len(records) + len(directories) > MAX_FILES:
                raise SkillError('package inventory limit exceeded')
        for name in files:
            path = Path(root)/name
            relative = path.relative_to(package).as_posix()
            safe_relative(relative)
            folded = unicodedata.normalize('NFC', relative).casefold()
            if folded in seen:
                raise SkillError('case/unicode path collision')
            seen.add(folded)
            data = read_regular(path)
            total += len(data)
            if len(records) >= MAX_FILES or total > MAX_BYTES:
                raise SkillError('package inventory limit exceeded')
            records.append({'path':relative, 'size':len(data), 'sha256':digest(data), 'mode':stat.S_IMODE(path.stat().st_mode)})
    if not any(r['path'] == 'SKILL.md' for r in records):
        raise SkillError('SKILL.md missing')
    metadata = skill_metadata(read_regular(package/'SKILL.md'), package.name if check_name else None)
    if len(records) + len(directories) > MAX_FILES:
        raise SkillError('package inventory limit exceeded')
    records.sort(key=lambda row:row['path'])
    directories.sort()
    return {'schema_version':1, 'name':metadata['name'], 'description':metadata['description'], 'metadata':metadata,
            'files':records, 'directories':directories, 'package_sha256':digest(canonical({'files':records,'directories':directories})), 'size':total}

def import_zip(archive, destination):
    """Only local ZIP input; limits are checked before and while extraction."""
    archive = unlinked(archive)
    destination = unlinked(destination)
    if destination.exists():
        raise SkillError('import destination already exists')
    data = read_regular(archive, MAX_BYTES)
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zipped:
            infos = zipped.infolist()
            if len(infos) > MAX_FILES or sum(i.file_size for i in infos) > MAX_BYTES:
                raise SkillError('archive inventory limit exceeded')
            seen = set()
            for info in infos:
                name = info.filename[:-1] if info.is_dir() else info.filename
                safe_relative(name)
                folded = unicodedata.normalize('NFC', name).casefold()
                if folded in seen:
                    raise SkillError('archive duplicate/colliding path')
                seen.add(folded)
                mode = info.external_attr >> 16
                if mode & 0o7000:
                    raise SkillError('archive special permission bits denied')
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR) or info.flag_bits & 1:
                    raise SkillError('archive special file/symlink/encryption denied')
                if info.file_size > MAX_FILE or info.compress_size and info.file_size / info.compress_size > 200:
                    raise SkillError('archive size/compression limit exceeded')
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.skill-import-', dir=destination.parent) as temp:
                stage = Path(temp)/destination.name
                stage.mkdir()
                for info in infos:
                    path = stage/info.filename
                    if info.is_dir():
                        path.mkdir(parents=True, exist_ok=True)
                        continue
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with zipped.open(info) as stream:
                        content = stream.read(MAX_FILE + 1)
                    if len(content) != info.file_size or len(content) > MAX_FILE:
                        raise SkillError('archive bytes disagree with inventory')
                    path.write_bytes(content)
                    path.chmod((info.external_attr >> 16) & 0o777 or 0o600)
                result = inventory(stage)
                if destination.exists():
                    raise SkillError('import destination conflict')
                stage.rename(destination)
                return result
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise SkillError('archive import failed') from exc

SCANNER_CONFIG = {'max_files':MAX_FILES,'max_file':MAX_FILE,'max_bytes':MAX_BYTES,
                  'check_ids':['AGENT-SKILL-PACKAGE-001'],'markers':['process','network','credentials']}

def scan(package):
    inv = inventory(package)
    findings = []
    for record in inv['files']:
        data = read_regular(Path(package)/record['path'])
        if digest(data) != record['sha256']:
            raise SkillError('package changed during scan')
        for marker, pattern in [('process',rb'(?i)\b(exec|eval|subprocess|os\.system|spawn)\b'),
                                ('network',rb'(?i)\b(curl|wget|requests|fetch|https?://)\b'),
                                ('credentials',rb'(?i)(api[_-]?key|password|secret|credential)')]:
            if re.search(pattern, data):
                findings.append({'path':record['path'], 'category':marker})
    if inventory(package)['package_sha256'] != inv['package_sha256']:
        raise SkillError('package changed during scan')
    return {'schema_version':1, 'scan_status':'complete', 'package_sha256':inv['package_sha256'],
            'files':inv['files'], 'findings':findings, 'scanner_id':'stdlib-package-inspector',
            'scanner_version':'1','config_sha256':digest(canonical(SCANNER_CONFIG)),
            'check_ids':SCANNER_CONFIG['check_ids'],'errors':[],'omissions':[], 'security_certified':False,
            'scope':'bounded static byte inventory and heuristic markers; no code execution'}

def utc(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        raise SkillError('UTC timestamp required')
    try:
        return datetime.fromisoformat(value[:-1]+'+00:00')
    except ValueError as exc:
        raise SkillError('invalid timestamp') from exc

def policy_read(policy_path, expected_sha256, candidate_revision, excluded_roots=()):
    path = unlinked(policy_path)
    for root in excluded_roots:
        if path.is_relative_to(unlinked(root)):
            raise SkillError('candidate/install scope cannot contain approval policy')
    data = read_regular(path)
    if not isinstance(expected_sha256,str) or not SHA.fullmatch(expected_sha256) or digest(data) != expected_sha256:
        raise SkillError('protected policy digest mismatch')
    policy = strict_json(path)
    if digest(read_regular(path)) != expected_sha256:
        raise SkillError('policy changed during inspection')
    exact(policy, ('schema_version','candidate_revision','entries','exceptions'), ('telemetry_enabled',))
    if type(policy['schema_version']) is not int or policy['schema_version'] != 1 or not isinstance(candidate_revision,str) or not COMMIT.fullmatch(candidate_revision) or policy['candidate_revision'] != candidate_revision:
        raise SkillError('policy candidate revision mismatch')
    if 'telemetry_enabled' in policy and type(policy['telemetry_enabled']) is not bool:
        raise SkillError('invalid telemetry preference')
    if policy['exceptions'] != []:
        raise SkillError('no scan/isolation/admission bypass exceptions supported', 'BLOCKED')
    if not isinstance(policy['entries'], list):
        raise SkillError('entries must be an array')
    seen = set()
    for entry in policy['entries']:
        exact(entry, ('name','source','source_commit','purpose','license','package_sha256','status','tasks','required_tools','isolation_profile','review','scan'))
        if not isinstance(entry['name'],str) or not NAME.fullmatch(entry['name']) or len(entry['name']) > 64:
            raise SkillError('invalid skill name')
        identity = (entry['name'],str(entry['package_sha256']))
        if identity in seen:
            raise SkillError('duplicate skill version')
        seen.add(identity)
        if not isinstance(entry['status'],str) or entry['status'] not in STATES or not isinstance(entry['source_commit'],str) or not COMMIT.fullmatch(entry['source_commit']) or not isinstance(entry['package_sha256'],str) or not SHA.fullmatch(entry['package_sha256']):
            raise SkillError('invalid registry identity/state')
        for key in ('source','purpose','license'):
            if not isinstance(entry[key],str) or not entry[key].strip():
                raise SkillError('missing source/purpose/license')
        if entry['status'] == 'allowed' and entry['license'].strip().lower() in {'unknown','undefined','unspecified','неопределена','неопределённая'}:
            raise SkillError('license permission unresolved', 'BLOCKED')
        for key in ('tasks','required_tools'):
            if not isinstance(entry[key],list) or any(not isinstance(v,str) or not v for v in entry[key]) or len(set(entry[key])) != len(entry[key]):
                raise SkillError('invalid task/tool list')
        exact(entry['review'], ('reviewer_id','submitter_id','status','reviewed_at','expires_at'))
        for field in ('reviewer_id','submitter_id','status','reviewed_at','expires_at'):
            if not isinstance(entry['review'][field],str):
                raise SkillError('invalid review field')
        exact(entry['scan'], ('status','scanner_id','runner_id','package_sha256','files','findings_reviewed','scanner_version','config_sha256','check_ids','errors','omissions'))
        for field in ('status','scanner_id','runner_id','package_sha256','scanner_version','config_sha256'):
            if not isinstance(entry['scan'][field],str):
                raise SkillError('invalid scan field')
        if not isinstance(entry['scan']['check_ids'],list) or any(not isinstance(v,str) or not v for v in entry['scan']['check_ids']):
            raise SkillError('invalid scan check IDs')
    return policy

def authorize(package, source_commit, policy_path, expected_policy_sha256, candidate_revision,
              isolation_profile='static-read-only', install_root=None, candidate_root=None):
    inv = inventory(package)
    policy = policy_read(policy_path, expected_policy_sha256, candidate_revision,
                         [package] + ([install_root] if install_root else []) + ([candidate_root] if candidate_root else []))
    if candidate_root and not unlinked(package).is_relative_to(unlinked(candidate_root)):
        raise SkillError('package outside candidate root')
    entries = [e for e in policy['entries'] if e['name'] == inv['name'] and e['package_sha256'] == inv['package_sha256']]
    if len(entries) != 1:
        raise SkillError('package missing from protected registry', 'BLOCKED')
    entry = entries[0]
    if entry['status'] != 'allowed':
        raise SkillError('skill admission state '+entry['status'], 'BLOCKED')
    if not COMMIT.fullmatch(source_commit or '') or source_commit != entry['source_commit'] or inv['package_sha256'] != entry['package_sha256']:
        raise SkillError('source/package identity mismatch')
    review, receipt = entry['review'], entry['scan']
    now = datetime.now(timezone.utc)
    if review['status'] != 'APPROVED' or not review['reviewer_id'] or review['reviewer_id'] == review['submitter_id'] or not review['submitter_id']:
        raise SkillError('independent approval required', 'BLOCKED')
    if not utc(review['reviewed_at']) <= now < utc(review['expires_at']):
        raise SkillError('review expired or future', 'BLOCKED')
    if not isinstance(receipt['status'],str) or receipt['status'] not in {'complete','incomplete','unavailable'}:
        raise SkillError('invalid scan status')
    if receipt['status'] != 'complete':
        raise SkillError('mandatory scan '+receipt['status'], 'BLOCKED')
    if not receipt['scanner_id'] or not receipt['runner_id'] or receipt['runner_id'] == review['submitter_id']:
        raise SkillError('independent scan receipt required', 'BLOCKED')
    if not isinstance(receipt['scanner_version'],str) or not receipt['scanner_version'].strip() or not isinstance(receipt['config_sha256'],str) or not SHA.fullmatch(receipt['config_sha256']):
        raise SkillError('scanner version/config identity missing')
    if not isinstance(receipt['check_ids'],list) or 'AGENT-SKILL-PACKAGE-001' not in receipt['check_ids'] or receipt['errors'] != [] or receipt['omissions'] != []:
        raise SkillError('mandatory scanner checks/errors/omissions incomplete', 'BLOCKED')
    if receipt['package_sha256'] != inv['package_sha256'] or receipt['files'] != inv['files'] or receipt['findings_reviewed'] is not True:
        raise SkillError('scan does not cover exact reviewed package')
    # This tool only enforces read-only byte inspection. Textual allowed-tools,
    # temporary use and telemetry cannot grant execution isolation.
    if isolation_profile != 'static-read-only' or entry['isolation_profile'] != isolation_profile:
        raise SkillError('requested operation isolation unavailable', 'BLOCKED')
    return inv, entry

def select(policy_path, expected_policy_sha256, candidate_revision, task, available_tools):
    policy = policy_read(policy_path, expected_policy_sha256, candidate_revision)
    if not isinstance(task,str) or not task:
        raise SkillError('explicit task required')
    result = []
    for entry in policy['entries']:
        if task not in entry['tasks']:
            continue
        missing = sorted(set(entry['required_tools']) - set(available_tools))
        if entry['status'] != 'allowed':
            status, reason = 'BLOCKED', 'admission '+entry['status']
        elif missing:
            status, reason = 'BLOCKED', 'required tools unavailable'
        else:
            status, reason = 'CANDIDATE', 'task/tools match; exact bytes and review still require check'
        result.append({'name':entry['name'], 'purpose':entry['purpose'], 'status':status,
                       'reason':reason, 'missing_tools':missing, 'source_commit':entry['source_commit'],
                       'package_sha256':entry['package_sha256']})
    return {'status':'PASS', 'scope':'description selection only', 'skills':result}

def load_resource(package, path, source_commit, policy_path, expected_policy_sha256, candidate_revision,
                  task=None, available_tools=None):
    inv, entry = authorize(package, source_commit, policy_path, expected_policy_sha256, candidate_revision)
    if not isinstance(task,str) or task not in entry['tasks']:
        raise SkillError('skill not applicable to explicit task', 'BLOCKED')
    if not isinstance(available_tools,list) or any(not isinstance(v,str) for v in available_tools) or set(entry['required_tools']) - set(available_tools):
        raise SkillError('required tools unavailable', 'BLOCKED')
    safe_relative(path)
    if path not in {row['path'] for row in inv['files']}:
        raise SkillError('resource outside admitted inventory')
    data = read_regular(Path(package)/path)
    row = next(row for row in inv['files'] if row['path'] == path)
    if digest(data) != row['sha256']:
        raise SkillError('resource changed during load')
    try:
        content = data.decode('utf-8')
    except UnicodeError as exc:
        raise SkillError('binary resource requires a read-only adapter', 'BLOCKED') from exc
    return {'status':'PASS','path':path,'sha256':row['sha256'],'content':content,
            'untrusted_material':True, 'scope':'one explicitly requested resource; not execution authority'}

OWNER_FILE = '.agent-skills-owner.json'
REGISTRY_FILE = '.agent-skills-registry.json'

def write_json(path, value):
    path = unlinked(path)
    data = canonical(value)+b'\n'
    fd, temp = tempfile.mkstemp(prefix='.agent-write-', dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data)
        os.chmod(temp,0o600)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def owner_state(root, owner, initialize=False):
    root = unlinked(root)
    if not isinstance(owner,str) or not owner.strip():
        raise SkillError('explicit installation owner required')
    if not root.exists():
        if not initialize:
            raise SkillError('installation scope missing')
        root.mkdir(parents=True)
    if not root.is_dir():
        raise SkillError('installation scope must be a directory')
    marker = root/OWNER_FILE
    if not marker.exists():
        if not initialize or any(p.name != '.agent-skills-lock' for p in root.iterdir()):
            raise SkillError('cannot claim existing unowned installation scope')
        write_json(marker,{'schema_version':1,'owner':owner,'scope':str(root.resolve())})
        write_json(root/REGISTRY_FILE,{'schema_version':1,'skills':{}})
    state = strict_json(marker)
    if state != {'schema_version':1,'owner':owner,'scope':str(root.resolve())}:
        raise SkillError('installation owner/scope conflict')
    registry = strict_json(root/REGISTRY_FILE)
    exact(registry,('schema_version','skills'))
    if type(registry['schema_version']) is not int or registry['schema_version'] != 1 or not isinstance(registry['skills'],dict):
        raise SkillError('invalid managed registry')
    for name,record in registry['skills'].items():
        if not isinstance(name,str) or not NAME.fullmatch(name) or len(name) > 64:
            raise SkillError('invalid installed registry name')
        validate_record(record)
    return root, registry

def validate_record(record):
    exact(record,('source_commit','package_sha256','files','history'))
    if not isinstance(record['source_commit'],str) or not COMMIT.fullmatch(record['source_commit']) or not isinstance(record['package_sha256'],str) or not SHA.fullmatch(record['package_sha256']):
        raise SkillError('invalid managed package identity')
    if not isinstance(record['files'],list) or not record['files'] or len(record['files']) > MAX_FILES:
        raise SkillError('invalid installed inventory')
    seen = set()
    for row in record['files']:
        exact(row,('path','size','sha256','mode'))
        safe_relative(row['path'])
        identity = unicodedata.normalize('NFC',row['path']).casefold()
        if identity in seen or type(row['size']) is not int or not 0 <= row['size'] <= MAX_FILE or type(row['mode']) is not int or not 0 <= row['mode'] <= 0o777 or not isinstance(row['sha256'],str) or not SHA.fullmatch(row['sha256']):
            raise SkillError('invalid/colliding inventory record')
        seen.add(identity)
    if not isinstance(record['history'],list):
        raise SkillError('invalid managed history')
    seen = set()
    for row in record['history']:
        exact(row,('source_commit','package_sha256'))
        if not isinstance(row['source_commit'],str) or not COMMIT.fullmatch(row['source_commit']) or not isinstance(row['package_sha256'],str) or not SHA.fullmatch(row['package_sha256']):
            raise SkillError('invalid managed history identity')
        identity = (row['source_commit'],row['package_sha256'])
        if identity in seen:
            raise SkillError('duplicate managed history')
        seen.add(identity)

def check_installed(root, name, record):
    safe_relative(name)
    if '/' in name or not NAME.fullmatch(name):
        raise SkillError('invalid installed package name')
    validate_record(record)
    inv = inventory(root/name)
    if inv['package_sha256'] != record['package_sha256'] or inv['files'] != record['files']:
        raise SkillError('installed files changed/foreign files present; preserving scope')
    return inv

def copy_verified(package, stage, inv):
    stage.mkdir()
    for directory in inv['directories']:
        (stage/directory).mkdir(parents=True,exist_ok=True)
    for row in inv['files']:
        data = read_regular(Path(package)/row['path'])
        if len(data) != row['size'] or digest(data) != row['sha256']:
            raise SkillError('source changed during managed copy')
        path = stage/row['path']
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        path.chmod(row['mode'])
    if inventory(stage)['package_sha256'] != inv['package_sha256']:
        raise SkillError('restored bytes do not match approved package')

def _manage_unlocked(action, root, owner, package=None, name=None, source_commit=None,
           policy_path=None, expected_policy_sha256=None, candidate_revision=None, target_digest=None):
    if action not in {'install','update','rollback','remove'}:
        raise SkillError('unsupported manager operation')
    # Approval before initialization: a rejected install cannot claim the scope.
    if action in {'install','update'}:
        inv, entry = authorize(package,source_commit,policy_path,expected_policy_sha256,candidate_revision,install_root=root)
        name = inv['name']
    root, registry = owner_state(root,owner,initialize=action=='install')
    if not isinstance(name,str) or not NAME.fullmatch(name):
        raise SkillError('invalid package name')
    existing = registry['skills'].get(name)
    if action == 'install':
        if existing or (root/name).exists():
            raise SkillError('skill name/owner conflict')
    else:
        if not existing:
            raise SkillError('package not managed by this owner')
        check_installed(root,name,existing)
    if action == 'remove':
        # No code is executed; foreign/modified files cause failure above.
        with tempfile.TemporaryDirectory(prefix='.agent-remove-',dir=root) as temp:
            backup = Path(temp)/name
            (root/name).rename(backup)
            del registry['skills'][name]
            try:
                write_json(root/REGISTRY_FILE,registry)
            except Exception:
                backup.rename(root/name)
                raise
        return {'status':'PASS','action':action,'name':name,'history_preserved':True}
    if action == 'rollback':
        if not isinstance(target_digest,str) or not SHA.fullmatch(target_digest):
            raise SkillError('explicit rollback digest required')
        matches = [r for r in existing['history'] if r['package_sha256'] == target_digest]
        if len(matches) != 1:
            raise SkillError('rollback version missing/ambiguous')
        target = matches[0]
        package = root/'.history'/name/target_digest/name
        source_commit = target['source_commit']
        inv, entry = authorize(package,source_commit,policy_path,expected_policy_sha256,candidate_revision,install_root=root)
        if inv['package_sha256'] != target_digest:
            raise SkillError('rollback restored bytes mismatch')
    with tempfile.TemporaryDirectory(prefix='.agent-stage-',dir=root) as temp:
        stage = Path(temp)/name
        copy_verified(package,stage,inv)
        history = list(existing['history']) if existing else []
        backup = None
        if existing:
            # Recheck after preparation, before any mutation.
            check_installed(root,name,existing)
            history_root = unlinked(root/'.history'/name/existing['package_sha256'])
            history_root.mkdir(parents=True,exist_ok=True)
            backup = history_root/name
            if backup.exists():
                if inventory(backup)['package_sha256'] != existing['package_sha256']:
                    raise SkillError('history conflict; preserving files')
                # Save this exact current directory separately during transaction.
                backup = Path(temp)/('previous-'+name)
            (root/name).rename(backup)
            previous = {'source_commit':existing['source_commit'],'package_sha256':existing['package_sha256']}
            if previous not in history:
                history.append(previous)
        try:
            stage.rename(root/name)
            registry['skills'][name] = {'source_commit':source_commit,'package_sha256':inv['package_sha256'],
                                       'files':inv['files'],'history':history}
            write_json(root/REGISTRY_FILE,registry)
        except Exception:
            if (root/name).exists():
                shutil.rmtree(root/name)
            if backup and backup.exists():
                backup.rename(root/name)
            raise
    return {'status':'PASS','action':action,'name':name,'package_sha256':inv['package_sha256'],
            'scope':'managed bytes only; no skill/script/hook/MCP execution'}

@contextmanager
def lifecycle_lock(root, initialize=False):
    root = unlinked(root)
    if not root.exists():
        if not initialize:
            raise SkillError('installation scope missing')
        root.mkdir(parents=True,exist_ok=True)
    lock = root/'.agent-skills-lock'
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise SkillError('installation operation already owns scope; explicit stale-lock recovery required','BLOCKED') from exc
    token = str(uuid.uuid4())
    marker = lock/'owner.json'
    try:
        write_json(marker,{'token':token,'pid':os.getpid(),'scope':str(root)})
        yield
    finally:
        if marker.exists() and strict_json(marker).get('token') == token:
            marker.unlink()
            lock.rmdir()

def manage(action, root, owner, package=None, name=None, source_commit=None,
           policy_path=None, expected_policy_sha256=None, candidate_revision=None, target_digest=None):
    if action in {'install','update'}:
        authorize(package,source_commit,policy_path,expected_policy_sha256,candidate_revision,install_root=root)
    with lifecycle_lock(root, initialize=action=='install'):
        return _manage_unlocked(action,root,owner,package,name,source_commit,policy_path,
                                expected_policy_sha256,candidate_revision,target_digest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='operation',required=True)
    for operation in ('inventory','scan'):
        sub = subs.add_parser(operation)
        sub.add_argument('--package',required=True)
    sub = subs.add_parser('import')
    sub.add_argument('--archive',required=True)
    sub.add_argument('--destination',required=True)
    for operation in ('check','select','load','install','update','rollback'):
        sub = subs.add_parser(operation)
        sub.add_argument('--policy',required=True)
        sub.add_argument('--expected-policy-sha256',required=True)
        sub.add_argument('--expected-candidate-revision',required=True)
        if operation != 'select':
            if operation != 'rollback':
                sub.add_argument('--package',required=True)
                sub.add_argument('--source-commit',required=True)
        if operation == 'check':
            sub.add_argument('--isolation-profile',default='static-read-only')
            sub.add_argument('--candidate-root')
        if operation == 'load':
            sub.add_argument('--resource',required=True)
            sub.add_argument('--task',required=True)
            sub.add_argument('--available-tool',action='append',default=[])
        if operation == 'select':
            sub.add_argument('--task',required=True)
            sub.add_argument('--available-tool',action='append',default=[])
        if operation in ('install','update','rollback'):
            sub.add_argument('--install-root',required=True)
            sub.add_argument('--owner',required=True)
        if operation == 'rollback':
            sub.add_argument('--name',required=True)
            sub.add_argument('--target-digest',required=True)
    sub = subs.add_parser('remove')
    sub.add_argument('--install-root',required=True)
    sub.add_argument('--owner',required=True)
    sub.add_argument('--name',required=True)
    args = parser.parse_args(argv)
    try:
        op = args.operation
        if op == 'inventory': result = inventory(args.package)
        elif op == 'scan': result = scan(args.package)
        elif op == 'import': result = import_zip(args.archive,args.destination)
        elif op == 'select': result = select(args.policy,args.expected_policy_sha256,args.expected_candidate_revision,args.task,args.available_tool)
        elif op == 'check':
            inv, entry = authorize(args.package,args.source_commit,args.policy,args.expected_policy_sha256,args.expected_candidate_revision,args.isolation_profile,candidate_root=args.candidate_root)
            result = {'status':'PASS','package_sha256':inv['package_sha256'],'security_certified':False,
                      'scope':'exact-byte admission consistency; independent custody required'}
        elif op == 'load': result = load_resource(args.package,args.resource,args.source_commit,args.policy,args.expected_policy_sha256,args.expected_candidate_revision,args.task,args.available_tool)
        else:
            result = manage(op,args.install_root,args.owner,package=getattr(args,'package',None),
                name=getattr(args,'name',None),source_commit=getattr(args,'source_commit',None),
                policy_path=getattr(args,'policy',None),expected_policy_sha256=getattr(args,'expected_policy_sha256',None),
                candidate_revision=getattr(args,'expected_candidate_revision',None),target_digest=getattr(args,'target_digest',None))
        print(json.dumps(result,ensure_ascii=True,sort_keys=True))
        return 0
    except (SkillError,OSError,TypeError,KeyError) as exc:
        print(json.dumps({'status':getattr(exc,'status','FAIL'),'error':str(exc),'security_certified':False}))
        return 2

if __name__ == '__main__':
    sys.exit(main())
