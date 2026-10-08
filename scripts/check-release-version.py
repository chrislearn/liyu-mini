import json
import os
import re
from pathlib import Path

version = json.loads(Path('bundle/manifest.json').read_text(encoding='utf-8'))['version']
tag = os.environ['GITHUB_REF_NAME']
assert re.fullmatch(r'v\d+\.\d+\.\d+', tag), 'Release tag must be vMAJOR.MINOR.PATCH'
assert tag == 'v' + version, f'Tag {tag} does not match manifest version {version}'
