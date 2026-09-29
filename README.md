# LIYU-MINI

LIYU-MINI is the OctoScript/Splash version of [LIYU](https://github.com/chrislearn/OctoSense/tree/liyu/apps/liyu). This checkout is configured for **local integration testing** with `liyu-server`; the running app has no bundled catalog, fictional contacts, or local gift/wishlist records. It requests products, categories, prices, stock, the signed-in account, friends, wishlists, and gifts through the host's `liyu` service. Friend detail now includes owner-private nickname, phone, email, relationship, birthday, and note fields. Each field opens a separate editor and saves through the host service; recent wishes and sent/received gift lists link to the existing detail flows. Product images use `https://liyu.localhost:8443`. An optional short Chinese keyword parser opens a review screen using the returned products and friends. An exact or broad wishlist is written to the server after confirmation. Gift checkout uses “+ TA” to add friends, permits removing each selected friend, and obtains a combined server quote for up to 100 recipients. One test order creates one gift per recipient after explicit confirmation and `pay-test`; puzzle settings and gift state changes also use the server API.

The 412-point phone shell follows the Makepad LIYU element tree: 58-point top bar, 66-point icon navigation, segmented tabs, category chips, two-column product cards, compact gift/contact rows, and the four-section wishlist and gift forms. See [UI-PARITY.md](UI-PARITY.md) for the source-to-Splash mapping and remaining differences. `liyu-server` is still a **test** backend with seeded products, optional local social/gift fixtures, test payment, and test delivery; these are persisted server records, not LIYU-MINI fallback data. LIYU-MINI does not sign in with a seeded account. If that backend has no iPhone product, LIYU-MINI does not invent one. The in-app command screen is a Splash view, not a system AppCard integration. A top-bar layout switch enables a desktop mode with LIYU-style 208-point left navigation, a flexible central content column, and a 300-point right information column. The phone layout retains its bottom navigation; the desktop mode is manually selected and is intended for wide viewports.

LIYU-MINI now has the same account gate as native LIYU: sign in or register with an email/phone identifier, password, and registration code; restore the server session on restart; return to the gate on logout or HTTP 401. The password and code are typed into an **OctoSense-owned sheet**, not the contained app. The host keeps the Bearer token in `<app-data>/.host/liyu/liyu-mini/session.json` with owner-only file permissions and proxies authenticated business requests. Caddy no longer injects a shared account. The `liyu` capability and service are currently implemented in the **local App-Hub checkout**; its pinned version in the OctoSense shell and the public App Hub do not yet include this change. A public release also needs a public HTTPS LIYU origin and host rollout. See [CAPABILITY-GAP.md](CAPABILITY-GAP.md) and [PRIVACY.md](PRIVACY.md).

## Run locally

Start `liyu-server` on `127.0.0.1:8789` with the local database. For a local registration test, `LIYU_TEST_DELIVERY=true` returns a test verification code; normal deployments need a configured delivery webhook. Caddy proxies the same server at `https://liyu.localhost:8443` without attaching Authorization. The host service uses that HTTPS address too; `LIYU_SERVICE_CA_FILE` supplies its local CA to Rust's TLS verifier. Run these long-lived commands in separate terminals:

```sh
cd ../liyu-server && LIYU_BIND=127.0.0.1:8789 LIYU_TEST_DELIVERY=true target/debug/liyu-server
caddy run --config build/local-caddy/Caddyfile --adapter caddyfile
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
