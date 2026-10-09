#!/usr/bin/env python3
"""Configure the HTTPS origin and the matching standard network allowlist."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

parser = argparse.ArgumentParser(description='设置礼遇 HTTPS 后端；随后需运行 octo check 重新校验。')
parser.add_argument('origin', help='例如 https://liyu.example.com')
parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parents[1] / 'bundle')
args = parser.parse_args()
try:
    url = urlsplit(args.origin)
    port = url.port
except ValueError:
    parser.error('地址或端口无效')
if (url.scheme != 'https' or not url.hostname or url.username or url.password
        or url.path not in ('', '/') or url.query or url.fragment
        or len(url.hostname) > 253
        or any(not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', label)
               for label in url.hostname.split('.'))
        or url.netloc.endswith(':')
        or (port is not None and port != 443)):
    parser.error('必须提供不含账号、路径、查询或片段的 HTTPS 域名地址')
origin = 'https://' + url.hostname.lower() + (f':{port}' if port else '')
source_path = args.bundle / 'main.splash'
manifest_path = args.bundle / 'manifest.json'
source = source_path.read_text(encoding='utf-8')
updated, count = re.subn(r'^let service_origin = "[^"]*"$',
                         'let service_origin = ' + json.dumps(origin), source, flags=re.M)
if count != 1:
    parser.error('服务地址声明缺失或重复，未修改文件')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['network']['hosts'] = [url.hostname.lower()]
for field, endpoint in [('authorization_url','authorize'),('token_url','token'),('me_url','me'),('logout_url','logout')]:
    manifest['backend'][field] = origin + '/oauth/' + endpoint
# Existing integrity is no longer valid after editing the source.
manifest.pop('integrity', None)
source_path.write_text(updated, encoding='utf-8')
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'已设置后端 {origin}。请运行 tools/octo check bundle 重新校验与生成完整性信息，再打包发布。')
