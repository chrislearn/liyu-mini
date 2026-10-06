# LIYU-MINI

LIYU-MINI is the OctoScript/Splash version of [LIYU](https://github.com/chrislearn/OctoSense/tree/liyu/apps/liyu). This checkout is configured for **local integration testing** with `liyu-server`; the running app has no bundled catalog, fictional contacts, or local gift/wishlist records. It requests products, categories, prices, stock, the signed-in account, friends, wishlists, and gifts through the host's `liyu` service. Friend detail now includes owner-private nickname, phone, email, relationship, birthday, and note fields. Each field opens a separate editor and saves through the host service; recent wishes and sent/received gift lists link to the existing detail flows. Product images use `https://liyu.localhost:8443`. An optional short Chinese keyword parser opens a review screen using the returned products and friends. An exact or broad wishlist is written to the server after confirmation. Gift checkout uses “+ TA” to add friends, permits removing each selected friend, and obtains a combined server quote for up to 100 recipients. One test order creates one gift per recipient after explicit confirmation and `pay-test`; puzzle settings and gift state changes also use the server API.

The 412-point phone shell follows the Makepad LIYU element tree: 58-point top bar, 66-point icon navigation, segmented tabs, category chips, two-column product cards, compact gift/contact rows, and the four-section wishlist and gift forms. See [UI-PARITY.md](UI-PARITY.md) for the source-to-Splash mapping and remaining differences. `liyu-server` is still a **test** backend with seeded products, optional local social/gift fixtures, test payment, and test delivery; these are persisted server records, not LIYU-MINI fallback data. LIYU-MINI does not sign in with a seeded account. If that backend has no iPhone product, LIYU-MINI does not invent one. The in-app command screen is a Splash view, not a system AppCard integration. A top-bar layout switch enables a desktop mode with LIYU-style 208-point left navigation, a flexible central content column, and a 300-point right information column. The phone layout retains its bottom navigation; the desktop mode is manually selected and is intended for wide viewports.

LIYU-MINI now has the same account gate as native LIYU: sign in or register with an email/phone identifier, password, and registration code; restore the server session on restart; return to the gate on logout or HTTP 401. The password and code are typed into an **OctoSense-owned sheet**, not the contained app. The host keeps the Bearer token in `<app-data>/.host/liyu/liyu-mini/session.json` with owner-only file permissions and proxies authenticated business requests. Caddy no longer injects a shared account. The `liyu` capability and service are currently implemented in the **local App-Hub checkout**; its pinned version in the OctoSense shell and the public App Hub do not yet include this change. A public release also needs a public HTTPS LIYU origin and host rollout. See [CAPABILITY-GAP.md](CAPABILITY-GAP.md) and [PRIVACY.md](PRIVACY.md).

The gift flow now requires an explicit open action on every received gift. The sender chooses direct opening, a sender-name guess, or a custom question. The server keeps all new paid gifts locked until that choice is saved; wrong answers never reveal a puzzle gift. Friend birthdays and wedding dates generate private in-app reminders seven days before and on the day. Two optional `model.complete` buttons ask the device's configured AI for gift suggestions or possible senders from visible clues; they cannot read the server's answer, open a gift, or order. Current OctoSense `main` has the model service, while this repository's older local Demo Runner and `card-host` do not; those hosts show a clear unavailable state until updated. The App-Hub LIYU proxy in this workspace now allows the reminder read route.

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

## Run locally

一键启动本地后端和 Caddy HTTPS 反代：

```sh
./start-local-services.sh
```

可从任意目录用脚本绝对路径运行。后端固定监听 `127.0.0.1:8787`，反代为 `https://liyu.localhost:8443`，管理页面为 `/admin`。首次启动前需配置 `../liyu-server/.env` 并确保其中的 PostgreSQL 数据库可用；命令会增量编译后端，使用现有账号与数据库配置，不启用演示登录或额外开启测试验证码。已有健康的后端会复用；两项服务都就绪时重复执行直接返回。保持终端打开，`Ctrl+C` 只停止本次命令启动的进程。日志在 `build/local-services/`，CA 沿用 `build/local-caddy/data/pki/authorities/local/root.crt`。管理界面需预先在后端执行 `just build-admin`。

Personal profile rows open a display-name editor or an OctoSense-owned email/phone verification sheet. The `liyu.edit_contact` host method requests a bearer-scoped binding challenge and returns the updated profile after verification; the app never receives the code. The new verified contact becomes the displayed contact, while prior verified identities and the login identifier are retained by the existing server API. Real email/SMS changes require the server's delivery webhook. Shipping addresses support multiple saved entries, a default selection, editing, and confirmed deletion through owner-scoped server routes.

For manual startup, run `liyu-server` on `127.0.0.1:8787` with the local database. For a local registration test, `LIYU_TEST_DELIVERY=true` returns a test verification code; normal deployments need a configured delivery webhook. Caddy proxies the same server at `https://liyu.localhost:8443` without attaching Authorization. The host service uses that HTTPS address too; `LIYU_SERVICE_CA_FILE` supplies its local CA to Rust's TLS verifier. After the one-command script has generated its configuration, these long-lived commands can also be run in separate terminals:

```sh
cd ../liyu-server && LIYU_BIND=127.0.0.1:8787 target/debug/liyu-server
# From liyu-mini, in another terminal:
LIYU_CADDY_DATA="$PWD/build/local-caddy/data" caddy run --config build/local-services/Caddyfile --adapter caddyfile
```

Then use the locally built App-Hub tools containing the `liyu` service:

```sh
OCTO_HUB=../OctoSense-App-Hub/target/debug/hub \
../OctoScript-App-Design-Flow/tools/octo check bundle
LIYU_SERVICE_URL=https://liyu.localhost:8443 \
LIYU_SERVICE_CA_FILE="$PWD/build/local-caddy/data/pki/authorities/local/root.crt" \
OCTO_CARD_HOST=../OctoSense-App-Hub/target/debug/card-host \
../OctoScript-App-Design-Flow/tools/octo run bundle --port 8141 --detach --app-data build/auth-app-data
```

Open the card-host window and choose **登录或注册**. The instance can also be driven at `127.0.0.1:8141` via `/snap`, `/click` and `/g`. Keep Caddy and the server running while using the app. The app's test payment remains simulated; account authentication uses real per-user server sessions.

To open the locally installed **LIYU-MINI 1.0.17** inside OctoSense, use the shell binary built with the local App-Hub `liyu` host service, then run `./run-octosense-local.sh`. The script points OctoSense at the signed local catalog and installed bundle under `build/`, configures the HTTPS service and local CA, and opens `hub:liyu-mini` on startup. The shell's remote control listens on `127.0.0.1:8399` by default. This is a local integration build; the public OctoSense dependency pin does not yet include the `liyu` service.

约定兑现状态由双方各自记录。约定列表及礼盒详情的「附带的约定」展示当前状态，点击进入约定状态页面，可标记已兑现、改回待兑现；状态按礼物和登录账号保存到后端，仅展示并修改当前账号自己的记录。旧版共享状态保留为历史数据，不推定为任何一方的个人标记。

「我」页面底部直接提供切换账号及退出登录。设置中的深色/浅色切换即时更新页面颜色，并将偏好保存在本地；切换账号取消时保留当前登录。

心愿单流程：先新建心愿单，再逐件挑选商品（最多 8 件，也支持填写商品需求），整理后设置可见范围和发布有效期。商品详情的「加入心愿单」选择已有未发布的心愿单；没有可用的心愿单时可在子页新建并加入。未发布的心愿单保存在后端、仅自己可见，重复加入同一商品不会增加重复项，商品可移除。发布后商品清单固定，有效期从发布时起算。

## 产品名词

- 商品：商品目录中可挑选、加入心愿单的内容。心愿单中的未指定商品条目标为「商品需求」。
- 礼盒：用户选好商品后送出的对象；包含商品、拆盒方式、寄语及可选约定。未拆开也展示商品信息，送礼人身份由服务端隐藏。
- 礼物：收礼人拆开礼盒后收到的、由另一位用户送来的商品。

送出记录统一使用「礼盒」；收到记录同时包含未拆和已拆的礼盒。收礼详情按状态显示「礼盒详情」或「礼物详情」，解谜中仍属于未拆开的礼盒。商品名称、用户自填标题及历史寄语保持原文。

送礼入口直接进入「挑礼」商品目录，选中商品并点击「送给TA」后才进入「设置礼盒」。设置中的「换一件」也使用同一商品目录；重新选商品或取消更换时保留收礼人、寄语和拆盒设置。
