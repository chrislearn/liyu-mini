#!/usr/bin/env python3
"""Production date/page/recovery functions in native Splash; synthetic backend, real private files and process restart."""
import datetime, json, os, subprocess, time, urllib.request
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = (root / 'bundle/main.splash').read_text()
def function(name):
    start = source.index('fn ' + name + '(')
    end = source.index('\nfn ', start + 1)
    return source[start:end]
names = ['floor_div', 'shanghai_time', 'pad2', 'expiry_time', 'record_has', 'api_request_once', 'api_request', 'read_list_pages', 'persist_purchase', 'restore_purchase', 'clear_purchase_recovery', 'retry_purchase', 'purchase_order_matches', 'resume_purchase', 'checkout_failed', 'create_order', 'get', 'configure_paid_gifts', 'save_display_name']
functions = '\n'.join(function(n) for n in names).replace('host.request(', 'fixture_backend_request(').replace('fs.write(', 'fixture_write(').replace('fs.remove(', 'fixture_remove(')
fixture = '''
let auth_state="signed_in"
let read_versions={}
let profile=nil
let profile_edit_value="saved"
let friend_wishes=[]
let wish_previews=[]
let wish_lists_loading=false
let gift_side="inbox"
let tab="command"
let stage="checkout"
let storage_failure=false
let cleanup_failure=false
let deferred=false
let callbacks=[]
let zero_id=false
let demo_mode=false
let connection="fixture-handle"
let auth_generation=1
let purchase_pending=-1
let purchase_request=nil
let purchase_expected=-1
let purchase_recipient_ids=[]
let purchase_settings=nil
let purchase_needs_answer=false
let purchase_recovery_blocked=false
let purchase_busy=false
let order_key=""
let quote=nil
let notice=""
let draft_product=-1
let draft_recipient_ids=[]
let draft_unlock="free"
let draft_clue=""
let draft_expiry_hours="24"
let response=nil
let reads=0
let writes=0
let broken=false
let legacy=false
let mismatch=false
let order_status="pending"
let completion_reads=0
let checks=0
let failures=""
fn fixture_write(path,data){fs.write(if storage_failure {"uncreated-review-directory/file"} else {path},data)}
fn fixture_remove(path){if !cleanup_failure {fs.remove(path)}}
fn account_write(path,method,body,done){done({name:body.display_name})}
fn refresh(){}
fn demo_request(input){return {is_ok:true,data:{status:200,body:{demo:true}}}}
fn check(value,label){checks=checks+1;if !value {failures=failures+label+";"}}
fn receive(r){response=r}
fn auth_lost(message){notice=message}
fn get_paid_order(id){completion_reads=completion_reads+1;purchase_busy=false}
fn submit_purchase(){writes=writes+1}
fn pay_pending_order(){writes=writes+1;purchase_busy=false}
fn fixture_backend_request(method,args,done){
 reads=reads+1
 if legacy {done({is_ok:true,data:{status:200,body:[]}});return}
 let path=args.query.path
 if deferred {callbacks.push(done);return}
 if path.search("/orders/")==0 {done({is_ok:true,data:{status:200,body:{id:42,status:order_status,total_cents:if mismatch {3600} else {3500},items:purchase_request.items}}});return}
 let catalog=path.search("/catalog?")==0
 let cursor=if catalog {path.split("cursor=")[1].to_f64()} else {path.split("before=")[1].to_f64()}
 let items=[]
 for i in 20 {let id=if catalog {cursor+1+i} else {if cursor==0 {60-i} else {cursor-1-i}}; if (catalog && id<=60) || (!catalog && id>=1) {items.push({id:id})}}
 let last=if items.len()==0 {-1} else {items[items.len()-1].id}
 let next=if (catalog && last<60) || (!catalog && last>1) {""+last} else {nil}
 if broken {next="999"}
 if zero_id {items=[{id:0}];next=nil}
 done({is_ok:true,data:{status:200,body:{items:items,next_cursor:next}}})
}
'''
phase1 = r'''
if fs.exists("purchase-recovery.json") {fs.remove("purchase-recovery.json")}
api_request({path:"/catalog?limit=50"},receive)
check(response.is_ok && response.data.body.items.len()==61 && response.data.body.items[60].id==60,"catalog beyond first fifty: "+response.to_json()+" reads="+reads)
check(reads==4,"bounded catalog pages")
api_request({path:"/friends"},receive)
check(response.is_ok && response.data.body.len()==60 && response.data.body[59].id==1,"descending list pages: "+response.to_json())
broken=true;api_request({path:"/friends"},receive);check(!response.is_ok,"nonprogressing cursor refused");broken=false
legacy=true;api_request({path:"/friends"},receive);check(!response.is_ok,"old unpaged server rejected instead of empty list");legacy=false
zero_id=true;api_request({path:"/friends"},receive);check(!response.is_ok,"zero descending ID refused");zero_id=false
deferred=true;get("/me/profile","profile");get("/me/profile","profile")
callbacks[1]({is_ok:true,data:{status:200,body:{name:"new"}}});callbacks[0]({is_ok:true,data:{status:200,body:{name:"old"}}})
check(profile.name=="new","late old same-account response discarded")
callbacks=[];get("/wishlists/7","preview");get("/wishlists/friends","friend_wishes")
callbacks[1]({is_ok:true,data:{status:200,body:{items:[],next_cursor:nil}}});callbacks[0]({is_ok:true,data:{status:200,body:{id:7}}})
check(wish_previews.len()==0,"old wishlist detail cannot repopulate refreshed previews")
callbacks=[];get("/me/profile","profile");auth_generation=auth_generation+1;callbacks[0]({is_ok:true,data:{status:200,body:{name:"other-account"}}})
check(profile.name=="new","account switch ignores deferred profile")
callbacks=[];get("/me/profile","profile");save_display_name();callbacks[0]({is_ok:true,data:{status:200,body:{name:"before-save"}}})
check(profile.name=="saved","late profile read cannot undo successful edit profile="+profile.to_json()+" versions="+read_versions.to_json()+" notice="+notice)
deferred=false
purchase_request={items:[{product_id:1,recipient_id:7}],expires_hours:24};purchase_expected=3500;purchase_recipient_ids=[7];order_key="same-attempt";purchase_pending=42
purchase_settings={unlock_kind:"question",clue:"颜色？",answer:"蓝色",message:"心意",contract_text:"电影"}
storage_failure=true;purchase_busy=true;check(!persist_purchase() && !purchase_busy && !fs.exists("purchase-recovery.json"),"storage failure stops purchase before write");storage_failure=false
check(persist_purchase(),"persist before continuation")
let saved=fs.read("purchase-recovery.json").parse_json()
check(saved.to_json().search("\"answer\":")<0 && saved.to_json().search("\"connection\":")<0 && saved.to_json().search("\"token\":")<0,"no credentials or puzzle answer stored: "+saved.to_json())
check(saved.key=="same-attempt" && saved.order_id==42,"same order and idempotency key")
'''
zone = datetime.timezone(datetime.timedelta(hours=8))
for epoch in [0, -28801, 951753599, 951753600, 1791820799, 1791820800, 4102444800] + [1000000000+i*7654321 for i in range(24)]:
    expected = datetime.datetime.fromtimestamp(epoch, zone).strftime('%Y-%m-%d %H:%M')
    phase1 += 'check(expiry_time('+str(epoch)+')=='+json.dumps(expected)+',"Shanghai epoch '+str(epoch)+' actual="+expiry_time('+str(epoch)+'))\n'
phase2 = '''
restore_purchase()
check(purchase_pending==42 && order_key=="same-attempt" && purchase_request.items[0].recipient_id==7,"real restart restores original order")
check(writes==0 && purchase_needs_answer && purchase_settings.answer=="","restore never pays; answer must be reentered")
retry_purchase();check(writes==0,"missing puzzle answer stops retry")
purchase_settings.answer="蓝色";retry_purchase();check(writes==1 && order_key=="same-attempt","retry uses original order")
mismatch=true;retry_purchase();check(writes==1 && notice.search("不一致")>=0,"mismatching recovered order cannot pay");mismatch=false
order_status="paid_test";retry_purchase();check(writes==1 && completion_reads==1,"paid recovery is read without paying again")
order_status="cancelled";retry_purchase();check(writes==1 && notice.search("待支付")>=0,"cancelled order cannot pay")
demo_mode=true;order_key="demo";persist_purchase();check(fs.read("purchase-recovery.json").parse_json().key=="same-attempt","demo never overwrites real recovery")
demo_mode=false;cleanup_failure=true;purchase_busy=true;configure_paid_gifts([],0)
check(purchase_request!=nil && purchase_pending==42 && !purchase_busy && notice.search("清理")>=0 && fs.exists("purchase-recovery.json"),"cleanup failure keeps recovery and blocks false completion")
cleanup_failure=false;clear_purchase_recovery();check(!fs.exists("purchase-recovery.json"),"completed recovery removed")
fs.write("purchase-recovery.json","invalid json");purchase_request=nil;restore_purchase()
check(purchase_recovery_blocked && purchase_request==nil && fs.read("purchase-recovery.json")=="invalid json","corrupt recovery preserved and blocks new purchases")
create_order();check(writes==1 && purchase_request==nil,"corrupt recovery blocks creating another order")
fs.remove("purchase-recovery.json")
purchase_recovery_blocked=false;purchase_request={items:[{product_id:1,recipient_id:7}],expires_hours:721};persist_purchase();purchase_request=nil;restore_purchase()
check(purchase_recovery_blocked && purchase_request==nil,"invalid expiry recovery refused")
purchase_request={items:[{product_id:1,recipient_id:0}],expires_hours:24};purchase_recipient_ids=[0];persist_purchase();purchase_request=nil;restore_purchase()
check(purchase_recovery_blocked && purchase_request==nil,"nonpositive recipient recovery refused")
fs.remove("purchase-recovery.json")
'''
bundle = root / 'build/resilience-check'
bundle.mkdir(parents=True, exist_ok=True)
manifest = json.loads((root/'bundle/manifest.json').read_text())
for key in ['integrity','requires','backend','host_api','storage','network']: manifest.pop(key,None)
manifest['capabilities']=['storage']
(bundle/'manifest.json').write_text(json.dumps(manifest))
harness=Path(os.environ.get('OCTO',str(root.parent/'OctoScript-App-Design-Flow/tools/octo')))
port='8152'
for phase in [phase1,phase2]:
    (bundle/'main.splash').write_text(fixture+'\n'+functions+'\n'+phase+'\nView{Label{text:"RESILIENCE_CHECKS="+checks+";FAILURES="+failures}}')
    subprocess.run([str(harness),'run',str(bundle),'--port',port,'--detach','--app-data',str(root/'build/resilience-check-data')],check=True,capture_output=True)
    try:
        result=''
        for _ in range(70):
            state=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'))
            result=next((n.get('t','') for n in state['s'] if n.get('t','').startswith('RESILIENCE_CHECKS=')),'')
            if result: break
            time.sleep(.2)
        assert result and result.endswith(';FAILURES='), result or state
        print(result)
    finally:
        urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
