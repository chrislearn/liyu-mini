#!/usr/bin/env bash
# Run only the mini client, connected to the production HTTPS backend.
set -euo pipefail

app_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
octo="${OCTO:-$app_root/../OctoScript-App-Design-Flow/tools/octo}"
runtime_dir="$app_root/build/prod-client"

[[ -x "$octo" ]] || {
    echo "找不到标准 OctoScript 启动工具，请通过 OCTO 指定 tools/octo 路径。" >&2
    exit 1
}
command -v python3 >/dev/null || { echo "请先安装 Python 3。" >&2; exit 1; }

# Use a separate editable copy so local-development configuration stays intact.
python3 - "$app_root" "$runtime_dir" <<'PY'
from pathlib import Path
import shutil
import sys
root, runtime = map(Path, sys.argv[1:])
runtime.mkdir(parents=True, exist_ok=True)
bundle = runtime / 'bundle'
if bundle.exists():
    shutil.rmtree(bundle)
shutil.copytree(root / 'bundle', bundle)
PY
python3 "$app_root/scripts/configure-backend.py" https://liyu.taidge.com --bundle "$runtime_dir/bundle"

# Reuse the verified standard runtime if it is present; otherwise use octo discovery.
for entry in 'OCTO_HUB:hub' 'OCTO_CARD_HOST:card-host'; do
    variable="${entry%%:*}"
    binary="$app_root/build/official-runtime/OctoSense-App-Hub/target/debug/${entry#*:}"
    if [[ -z "${!variable:-}" && -x "$binary" ]]; then
        export "$variable=$binary"
    fi
done

"$octo" check "$runtime_dir/bundle"
echo "启动 LIYU-MINI，连接 https://liyu.taidge.com"
exec "$octo" run "$runtime_dir/bundle" \
    --port "${LIYU_MINI_PORT:-8146}" --detach --no-stamp \
    --app-data "$runtime_dir/app-data" "$@"
