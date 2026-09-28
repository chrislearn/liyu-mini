# LIYU-MINI

LIYU-MINI is a contained OctoScript/Splash demonstration of the native [LIYU](https://github.com/chrislearn/OctoSense/tree/liyu/apps/liyu) gift experience. It ships LIYU's 33 sample catalog items plus two clearly marked iPhone model placeholders. People can search and filter products, type a limited Chinese gift or wishlist request, review a draft card, edit sample contacts, build multi-item local wishlists, set a reveal question or passphrase, and open and accept a simulated gift. No action buys or sends anything.

The app runs offline for its core flows. `images` fetches eight large product pictures from the public LIYU source repository over HTTPS, keeping the bundle below the Hub's 8 MB limit. With `net` restricted to `raw.githubusercontent.com`, the user may manually synchronize the public demo catalog in this repository; the bundled 35-item catalog remains available if the request fails. It sends no contact, wishlist or gift data to the network. See [PRIVACY.md](PRIVACY.md).

The current OctoSense shell does not connect a published Splash app's data and actions to the system AppCard, and has no LIYU account host service. LIYU's server also defaults to a local HTTP address, which the sandbox cannot access. The app therefore uses local rule matching and local sample data. See [CAPABILITY-GAP.md](CAPABILITY-GAP.md) for the exact feature boundary.

Only `bundle/` is submitted to App Hub. The remaining files are source and documentation. The bundle uses the app ID `liyu-mini`; it has a separate storage jail from the former `liyu-demo`. Old demo data is not migrated automatically.

## Validate locally

```sh
OCTO_HUB=/path/to/hub OCTO_CARD_HOST=/path/to/card-host \
  ../OctoScript-App-Design-Flow/tools/octo run bundle --port 8141 --hidden --detach
OCTO_HUB=/path/to/hub OCTO_CARD_HOST=/path/to/card-host \
  ../OctoScript-App-Design-Flow/tools/octo check bundle
curl -s 127.0.0.1:8141/quit
```

The reference host is built from [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub). `run-octosense-local.sh` starts the optional local OctoSense shell and AppCard module using the ignored `build/desktop-mirror/` catalog; regenerate that mirror for this bundle before using the launcher. The original LIYU assets are Apache-2.0 licensed; see [LICENSE](LICENSE).
