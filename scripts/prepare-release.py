import hashlib
import json
import os
import shutil
from pathlib import Path

packages = sorted(Path('build/artifacts').glob('*/liyu-mini-*.zip'))
assert len(packages) == 3, 'Expected all three platform packages'
checksums = [hashlib.sha256(p.read_bytes()).hexdigest() for p in packages]
assert len(set(checksums)) == 1, 'Platform packages differ'
for package in packages:
    report = json.loads((package.parent / 'verification.json').read_text(encoding='utf-8'))
    assert report['archive_sha256'] == checksums[0], 'Invalid verification report'
    assert not report['working_tree_dirty'], 'Release must use a clean checkout'
    assert report['source_revision'] == os.environ['GITHUB_SHA'], 'Wrong source revision'
    assert 'v' + report['app_version'] == os.environ['GITHUB_REF_NAME'], 'Wrong release version'
output = Path('build/release')
output.mkdir(parents=True, exist_ok=True)
shutil.copy2(packages[0], output / packages[0].name)
shutil.copy2(packages[0].parent / 'verification.json', output / 'verification.json')
(output / 'SHA256SUMS').write_text(f'{checksums[0]}  {packages[0].name}\n', encoding='utf-8')
Path('build/release-notes.md').write_text(
    '下载 liyu-mini 版本 ZIP 即可获得小程序包；verification.json 和 SHA256SUMS 用于核对来源和摘要。\n\n'
    '三个平台的 CI 已验证包内容一致。运行需要标准 OctoScript 环境，本地演示无需服务器；真实账号需要配置 liyu-server 与 HTTPS。\n\n'
    '这是未经 App Hub 发布者签名的小程序包，不代表已通过 App Hub 审核。\n', encoding='utf-8')
