#!/usr/bin/env bash
set -euo pipefail
app_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${OCTOSENSE_APP_DATA:-}" && -f "$app_root/.local-state/runtime.env" ]]; then source "$app_root/.local-state/runtime.env"; fi
host="${OCTOSENSE_HOST_BIN:-$HOME/Applications/OctoSense.app/Contents/MacOS/octosense}"
if [[ ! -x "$host" ]]; then host="/Applications/OctoSense.app/Contents/MacOS/octosense"; fi
[[ -x "$host" ]] || { echo "Install a compatible OctoSense desktop RC2 host, or set OCTOSENSE_HOST_BIN." >&2; exit 1; }
export OCTOSENSE_APP_DATA="${OCTOSENSE_APP_DATA:-$app_root/build/desktop-apps}"
export OCTOSENSE_HOME="${OCTOSENSE_HOME:-$app_root/build/desktop-home}"
[[ -f "$OCTOSENSE_APP_DATA/catalog.json" ]] || { echo "Install the checked bundle in an isolated native profile first; see docs/native-development.md." >&2; exit 1; }
# This explicit developer catalog has ephemeral test keys, never production authority.
export OCTOSENSE_HUB="${OCTOSENSE_HUB:-$OCTOSENSE_APP_DATA}"
export OCTOSENSE_HUB_CATALOG=legacy
if [[ -z "${OCTOSENSE_HUB_ANCHOR:-}" ]]; then
    export OCTOSENSE_HUB_ANCHOR="$(python3 -c 'import json,os; print(json.load(open(os.path.join(os.environ["OCTOSENSE_APP_DATA"],".connected-e2e.json")))["anchor"])')"
fi
export MAKEPAD_WM_TEST_APP=apphub
cd "$(dirname "$host")"
exec "$host" "$@"
