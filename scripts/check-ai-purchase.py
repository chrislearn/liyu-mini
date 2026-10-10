#!/usr/bin/env python3
"""Execute production proposal/date guards and demo price protection in native Splash.

Synthetic proposals test rejection, not a successful real-model inference.
"""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

root = Path(__file__).resolve().parents[1]
source = (root / 'bundle/main.splash').read_text()
transport = source[source.index('let demo_mode ='):source.index('// Keep the established response shape')]

def function(name):
    start = source.index('fn ' + name + '(')
    end = source.index('\nfn ', start + 1)
    return source[start:end]

guards = '\n'.join(function(name) for name in ['valid_plan_date', 'budget_cents', 'gift_ideas_input', 'valid_gift_result','valid_gift_plan'])
checks = '''
demo_data = demo_seed()
let ai_budget = "35.00"
let ai_occasion = "生日"
let contact_index = 0
let friends = demo_data.friends
let products = demo_data.products
let checks = 0
let failures = ""
fn check(value, name){checks = checks + 1; if !value {failures = failures + name + "; "}}
check(valid_plan_date("2028-02-29"), "leap year")
check(!valid_plan_date("2026-02-29") && !valid_plan_date("2026-04-31"), "impossible date")
check(!valid_plan_date("2026/10/09") && valid_plan_date(""), "date format and clear")
check(budget_cents()==3500, "budget cents")
ai_budget = "35.555"; check(budget_cents()==-1, "budget precision")
ai_budget = "35.01"; check(budget_cents()==3501, "budget rounding")
ai_budget = "35"; let input = gift_ideas_input()
check(input.products.len()>0, "budget catalogue")
for p in input.products {check(p.price_cents<=3500, "no over budget candidate")}
let candidate = {product_id: input.products[0].product_id, reason: "适合", buying_tip: "核对规格", message: "生日快乐"}
let plan = {status:"matched",no_match_reason:"",recommendations: [candidate]}
check(valid_gift_plan(plan,input), "known proposal")
let fake = {status:"matched",no_match_reason:"",recommendations: [{product_id: 99999, reason: "适合", buying_tip: "核对规格", message: "生日快乐"}]}
check(!valid_gift_plan(fake,input), "invented id")
check(!valid_gift_plan({status:"matched",no_match_reason:"",recommendations: [candidate,candidate]},input), "duplicate candidates")
check(!valid_gift_plan({status:"matched",no_match_reason:"",recommendations: []},input), "empty candidates")
let old = input.to_json(); ai_occasion = "乔迁"; check(gift_ideas_input().to_json()!=old, "changed occasion invalidates snapshot")
let before = demo_data.orders.len()
let body = {items: [{product_id: 1,recipient_id:9001}]}
let changed = demo_request({path:"/orders",method:"POST",body:body,idempotency_key:"guarded",expected_total:1})
check(changed.data.status==409 && demo_data.orders.len()==before, "price change no order")
let order = demo_request({path:"/orders",method:"POST",body:body,idempotency_key:"guarded",expected_total:3500}).data.body
check(order.items.len()==1, "confirmed purchase")
check(demo_request({path:"/orders",method:"POST",body:body,idempotency_key:"guarded",expected_total:3500}).data.body.id==order.id, "retry same order")
check(demo_request({path:"/orders",method:"POST",body:{items:[{product_id:3,recipient_id:9001}]},idempotency_key:"guarded",expected_total:4900}).data.status==409, "conflicting retry")
demo_request({path:"/gifts/503/open",method:"POST",body:{},idempotency_key:""})
demo_request({path:"/gifts/503/answer",method:"POST",body:{answer:"蓝色"},idempotency_key:""})
demo_request({path:"/gifts/503/accept",method:"POST",body:{agree:true},idempotency_key:""})
let schedule = {path:"/contracts/503/schedule",method:"PUT",body:{proposed_on:"2028-02-29",expected_revision:0},idempotency_key:""}
let proposal = demo_request(schedule).data.body
check(proposal.planned_on=="" && proposal.pending && proposal.proposed_on=="2028-02-29", "proposal not effective")
check(demo_request(schedule).data.status==409, "stale date refused")
schedule.body = {proposed_on:"2026-02-29",expected_revision:1}; check(demo_request(schedule).data.status==400, "invalid date refused")
let confirmation = {path:"/contracts/503/schedule/confirm",method:"POST",body:{expected_revision:1},idempotency_key:""}
check(demo_request(confirmation).data.status==409, "self confirmation refused")
confirmation.body.demo_peer = true
check(demo_request(confirmation).data.body.planned_on=="2028-02-29", "simulated peer confirmation")
View{width: Fill height: Fill Label{text:"AI_PURCHASE_CHECKS=" + checks + ";FAILURES=" + failures}}
'''
folder = root / 'build/ai-purchase-check'
folder.mkdir(parents=True, exist_ok=True)
(folder / 'main.splash').write_text(transport + '\n' + guards + '\n' + checks)
manifest = json.loads((root / 'bundle/manifest.json').read_text())
manifest.pop('integrity', None)
for field in ('requires','backend','host_api','storage'): manifest.pop(field,None)
manifest['capabilities']=['images','model','net','storage']
(folder / 'manifest.json').write_text(json.dumps(manifest))
harness = Path(os.environ.get('OCTO', str(root.parent / 'OctoScript-App-Design-Flow/tools/octo')))
env = dict(os.environ)
port = '8144'
subprocess.run([str(harness), 'run', str(folder), '--port', port, '--detach', '--app-data', str(root / 'build/ai-purchase-check-data')], env=env, check=True, capture_output=True)
try:
    result = ''
    for _ in range(30):
        state = json.load(urllib.request.urlopen('http://127.0.0.1:' + port + '/snap'))
        result = next((n.get('t', '') for n in state['s'] if n.get('ty') == 'Label' and n.get('t', '').startswith('AI_PURCHASE_CHECKS=')), '')
        if result:
            break
        time.sleep(.1)
    assert result and result.endswith('FAILURES='), result or 'Native guard check did not render'
    print(result)
finally:
    urllib.request.urlopen('http://127.0.0.1:' + port + '/quit').read()
