#!/usr/bin/env bash
# Run the real local LIYU backend and its HTTPS proxy together.
set -euo pipefail

app_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_root="${LIYU_SERVER_DIR:-$app_root/../liyu-server}"
runtime_dir="$app_root/build/local-services"
export LIYU_BIND=127.0.0.1:8787
export LIYU_CADDY_DATA="$app_root/build/local-caddy/data"
backend_pid=""
proxy_pid=""

cleanup() {
    trap - EXIT INT TERM
    for pid in "$proxy_pid" "$backend_pid"; do
        if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi
    done
    for pid in "$proxy_pid" "$backend_pid"; do
        if [[ -n "$pid" ]]; then wait "$pid" 2>/dev/null || true; fi
    done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

for tool in cargo caddy curl python3; do
    command -v "$tool" >/dev/null || { echo "Missing command: $tool" >&2; exit 1; }
done
[[ -f "$server_root/.env" ]] || { echo "Configure $server_root/.env first." >&2; exit 1; }
# Reuse a healthy backend; refuse other occupied ports.
backend_ready=false
if curl --silent --fail --max-time 2 http://127.0.0.1:8787/health >/dev/null; then
    backend_ready=true
    echo "Using the existing backend on 127.0.0.1:8787."
fi
ca_file="$LIYU_CADDY_DATA/pki/authorities/local/root.crt"
if [[ "$backend_ready" == true ]] && curl --silent --fail --max-time 2 --cacert "$ca_file" https://liyu.localhost:8443/health >/dev/null; then
    echo "Backend and HTTPS proxy are already ready: https://liyu.localhost:8443"
    exit 0
fi
export LIYU_BACKEND_READY="$backend_ready"
python3 - <<'PY'
import os, socket
ports = (8443,) if os.environ['LIYU_BACKEND_READY'] == 'true' else (8787, 8443)
for port in ports:
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            raise SystemExit(f'Port {port} is occupied. Stop its existing service first.')
PY

mkdir -p "$runtime_dir" "$LIYU_CADDY_DATA"
cat > "$runtime_dir/Caddyfile" <<'CADDY'
{
    admin off
    auto_https disable_redirects
    skip_install_trust
    storage file_system {$LIYU_CADDY_DATA}
}
https://liyu.local:8443, https://liyu.localhost:8443 {
    bind 127.0.0.1
    tls internal
    reverse_proxy 127.0.0.1:8787
}
CADDY
caddy validate --config "$runtime_dir/Caddyfile" --adapter caddyfile > "$runtime_dir/caddy-validate.log" 2>&1 || {
    echo "Caddy configuration failed. See $runtime_dir/caddy-validate.log" >&2; exit 1;
}
if [[ "$backend_ready" != true ]]; then
    (cd "$server_root" && cargo build --bin liyu-server)
    (cd "$server_root" && exec target/debug/liyu-server) > "$runtime_dir/backend.log" 2>&1 &
    backend_pid=$!
fi

wait_ready() {
    local url="$1" pid="$2" log="$3"
    shift 3
    for ((attempt=0; attempt<100; attempt++)); do
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "Service exited before startup completed. See $log" >&2; return 1
        fi
        if curl --silent --fail --max-time 1 "$@" "$url" >/dev/null; then return 0; fi
        sleep 0.2
    done
    echo "Service startup timed out. See $log" >&2; return 1
}
if [[ -n "$backend_pid" ]]; then
    wait_ready http://127.0.0.1:8787/health "$backend_pid" "$runtime_dir/backend.log"
fi
caddy run --config "$runtime_dir/Caddyfile" --adapter caddyfile > "$runtime_dir/caddy.log" 2>&1 &
proxy_pid=$!
wait_ready https://liyu.localhost:8443/health "$proxy_pid" "$runtime_dir/caddy.log" --cacert "$ca_file"

echo "LIYU backend: http://127.0.0.1:8787"
echo "HTTPS proxy:  https://liyu.localhost:8443"
echo "Admin:        https://liyu.localhost:8443/admin"
echo "Logs:         $runtime_dir"
echo "Host CA:      $ca_file"
echo "Ready. Keep this terminal open; Ctrl+C stops services started by this command."
while kill -0 "$proxy_pid" 2>/dev/null; do
    if [[ -n "$backend_pid" ]] && ! kill -0 "$backend_pid" 2>/dev/null; then break; fi
    sleep 1
done
echo "A service stopped. See logs in $runtime_dir" >&2
exit 1
