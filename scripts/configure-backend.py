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
url = urlsplit(args.origin)
try:
    port = url.port
except ValueError:
    parser.error('端口无效')
if (url.scheme != 'https' or not url.hostname or url.username or url.password
        or url.path not in ('', '/') or url.query or url.fragment
        or not re.fullmatch(r'[a-zA-Z0-9.-]+', url.hostname)
        or (port is not None and not 1 <= port <= 65535)):
    parser.error('必须提供不含账号、路径、查询或片段的 HTTPS 域名地址')
origin = 'https://' + url.hostname.lower() + (f':{port}' if port else '')
source_path = args.bundle / 'main.splash'
manifest_path = args.bundle / 'manifest.json'
source = source_path.read_text()
updated, count = re.subn(r'^let service_origin = "[^"]*"$',
                         'let service_origin = ' + json.dumps(origin), source, flags=re.M)
if count != 1:
    parser.error('服务地址声明缺失或重复，未修改文件')
manifest = json.loads(manifest_path.read_text())
manifest['network']['hosts'] = [url.hostname.lower()]
# Existing integrity is no longer valid after editing the source.
manifest.pop('integrity', None)
source_path.write_text(updated)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(f'已设置后端 {origin}。请运行 tools/octo check bundle 重新校验与生成完整性信息，再打包发布。')
