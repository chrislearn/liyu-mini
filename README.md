# LIYU-MINI

LIYU-MINI 是 [LIYU](https://github.com/chrislearn/OctoSense/tree/liyu/apps/liyu) 的 OctoScript / Splash 版本，用于与 `liyu-server` 进行本地联调。商品、分类、价格、库存、账号、熟人、心愿单和礼盒记录均通过宿主的 `liyu` 服务读取。应用使用真实用户登录及服务端会话。

## 主要功能

- **挑礼与送礼**：浏览商品目录和详情，选择商品后点击「送给TA」设置礼盒。支持添加、移除收礼人，一次最多选择 100 位熟人，合并报价并生成测试订单，每位收礼人对应一个礼盒。
- **主动拆盒**：收到礼盒后可以查看商品信息，送礼人身份在拆盒前隐藏。送礼人可选择直接打开、猜送礼人或回答问题；每个礼盒都必须主动打开，谜题答错不能拆盒。
- **心愿单**：新建心愿单后逐件加入商品，最多 8 项，也可填写商品种类、预算等需求。发布前仅自己可见，发布时设置可见范围和有效期；发布后商品清单固定。重复加入同一商品不会增加重复项。
- **熟人资料与提醒**：保存仅自己可见的昵称、联系方式、关系、生日、结婚日期和备注。生日及结婚纪念日在提前七天和当天产生站内提醒。
- **AI 建议**：通过设备配置的模型分析适合赠送的商品，或根据可见线索推测送礼人。AI 无法读取真正答案，也不能替用户拆盒或下单；宿主未提供模型服务时会提示不可用。
- **约定记录**：双方分别记录待兑现、已兑现状态。点击「附带的约定」进入状态页面，修改只影响当前账号的记录。旧版共享状态保留为历史数据。
- **账号与地址**：支持修改显示名、验证邮箱或手机号，保存多个收货地址，设置默认地址，以及编辑和删除地址。「我」页面底部提供切换账号和退出登录。
- **外观与布局**：支持深色、浅色主题并保存偏好。手机布局使用底部导航、双栏商品卡片；桌面布局包含左侧导航、中间内容区和右侧信息栏。具体对应关系见[界面实现说明](UI-PARITY.md)。

## 登录与数据

密码和验证码在 **OctoSense 宿主提供的弹层**中输入。宿主将会话令牌保存在 `<app-data>/.host/liyu/liyu-mini/session.json`，限制为当前用户访问，并代理带认证的业务请求；应用不会收到密码、验证码或令牌。重启后恢复会话，退出登录或收到 HTTP 401 后返回登录入口。Caddy 不注入共享账号。

邮箱和手机号修改由宿主的 `liyu.edit_contact` 方法完成验证，真实邮件、短信发送需要后端配置发送服务。新联系方式验证后用于资料展示；原有已验证身份和登录标识按服务端规则保留。熟人备注与资料属于当前账号，不会修改对方已验证的身份信息。

商品图片通过 `https://liyu.localhost:8443` 加载。此版本使用本地测试后端，测试支付不产生真实扣款；测试数据保存在服务端数据库中。应用没有内置虚构熟人或本地业务数据兜底。中文关键词输入可使用服务端返回的商品和熟人生成待确认内容，目前该页面由 Splash 实现。

本地 App-Hub 已实现 `liyu` 能力。公开上架还需要提供正式 HTTPS 服务地址，并确认目标宿主支持所需能力。详情见[能力差异说明](CAPABILITY-GAP.md)和[隐私政策](PRIVACY.md)。

## 演示视频

[观看 LIYU-MINI 操作演示](liyu-demo.mp4)（MP4，约 3 分钟，32 MB）。

## 界面截图

以下为连接本地 LIYU 后端的真实页面截图，包含浅色、深色及桌面布局。

### 桌面布局

![桌面布局：左侧导航、中央内容与右侧信息栏](screenshots/desktop.png)

### 主要功能

| 挑选商品 | 商品详情 |
| --- | --- |
| <img src="screenshots/catalog.png" alt="挑礼：商品分类、图片和价格" width="300"> | <img src="screenshots/product.png" alt="商品详情：介绍、规格以及送礼和加入心愿单入口" width="300"> |

| 心愿单 | 送出的礼盒 |
| --- | --- |
| <img src="screenshots/wishlists.png" alt="我的心愿单：商品清单、发布状态和有效期" width="300"> | <img src="screenshots/gift-box.png" alt="礼盒详情：商品、收礼人、礼盒信息及解谜进度" width="300"> |

| 熟人 | 心愿单可见范围 |
| --- | --- |
| <img src="screenshots/contacts.png" alt="熟人列表：搜索、关系和标签入口" width="300"> | <img src="screenshots/wishlist-audience.png" alt="心愿单可见范围：按熟人或标签选择" width="300"> |

## 本地运行

一键启动本地后端和 Caddy HTTPS 反代：

```sh
./start-local-services.sh
```

可从任意目录用脚本绝对路径运行。后端固定监听 `127.0.0.1:8787`，反代为 `https://liyu.localhost:8443`，管理页面为 `/admin`。首次启动前需配置 `../liyu-server/.env` 并确保其中的 PostgreSQL 数据库可用；命令会增量编译后端，使用现有账号与数据库配置，不启用演示登录或额外开启测试验证码。已有健康的后端会复用；两项服务都就绪时重复执行直接返回。保持终端打开，`Ctrl+C` 只停止本次命令启动的进程。日志在 `build/local-services/`，CA 沿用 `build/local-caddy/data/pki/authorities/local/root.crt`。管理界面需预先在后端执行 `just build-admin`。

如需分别启动后端与反代，可在一键脚本生成配置后执行以下命令。后端读取现有 `.env`；注册测试可显式设置 `LIYU_TEST_DELIVERY=true` 返回测试验证码，正常验证需要配置发送服务。宿主通过 `LIYU_SERVICE_CA_FILE` 使用本地 CA 校验证书。

```sh
cd ../liyu-server && LIYU_BIND=127.0.0.1:8787 target/debug/liyu-server
# 在另一个终端中进入 liyu-mini 后执行：
LIYU_CADDY_DATA="$PWD/build/local-caddy/data" caddy run --config build/local-services/Caddyfile --adapter caddyfile
```

随后使用包含 `liyu` 服务的本地 App-Hub 工具启动应用：

```sh
OCTO_HUB=../OctoSense-App-Hub/target/debug/hub \
../OctoScript-App-Design-Flow/tools/octo check bundle
LIYU_SERVICE_URL=https://liyu.localhost:8443 \
LIYU_SERVICE_CA_FILE="$PWD/build/local-caddy/data/pki/authorities/local/root.crt" \
OCTO_CARD_HOST=../OctoSense-App-Hub/target/debug/card-host \
../OctoScript-App-Design-Flow/tools/octo run bundle --port 8141 --detach --app-data build/auth-app-data
```


打开 `card-host` 窗口，选择「登录或注册」。也可通过 `127.0.0.1:8141` 的 `/snap`、`/click` 和 `/g` 接口查看和操作应用。使用期间保持 Caddy 和后端运行。

如需在 OctoSense 中打开本地安装的应用，使用包含 `liyu` 服务的宿主程序，并执行：

```sh
./run-octosense-local.sh
```

该脚本使用 `build/` 下的本地签名目录和已安装应用，配置 HTTPS 服务及本地 CA，启动时打开 `hub:liyu-mini`。宿主远程操作端口默认为 `127.0.0.1:8399`。模型功能还需在宿主中完成模型配置。

## 文件说明

- `liyu-demo.mp4`：操作演示视频。
- `screenshots/`：README 展示的真实页面截图。
- `bundle/`：提交给 App Hub 的应用包。
- `build/`：本地构建、日志、证书及运行数据，已被 Git 忽略，不提交到仓库。

## 产品名词

- 商品：商品目录中可挑选、加入心愿单的内容。心愿单中的未指定商品条目标为「商品需求」。
- 礼盒：用户选好商品后送出的对象；包含商品、拆盒方式、寄语及可选约定。未拆开也展示商品信息，送礼人身份由服务端隐藏。
- 礼物：收礼人拆开礼盒后收到的、由另一位用户送来的商品。

送出记录统一使用「礼盒」；收到记录同时包含未拆和已拆的礼盒。收礼详情按状态显示「礼盒详情」或「礼物详情」，解谜中仍属于未拆开的礼盒。商品名称、用户自填标题及历史寄语保持原文。

送礼入口直接进入「挑礼」商品目录，选中商品并点击「送给TA」后才进入「设置礼盒」。设置中的「换一件」也使用同一商品目录；重新选商品或取消更换时保留收礼人、寄语和拆盒设置。
