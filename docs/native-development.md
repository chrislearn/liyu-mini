# 原生开发运行

真实登录、后端写入和日历必须使用兼容的 OctoSense 宿主。macOS 当前验证版本为官方 desktop-v0.1.0-rc.2；安装到 ~/Applications/OctoSense.app，或用 OCTOSENSE_HOST_BIN 指定可执行文件。小程序真实登录需要后端先部署新版 /oauth/* 与 /api/v1/host/*，本地代码完成不表示线上服务器已升级。

1. 准备最新 App Hub 和其固定版本的依赖，编译 hub；用最新 App Flow 的 octo doctor 检查工具。设置 OCTOSENSE_APP_HUB 与 OCTO_HUB 指向已验证的 checkout 和工具。
2. 执行 `python3 scripts/prepare-native.py --app-data "$PWD/build/native-profile/apps" --configure-launch`。目录必须新建或为空。它复制源码，校验内容，用仅存在于内存的临时测试密钥建立隔离签名目录，并核验安装及启动凭据；不会修改公开 catalog 或建立生产 publisher 身份。
3. 执行 `./run-octosense-local.sh --remote`。宿主打开 App Hub，在 LIYU-MINI 上点 Open。模型需在该隔离宿主配置；拒绝 App Hub 自身 agent 不影响打开小程序。
4. 登录按钮会显示宿主来源与权限页。实际用户继续后，在宿主拥有的网页登录。后端写入、日历授权和日历事件操作都保留原生审阅；远程输入不能证明实际用户批准。

本地后端可配置 `--origin https://liyu.localhost`，必须使用受系统信任的 HTTPS 443 证书。此参数只修改忽略目录中的运行副本，清单里的四个 OAuth 地址、service_origin 和允许列表会一起修改。源发布包仍使用正式域名。

重新安装改动时使用新的隔离目录，避免覆盖已有宿主凭据或业务数据。临时目录和 .local-state/runtime.env 均被 Git 忽略；不要上传宿主数据。生产发布仍走 GitHub 证明和 App Hub 人工审批，此工具不执行发布。

自动检查：check-local-demo.py（内存演示）、check-ai-purchase.py（AI/报价/日期守卫）、check-real-ai-flow.py（AI规划与查询合成控制流）、check-net.py（宿主传输合成适配器）、check-host-calendar.py（日历合成控制流）、check-resilience.py（上海日期、分页和实际文件跨进程恢复）。后端 tests/run_ci.py 使用独立临时数据库。个人日历实际写入、线上登录和真实模型质量必须分别记录，不能由合成检查推定。

## 真实 AI 挑礼

入口：熟人 → 熟人详情 → AI 帮我挑礼。真实账号先读取最新 `/friends` 与 `/catalog/search-options`，展示发送预览。确认后将预算、场景及查询工具说明发送给 `model.complete`；关系和备注仅在预览主动勾选时发送，姓名、联系方式、熟人编号、生日和结婚日期不作为资料字段发送。模型解析硬条件后，由应用执行固定 `/catalog/search` 只读 GET，最多4轮查询、6次模型请求；每轮只发送实际查询商品与当前范围的记录。无精确匹配时单独搜索备选，显示预算、种类、配送及无法核验条件的差异。采纳重新读取商品详情核验价格、库存和规格，再进入待确认草稿。模型/后端错误不会切换演示。数据范围详见[隐私说明](../PRIVACY.md)。

在同一个宿主数据目录中打开 AI providers → Add model；MiniMax 国内与国际账号分别选 MiniMax (China) 或 MiniMax，按宿主表单完成路由、模型、密钥和保存。密钥在宿主 Keychain 中，不应提交给应用或写进本仓库。供应商配置是每个宿主配置目录独立的；其他测试窗口的配置不一定适用于当前实例。

`python3 scripts/check-real-ai-flow.py` 执行生产 Splash 控制流，模型和后端适配器明确为合成测试，覆盖规划、只读查询循环、备选差异、超时与采纳核验，不读取外部捕获文件。这不证明真实外部模型推理。外部推理验收需真实宿主、已保存的供应商、受信 HTTPS 后端和登录账号，并记录人工点击后的推荐结果；已有真实推理记录及限制见[验证文档](verification.md)。
