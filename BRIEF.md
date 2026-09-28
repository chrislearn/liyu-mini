# LIYU-DEMO brief

LIYU-DEMO 0.2 is a contained OctoScript/Splash prototype for a complete **local simulation** of the request-to-card flow. The on-screen command parser is deterministic and recognizes a small set of Chinese intents and product words. It is not an AppCard or AI integration.

1. Enter “给我创建一个心愿单，买一个 iphone”. The app proposes a wishlist card with two illustrative iPhone variants. The user chooses a model, edits the title and optional note, then confirms. A structured local wishlist record appears.
2. Enter “送阿宁一个 iphone”. The app proposes a gift card with the matched sample contact, model options, reveal mode (question, passphrase, direct), question/answer, and greeting. The user confirms; a local sealed gift appears. Entering the sample answer reveals the chosen item.
3. Browse 13 illustrative products, see details, and begin a wishlist or gift draft directly. Three sample contacts are preloaded; users can add or remove local contacts with relationship and occasion notes. Both gift and wishlist records can be removed.

No orders, checkout, payment, stock, vouchers, messages, contact import, account authentication, or real delivery occur. iPhone variants are deliberately labeled illustrative placeholders, not live Apple SKUs. A public HTTPS image is loaded only on the catalog screen; core images are bundled and the flow works offline. The app requests `storage` and `images`, but not broad HTTP API access (`net`). External image requests go to `raw.githubusercontent.com` and carry the normal network metadata of an image load; no contact or wish data is sent there.

The bundle is well below the 8 MiB limit. The chosen LiYu photos were copied locally and one large flower PNG was converted to a small JPEG. Loading optional product art from HTTPS is possible with `images`; a future live catalog API would additionally need `net` with explicit hosts and a real backend contract.

The old 0.1 data file remains in the app jail; 0.2 writes `demo-v2.json` because it has a different record schema. No automatic migration is performed for this experiment.

Acceptance: validate with `tools/octo check`; run in `card-host`; drive both example commands through confirmation; inspect persisted JSON; test gift reveal and local contact management; capture real screenshots; install the updated signed 0.2 bundle in the local OctoSense App Hub. Public publication remains a separate human step.
