#!/usr/bin/env python3
"""Check bundled size/images and exercise the actual demo transport in native Splash."""
import json, pathlib, os, subprocess, time, urllib.request
root=pathlib.Path(__file__).resolve().parents[1]
size=sum(p.stat().st_size for p in (root/'bundle').rglob('*') if p.is_file())
assert size < 8_000_000, f'Bundle exceeds 8 MB: {size}'
assert len(list((root/'bundle/assets').glob('p[0-9][0-9].png')))==8
source=(root/'bundle/main.splash').read_text()
seed=json.loads(json.loads(source.split('fn demo_seed(){ return ',1)[1].split('.parse_json()',1)[0].strip()))
for p in seed['products']: assert (root/'bundle'/p['demo_image'].lstrip('/')).is_file(),p['name']
transport=source[source.index('let demo_mode ='):source.index('// Keep the established response shape')]
checks=r'''
demo_data = demo_seed()
let failures = ""
let checks = 0
fn check(value, name){ checks = checks + 1; if !value { failures = failures + name + "; " } }
fn call(path, method, body){ return demo_request({path: path, method: method, body: body, idempotency_key: "test-order"}) }
check(call("/catalog", "GET", nil).data.body.items.len() == 8, "catalog")
let sealed = call("/gifts/501", "GET", nil).data.body
check(sealed.sender == nil && sealed.product.name != "", "sealed product visible and sender hidden")
call("/gifts/501/open", "POST", {})
check(call("/gifts/501", "GET", nil).data.body.sender.display_name == "林舟", "explicit free opening")
let initial = demo_data.wallet.balance_cents
call("/gifts/501/cash-out", "POST", {})
check(demo_data.wallet.balance_cents == initial + 3920 && demo_data.wallet.ledger.len() == 2, "cash-out ledger")
check(call("/gifts/501/cash-out", "POST", {}).data.status == 400 && demo_data.wallet.balance_cents == initial + 3920, "duplicate cash-out")
call("/gifts/502/open", "POST", {})
check(!call("/gifts/502/answer", "POST", {answer: "错误"}).data.body.correct, "wrong guess")
check(call("/gifts/502", "GET", nil).data.body.sender == nil, "wrong guess hides sender")
check(call("/gifts/502/answer", "POST", {answer: "林舟"}).data.body.correct, "correct guess")
call("/gifts/503/open", "POST", {})
for _i in 3 { call("/gifts/503/answer", "POST", {answer: "错误"}) }
check(call("/gifts/503", "GET", nil).data.body.sender == nil, "three wrong answers never reveal")
demo_data = demo_seed()
call("/gifts/503/open", "POST", {})
check(call("/gifts/503/answer", "POST", {answer: "蓝色"}).data.body.correct, "correct question")
call("/gifts/503/accept", "POST", {agree: true})
check(call("/gifts/503", "GET", nil).data.body.state == "accepted", "accept")
call("/contracts/503/status", "PUT", {status: "fulfilled"})
check(call("/gifts/503", "GET", nil).data.body.contract_status == "fulfilled", "own contract mark")
let wid = call("/wishlists/drafts", "POST", {title: "测试清单", items: []}).data.body.id
call("/wishlists/" + wid + "/items", "POST", {product_id: 1})
call("/wishlists/" + wid + "/items", "POST", {product_id: 3})
check(call("/wishlists/" + wid, "GET", nil).data.body.items.len() == 2, "multi-product wishlist")
check(call("/wishlists/" + wid + "/items", "POST", {product_id: 1}).data.body.already_present, "wishlist deduplicates")
call("/wishlists/" + wid + "/publish", "POST", {title: "已发布"})
check(call("/wishlists/" + wid + "/items", "POST", {product_id: 6}).data.status == 400, "published items fixed")
let items = [{product_id: 1, recipient_id: 9001}, {product_id: 3, recipient_id: 9002}]
check(call("/orders/quote", "POST", {items: items}).data.body.total_cents == 8400, "batch quote")
let order = call("/orders", "POST", {items: items}).data.body
check(order.items.len() == 2, "one box per recipient")
check(call("/orders", "POST", {items: items}).data.body.id == order.id, "order idempotency")
for item in order.items { call("/gifts/" + item.gift_id + "/puzzle", "PUT", {unlock_kind: "question", clue: "颜色", answer: "蓝色", message: "演示", contract_text: "一起看电影"}) }
check(call("/gifts/" + order.items[0].gift_id, "GET", nil).data.body.ready, "outgoing puzzle configuration")
let a = call("/me/addresses", "POST", {recipient_name: "体验", phone: "13800000000", address: "虚构地址", is_default: false}).data.body.id
check(call("/me/addresses", "GET", nil).data.body.len() == 2, "multiple addresses")
call("/me/addresses/" + a, "DELETE", {})
check(call("/me/addresses", "GET", nil).data.body.len() == 1, "delete address")
check(call("/not-a-real-route", "POST", {}).data.status == 400, "unsupported request stays local")
demo_data = demo_seed()
check(call("/gifts/501", "GET", nil).data.body.state == "sealed", "demo reset")
View{width: Fill height: Fill flow: Down Label{text: "DEMO_CHECKS=" + checks + ";FAILURES=" + failures}}
'''
folder=root/'build/demo-flow-check';folder.mkdir(parents=True,exist_ok=True)
(folder/'main.splash').write_text(transport+checks)
manifest=json.loads((root/'bundle/manifest.json').read_text());manifest.pop('integrity',None);manifest.pop('requires',None);manifest.pop('backend',None);manifest.pop('host_api',None);manifest['capabilities']=['images','model','net','storage'];manifest.pop('storage',None)
(folder/'manifest.json').write_text(json.dumps(manifest))
harness=pathlib.Path(os.environ.get('OCTO',str(root.parent/'OctoScript-App-Design-Flow/tools/octo')))
env = dict(os.environ)
# Respect configured runtime paths; otherwise let the harness discover releases.
for key, binary in [('OCTO_HUB', 'hub'), ('OCTO_CARD_HOST', 'card-host')]:
 candidate = root.parent / 'OctoSense-App-Hub/target/debug' / binary
 if key not in env and candidate.is_file():
  env[key] = str(candidate)
port='8143'
subprocess.run([str(harness),'run',str(folder),'--port',port,'--detach','--app-data',str(root/'build/demo-flow-check-data')],env=env,check=True,capture_output=True)
try:
 result=''
 for _ in range(30):
  state=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'))
  result=next((n.get('t','') for n in state['s'] if n.get('ty')=='Label' and n.get('t','').startswith('DEMO_CHECKS=')),'')
  if result:break
  time.sleep(.1)
 assert result and result.endswith('FAILURES='), result or 'native demo check failed to render; inspect build/demo-flow-check-data/card-host.log'
 print(result);print(f'Bundle: {size:,} bytes; 8 bundled product images; below 8,000,000 bytes')
finally: urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
