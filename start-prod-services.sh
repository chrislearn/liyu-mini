#!/usr/bin/env bash
# Start the production backend behind the operator's existing HTTPS proxy.
set -euo pipefail

app_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
server_root="${LIYU_SERVER_DIR:-$app_root/../liyu-server}"
env_file="${LIYU_PROD_ENV_FILE:-deploy/production.env}"

command -v docker >/dev/null || { echo "请先安装 Docker。" >&2; exit 1; }
docker compose version >/dev/null
[[ -d "$server_root" ]] || { echo "找不到 liyu-server，请通过 LIYU_SERVER_DIR 设置目录。" >&2; exit 1; }
cd -- "$server_root"
[[ -f compose.deploy.yaml ]] || { echo "找不到 compose.deploy.yaml，请更新 liyu-server。" >&2; exit 1; }
[[ -f "$env_file" ]] || {
    echo "请先复制 deploy/production.env.example 为 deploy/production.env，并填写密码及发送服务配置。" >&2
    echo "使用其他配置文件时，请设置 LIYU_PROD_ENV_FILE。" >&2
    exit 1
}

compose=(docker compose --env-file "$env_file" -f compose.deploy.yaml)
"${compose[@]}" config --quiet
"${compose[@]}" pull
"${compose[@]}" up -d --wait --wait-timeout 120
"${compose[@]}" ps

echo "生产后端已启动，容器健康检查通过。"
echo "默认由你现有的宿主机 Caddy 将 liyu.taidge.com 反代到 127.0.0.1:8787。"
echo "公网 HTTPS 和登录流程仍需单独核验。"
