# LIYU-DEMO brief

An offline interactive preview of LiYu's anonymous-gifting idea. No account, payment, contact, delivery, voucher, network request, or AI runs in this version.

Screens and actions:

1. Discover five selected items from LiYu's catalog and open a product detail.
2. Enter a local recipient label and message, then add a simulated gift to the on-device experience box.
3. Inspect a sealed gift, answer a fixed light puzzle, then reveal the item. A preloaded gift demonstrates the flow immediately. Simulated gifts can be removed locally.
4. Add and remove local wishes.

Empty and error states: an empty box and wishlist have messages; missing recipient, message or wish prompts for input; a wrong puzzle answer offers a clue. Gifts and wishes persist in the app's storage jail across restarts.

Capability: `storage` only. No network hosts. Five local illustrative product images and the LiYu icon are bundled.

Scope boundary: App-Hub script bundles cannot ship LiYu's native Rust/Makepad executable or collect account passwords and verification codes inside the contained app. No general host authentication service was available for this exercise, and the app therefore has no account flow. The device AI service is also unavailable to a contained app. Real orders, payments, vouchers, social delivery and backend data were intentionally omitted for this offline demonstration; they are not claimed to be technically impossible in every future host configuration.

Acceptance: run in `card-host`, drive each action through the remote bridge, verify persistence after restart, capture real screenshots, pass `hub check`, and answer `hub scan` questions.
