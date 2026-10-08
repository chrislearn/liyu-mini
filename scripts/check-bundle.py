#!/usr/bin/env python3
"""Portable package checks and deterministic review artifact; not a runtime gate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
from blake3 import blake3

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path('build/review'))
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
bundle = root / 'bundle'
paths = sorted(bundle.rglob('*'))
assert not any(p.is_symlink() for p in paths), 'Bundle contains symlinks'
files = [p for p in paths if p.is_file()]
size = sum(p.stat().st_size for p in files)
assert size < 8_000_000, f'Bundle too large: {size}'
allowed = {'.card', '.json', '.l0', '.octoscript', '.splash', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ttf', '.otf', '.txt', '.md'}
assert all(p.suffix.lower() in allowed for p in files), 'Unexpected package content'
manifest = json.loads((bundle / 'manifest.json').read_text())
listing = json.loads((bundle / 'listing.json').read_text())
source = (bundle / 'main.splash').read_text()
assert manifest['capabilities'] == ['images', 'model', 'net', 'storage']
assert 'host.request("liyu.' not in source and 'services.liyu' not in source
origin = json.loads(re.search(r'^let service_origin = ("[^"]+")$', source, re.M)[1])
from urllib.parse import urlsplit
assert urlsplit(origin).scheme == 'https'
assert manifest['network']['hosts'] == [urlsplit(origin).hostname]
assert 'net.http_request' in source and '本地演示' in source
assert not re.search(r'is_password\s*:\s*true|TextInputContentType\.(Password|NewPassword|OneTimeCode)', source)
for name in [listing['icon'], *listing['screenshots']]:
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts and (bundle / path).is_file(), name
seed = json.loads(json.loads(source.split('fn demo_seed(){ return ', 1)[1].split('.parse_json()', 1)[0].strip()))
assert len(seed['products']) == 8
for product in seed['products']:
    assert (bundle / product['demo_image'].lstrip('/')).is_file()
assert len(list((bundle / 'assets').glob('p[0-9][0-9].png'))) == 8
# Matches app-policy/src/bundle.rs: sorted path, NUL, u64 LE length, bytes.
hash_state = blake3()
for path in files:
    relative = path.relative_to(bundle).as_posix()
    if relative == 'manifest.json':
        continue
    data = path.read_bytes()
    hash_state.update(relative.encode() + b'\0' + len(data).to_bytes(8, 'little') + data)
digest = hash_state.hexdigest()
assert digest == manifest['integrity']['bundle_blake3'], 'Stale bundle integrity; run octo check'
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
archive = output / f"liyu-mini-{manifest['version']}.zip"
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in files:
        info = zipfile.ZipInfo(path.relative_to(bundle).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, path.read_bytes())
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
report = {'app_version': manifest['version'], 'source_revision': revision, 'working_tree_dirty': dirty,
          'bundle_blake3': digest, 'bundle_bytes': size, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'server_revision': (root / 'verification/server-revision.txt').read_text().strip(),
          'scope': 'portable package validation; no GUI, real login, signature or platform certification claim'}
(output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
