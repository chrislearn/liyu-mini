# LIYU-MINI capability boundary (2026-09-28)

| LIYU feature | Splash / App Hub status | LIYU-MINI behavior |
| --- | --- | --- |
| Catalog, search, categories and product pictures | Supported through Splash UI, `images` and `net` with exact HTTPS hosts | 33 original sample products, two iPhone placeholders, search/filter, optional public catalog sync; 25 local images and eight HTTPS images |
| Local contacts and wishlists | Supported in app storage; no platform contacts API | Fictional starter contacts, add/edit/remove, multi-item wishlists |
| Gift draft, reveal question/passphrase and recipient review | Supported as local UI and storage | Draft confirmation, local gift box, reveal and simulated acceptance |
| Live LIYU catalog/stock, shared contacts, real wishlists and orders | Technically possible over an allowed public HTTPS LIYU API, but none is configured: the current native client defaults to `http://127.0.0.1:8787`, and the contained runtime refuses HTTP and private hosts | No live business requests; prices and gift records are illustrative |
| LIYU account login, password and verification code | The publication gate refuses password/code input fields; the policed runtime makes password fields inert. No general LIYU authentication host service or sheet is registered | No account login or cross-device session |
| Purchase, payment, voucher, wallet, delivery, recipient claiming | Need authenticated LIYU server workflows and a real payment/delivery integration; `net` alone cannot grant a session or make the local simulation real | Not offered; “accept” changes only local demo state |
| System AppCard / assistant calling this app's product and gift actions | App Hub can validate a `tools.json`, but current OctoSense shells do not load and execute contained-app tools/agents or expose an AppCard bridge | The in-app command field uses local keyword rules; the review card is a Splash view, not a system AppCard |
| Native Makepad UI, system contact import and unrestricted local device access | A Hub bundle contains no native code and receives only declared sandbox capabilities | LIYU-MINI is a contained app; LIYU remains the native implementation |

To close the remaining product gap, deploy LIYU's server at a real public HTTPS origin and define a host-owned LIYU account service/sheet that keeps credentials and sessions outside the app. Then add the exact API host to the manifest and implement authenticated catalog, contacts, wishlists and gift state calls. For AppCard routing, OctoSense must execute contained-app tools and expose them to its system assistant with explicit user confirmation for gift actions. These are host and backend changes, not manifest switches.

Source of runtime and publication rules: [capabilities](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md), [script API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md), [host services](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/HOST-SERVICES.md), [App Hub publishing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md).
