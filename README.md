# LIYU-DEMO

An OctoScript/Splash demonstration of LiYu's request-to-card experience. It contains 13 illustrative products, three sample contacts plus manual contact entry, structured wishlists, and simulated gifts with question, passphrase, or direct reveal. The product artwork and icon come from the local LiYu source tree.

This is a contained App-Hub script app, not a replacement for native Rust LiYu. Enter “给我创建一个心愿单，买一个 iphone” or “送阿宁一个 iphone” to see a **local rule-based** temporary card, choose a model and recipient, and confirm a local record. It is not connected to the system AppCard or AI. There is no account, contact import, payment, order, voucher, delivery, or actual gift sending. Prices and gifts are simulated. Personal text is stored only in the app's local storage jail; users can remove demo contacts, gifts, and wishes.

The app can load public HTTPS images with the `images` capability. The catalog has one optional online illustration from GitHub; all images needed for the main flow are bundled. This bundle does not request `net`, so it cannot call arbitrary business APIs. See [INTEGRATION.md](INTEGRATION.md) for the proposed AppCard bridge and [BRIEF.md](BRIEF.md) for the demo scope.

The submission candidate is `bundle/`. `BRIEF.md` documents the scope, and `build/` holds local review artifacts excluded from Git. The listing uses experimental publisher details. Its privacy-policy URL is a **planned** URL: the `chrislearn/liyu-demo` repository does not exist yet, so the link is not live and the bundle must not be submitted as-is.

To validate on macOS with [OctoScript-App-Design-Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow):

```sh
OCTOSENSE_APP_HUB=/path/to/OctoSense-App-Hub tools/octo doctor
OCTOSENSE_APP_HUB=/path/to/OctoSense-App-Hub tools/octo run /path/to/liyu-demo/bundle --port 8141 --hidden --detach
OCTOSENSE_APP_HUB=/path/to/OctoSense-App-Hub tools/octo check /path/to/liyu-demo/bundle
curl -s 127.0.0.1:8141/quit
```

The code and copied LiYu assets follow the source repository's Apache-2.0 license; see `LICENSE`.

## Run inside local OctoSense

The sibling `OctoSense-Demo-Runner` checkout is a separate build of OctoSense `main` with the App Hub and opt-in AppCard features. The signed experimental catalog in `build/desktop-mirror/` contains this demo; its trust anchor and installed-app state are local to `build/`. Build and launch it with:

```sh
cd ../OctoSense-Demo-Runner
cargo build --release --locked -p octosense --no-default-features --features app-hub,app-appcard
cd ../liyu-demo
./run-octosense-local.sh
```

The script enables AppCard and points the shell to the `octos` executable found on `PATH`, with an isolated kernel profile under `build/octos-core/`. Open **Applications → AppCard** in the desktop launcher. On a fresh checkout, configure a model in **AI providers** before generating a card: AppCard requires `build/octos-core/.octos/profiles/_main.json`, and an empty core directory causes `profile '_main' is not configured`. This machine's local, Git-ignored `_main` profile was initialized from its existing `octos` model selection and credentials, with file mode `0600`; the original profile was not changed. A prompt for a Beijing weather card then generated and rendered successfully.

Open **App Hub → LIYU-DEMO → Open** as a separate window to see the contained demo. AppCard does not yet route to LIYU-DEMO's local command parser or its data. The local install persists under `build/desktop-apps/`. This is a test catalog, not the public App Hub. The script defaults to the remote-control port `8399`; set `MAKEPAD_REMOTE` to another port if it is occupied.
