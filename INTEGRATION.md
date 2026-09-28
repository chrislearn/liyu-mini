# From LIYU-MINI's local card to a real AppCard flow

The current command field lives inside LIYU-MINI. It uses literal keyword matching, not a model. The draft card is a Splash view in the app, not a system-generated AppCard card. The AppCard module in OctoSense can route requests to native modules, while the published contained-app agent manifest is not yet loaded by the shell. A third-party app therefore cannot currently register product/contact/draft tools that AppCard will call end to end.

An actual integration needs an AppCard-to-contained-app tool bridge and a narrow contract. A possible contract is:

| Tool | Input | Output | Boundary |
| --- | --- | --- | --- |
| `liyu_demo.search_products` | query, category | public product IDs, names, variants, price source and availability | Read-only; never expose private user data. |
| `liyu_demo.find_contact_candidates` | name fragment | only the user's consenting local matching contact labels and opaque IDs | Scoped to this app, with explicit contact access/consent; do not export the address book to the model. |
| `liyu_demo.prepare_wishlist_draft` | product ID, suggested title | short-lived draft handle / app route | Does not create a purchase or persist until user confirms inside the app. |
| `liyu_demo.prepare_gift_draft` | recipient ID, product/variant ID, suggested greeting | short-lived draft handle / app route | Opens the app's own review screen; never sends, pays, or reveals an answer. |

The AppCard orchestrator should ask for missing recipient or variant and render a short-lived review card. Selection should carry opaque IDs and explicit source freshness, not a guessed product name or invented current price. Tapping the card opens LIYU-MINI at the draft handle. The app itself shows recipient, exact variant, price/availability source, reveal mode, question, and greeting, then requires a final user action. Reveal answers stay inside the app and are not returned to AppCard or a model. A real purchase still needs a backend, user account/session, inventory check, and payment/delivery flow; those are outside this demo.

Until that bridge exists, the local parser and card are a UX prototype. `model.complete` and contained-app agent manifests do not currently provide an on-device AppCard integration. The `images` grant permits the optional HTTPS catalog illustration; live API requests would need `net` and explicit `network.hosts` entries. The 8 MiB bundle limit can be met by bundling compact core thumbnails and loading larger photos from a trusted HTTPS image origin on demand, with offline placeholders and an appropriate privacy description.
