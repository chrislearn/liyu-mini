#!/usr/bin/env bash
# Login and backend writes require the native host, not card-host.
set -euo pipefail
app_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$app_root/run-octosense-local.sh" "$@"
