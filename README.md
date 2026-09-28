# LIYU-DEMO

An offline OctoScript/Splash demonstration of a small part of [LiYu](https://github.com/OctoSense-org/OctoSense/tree/liyu/apps/liyu). It contains a five-item catalog, simulated gift cards, a simple reveal puzzle, and a local wishlist. The product artwork and icon come from the LiYu source tree.

This is a contained App-Hub script app, not a replacement for the native Rust LiYu. It has no account, contact import, payment, order, voucher, delivery, AI, or network feature. Prices and gift delivery are simulated. Personal text is stored only in the app's local storage jail; users can remove their demo gifts and wishes.

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

The sibling `OctoSense-Demo-Runner` checkout is a separate build of OctoSense `main` with the App Hub feature. The signed experimental catalog in `build/desktop-mirror/` contains this demo; its trust anchor and installed-app state are local to `build/`. After building the runner once, launch it with:

```sh
./run-octosense-local.sh
```

Open **App Hub → LIYU-DEMO → Open** if the app window is not already open. The local install persists under `build/desktop-apps/`. This is a test catalog, not the public App Hub. The script defaults to the remote-control port `8399`; set `MAKEPAD_REMOTE` to another port if it is occupied.
