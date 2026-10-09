# 原生开发运行

真实登录、后端写入和日历必须使用兼容的 OctoSense 宿主。macOS 当前验证版本为官方 desktop-v0.1.0-rc.2；安装到 ~/Applications/OctoSense.app，或用 OCTOSENSE_HOST_BIN 指定可执行文件。小程序真实登录需要后端先部署新版 /oauth/* 与 /api/v1/host/*，本地代码完成不表示线上服务器已升级。

1. 准备最新 App Hub 和其固定版本的依赖，编译 hub；用最新 App Flow 的 octo doctor 检查工具。设置 OCTOSENSE_APP_HUB 与 OCTO_HUB 指向已验证的 checkout 和工具。
2. 执行 `python3 scripts/prepare-native.py --app-data "$PWD/build/native-profile/apps" --configure-launch`。目录必须新建或为空。它复制源码，校验内容，用仅存在于内存的临时测试密钥建立隔离签名目录，并核验安装及启动凭据；不会修改公开 catalog 或建立生产 publisher 身份。
3. 执行 `./run-octosense-local.sh --remote`。宿主打开 App Hub，在 LIYU-MINI 上点 Open。模型需在该隔离宿主配置；拒绝 App Hub 自身 agent 不影响打开小程序。
4. 登录按钮会显示宿主来源与权限页。实际用户继续后，在宿主拥有的网页登录。后端写入、日历授权和日历事件操作都保留原生审阅；远程输入不能证明实际用户批准。

本地后端可配置 `--origin https://liyu.localhost`，必须使用受系统信任的 HTTPS 443 证书。此参数只修改忽略目录中的运行副本，清单里的四个 OAuth 地址、service_origin 和允许列表会一起修改。源发布包仍使用正式域名。

重新安装改动时使用新的隔离目录，避免覆盖已有宿主凭据或业务数据。临时目录和 .local-state/runtime.env 均被 Git 忽略；不要上传宿主数据。生产发布仍走 GitHub 证明和 App Hub 人工审批，此工具不执行发布。

自动检查：check-local-demo.py（内存演示）、check-ai-purchase.py（AI/报价/日期守卫）、check-net.py（宿主传输合成适配器）、check-host-calendar.py（日历合成控制流）。后端 tests/run_ci.py 使用独立临时数据库。个人日历实际写入、线上登录和真实模型质量必须分别记录，不能由合成检查推定。

## 真实 AI 挑礼

入口：熟人 → 熟人详情 → AI 帮我挑礼。真实账号点击时，通过宿主 auth.backend.request 重新读取 `/friends` 与 `/catalog?limit=50`；两次读取成功后，将所选熟人的内部编号、关系、生日、结婚纪念日、备注及预算、场景、最多 50 件有库存商品的编号/名称/类型/价格交给 `model.complete`。宿主负责供应商、模型和密钥；应用仅接收 `output.recommendations`，校验目录成员、预算和重复项，再允许人工采纳。没有自动下单。模型/后端错误不会切换演示。

在同一个宿主数据目录中打开 AI providers → Add model；MiniMax 国内与国际账号分别选 MiniMax (China) 或 MiniMax，按宿主表单完成路由、模型、密钥和保存。密钥在宿主 Keychain 中，不应提交给应用或写进本仓库。供应商配置是每个宿主配置目录独立的；其他测试窗口的配置不一定适用于当前实例。

`python3 scripts/check-real-ai-flow.py` 执行生产 Splash 控制流，模型适配器明确为合成测试。可用 `LIYU_AI_SERVER_CAPTURE=/absolute/server-data.json` 提供通过真实服务端 PKCE 接口读回的 `{friends:{status:200,body:[...]},catalog:{status:200,body:{items:[...]}}}`。这验证真实数据形状和传递，不证明真实外部模型推理。外部推理验收需真实宿主、已保存的供应商、受信 HTTPS 后端和登录账号，并记录人工点击后的推荐结果。
