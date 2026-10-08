# 版本、证据与复现

## 如何对应同一个版本

小程序的 `verification/server-revision.txt` 固定配套服务端提交。CI 从提交后的干净检出校验包内路径、八张演示图片、8 MB 上限、服务域名、能力与 BLAKE3 完整性，不修改清单，也不重新盖章掩盖过期摘要。

CI 生成 ZIP 和 `verification.json`，包含小程序提交 SHA、配套服务端 SHA、应用版本、包 BLAKE3、ZIP SHA256 及工作目录是否有修改。Windows、Linux、macOS 任务都只验证打包；它们通过不代表这些系统上的图形运行或模型功能已验证。ZIP 是未签名的检查材料，不是完成平台审批的发行包。

下载 Actions 的对应提交 artifact，核对 `verification.json` 后计算 ZIP 的 SHA256。包内清单的完整性还应交给标准 `hub check` 验证；数字签名需由发布者按官方流程完成。不要把 `main` 的浮动内容当成固定版本。

## 从干净检出复现

```sh
git clone https://github.com/chrislearn/liyu-mini.git
cd liyu-mini
# 使用 Actions 记录中的 source_revision 替换下列值
git checkout <小程序提交SHA>
python3 -m venv build/verify-venv
build/verify-venv/bin/python -m pip install --require-hashes --only-binary=:all: -r scripts/ci-requirements.txt
build/verify-venv/bin/python scripts/check-bundle.py
```

Windows 的虚拟环境 Python 为 `build/verify-venv/Scripts/python.exe`。获取标准运行器按 [官方 Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)，记录运行器和框架的提交、二进制摘要，确认源码无修改；不要使用未公开的专用 LIYU 宿主补丁。

1. 标准运行器打开 `bundle`，点击「本地演示」。无需后端或模型，检查送出礼盒、必须主动打开、猜错不揭晓、答对后收到礼物、钱包流水与多商品心愿单。自动检查可运行 `python3 scripts/check-local-demo.py`。
2. 检出 `verification/server-revision.txt` 所指服务端，按其部署指南启动 Compose 并信任自己生成的 Caddy CA。配置的后端域名必须与小程序允许列表一致。
3. 使用自己的测试账号在授权网页登录并确认；取消授权不得登录。浏览商品和熟人、送礼、由另一测试账号拆盒，并退出登录验证会话撤销。`python3 scripts/check-net.py` 单独验证实际请求函数的标准 HTTPS 商品读取。
4. 运行服务端 `tests/run_ci.py`：一次性数据库验证授权、心愿单隐私及并发、个人约定状态。此检查不代替两个账号在图形界面的完整交互。

## 当前验证范围

2026-10-08：本机 macOS Apple Silicon 已完成本地演示 23 项检查、标准 HTTPS 商品读取、应用包校验；服务端完成 38 个 Rust 测试、65 项授权、65 项心愿单及 58 项约定接口检查，容器 HTTPS、管理后台、图片与生产测试账号拒绝已通过。

**现有图形截图和运行检查来自作者机器，且其 App Hub 源码有未提交修改。**这些结果不证明官方运行器干净检出或其他平台兼容。现有网页授权测试为 HTTP/API 自动化；完整图形跨账号流程仍应按上面的清单独立复核，不能与 API 结果混算。本仓库未声称双环独立审查通过、苹果公证通过或 Windows/Linux 图形运行通过。

本轮包 CI 与 API CI 提供独立机器的检查记录，但图形运行、平台认证、真实供应商／支付仍各有自己的验证范围。复现后附提交 SHA、运行环境、命令、结果和实际截图，不引用其他项目的测试结果。

校验工具的 Python 包固定版本及 PyPI wheel SHA256，安装使用 `--require-hashes --only-binary`，不构建源码安装包。CI Actions 也固定到提交 SHA。小程序自身不下载或执行 agent 程序，不需要其进程启动权限。
