#!/usr/bin/env bash
set -euo pipefail

app_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
runner="${OCTOSENSE_DEMO_RUNNER:-$app_root/../OctoSense-Demo-Runner}"
mirror="$app_root/build/desktop-mirror"

if [[ ! -x "$runner/target/release/octosense" ]]; then
    echo "OctoSense demo binary missing: $runner/target/release/octosense" >&2
    echo "Build it with: cargo build --release --locked -p octosense --no-default-features --features app-hub" >&2
    exit 1
fi
if [[ ! -f "$mirror/catalog.json" ]]; then
    echo "Local LIYU-DEMO catalog missing: $mirror/catalog.json" >&2
    exit 1
fi

mkdir -p "$app_root/build/desktop-home" "$app_root/build/desktop-apps"
export OCTOSENSE_HUB="$mirror"
export OCTOSENSE_HUB_ANCHOR="ed41b166b1624c5c0fc825f658a17cd513f664dc761ae773b125dfca6824609e"
export OCTOSENSE_HOME="$app_root/build/desktop-home"
export OCTOSENSE_APP_DATA="$app_root/build/desktop-apps"
export MAKEPAD_REMOTE="${MAKEPAD_REMOTE:-8399}"

cd "$runner"
exec "$runner/target/release/octosense"
