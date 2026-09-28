#!/usr/bin/env bash
set -euo pipefail

app_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
runner="${OCTOSENSE_DEMO_RUNNER:-$app_root/../OctoSense-Demo-Runner}"
mirror="$app_root/build/desktop-mirror"

if [[ ! -x "$runner/target/release/octosense" ]]; then
    echo "OctoSense demo binary missing: $runner/target/release/octosense" >&2
    echo "Build it with: cargo build --release --locked -p octosense --no-default-features --features app-hub,app-appcard" >&2
    exit 1
fi
if [[ ! -f "$mirror/catalog.json" ]]; then
    echo "Local LIYU-DEMO catalog missing: $mirror/catalog.json" >&2
    exit 1
fi
if [[ -z "${OCTOS_APP_CORE_BIN:-}" ]]; then
    OCTOS_APP_CORE_BIN="$(command -v octos || true)"
fi
if [[ -z "$OCTOS_APP_CORE_BIN" || ! -x "$OCTOS_APP_CORE_BIN" ]]; then
    echo "AppCard needs an octos kernel binary; set OCTOS_APP_CORE_BIN to its path." >&2
    exit 1
fi

export OCTOS_APP_CORE_DIR="${OCTOS_APP_CORE_DIR:-$app_root/build/octos-core/.octos}"
mkdir -p "$app_root/build/desktop-home" "$app_root/build/desktop-apps" "$OCTOS_APP_CORE_DIR"
if [[ ! -f "$OCTOS_APP_CORE_DIR/profiles/_main.json" ]]; then
    echo "AppCard has no _main model profile in $OCTOS_APP_CORE_DIR; configure a model in AI providers before generating a card." >&2
fi
export OCTOSENSE_HUB="$mirror"
export OCTOSENSE_HUB_ANCHOR="ed41b166b1624c5c0fc825f658a17cd513f664dc761ae773b125dfca6824609e"
export OCTOSENSE_HOME="$app_root/build/desktop-home"
export OCTOSENSE_APP_DATA="$app_root/build/desktop-apps"
export OCTOS_APP_CORE_BIN
export OCTOSENSE_LLM_VAULT=file
export OCTOSENSE_MAIL_VAULT=file
export MAKEPAD_REMOTE="${MAKEPAD_REMOTE:-8399}"

cd "$runner"
exec "$runner/target/release/octosense" --module appcard
