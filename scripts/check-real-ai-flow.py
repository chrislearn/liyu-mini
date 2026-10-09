#!/usr/bin/env python3
"""Production Splash flow with server response capture and explicit model adapter.
This checks transport/control flow, never claims real external inference.
LIYU_AI_SERVER_CAPTURE can point to responses read through real host PKCE APIs.
"""
import json, os, subprocess, time, urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'bundle/main.splash').read_text()
def function(name):
 start=s.index('fn '+name+'(');end=s.index('\nfn ',start+1)
 return s[start:end].replace('host.request(', 'model_adapter(')
names=['budget_cents','gift_ideas_input','valid_gift_plan','gift_ai_error','ask_gift_ideas','generate_gift_ideas']
seed=json.loads(json.loads(s.split('fn demo_seed(){ return ',1)[1].split('.parse_json()',1)[0].strip()))
capture_path=os.environ.get('LIYU_AI_SERVER_CAPTURE')
capture=json.loads(Path(capture_path).read_text()) if capture_path else {'friends':{'status':200,'body':seed['friends']},'catalog':{'status':200,'body':{'items':seed['products']}}}
assert capture['friends']['status']==200 and capture['friends']['body'] and capture['catalog']['status']==200
fixture='let server = '+json.dumps(json.dumps(capture,ensure_ascii=False),ensure_ascii=False)+'.parse_json()\n'+r'''
let friends=server.friends.body.to_json().parse_json()
let products=server.catalog.body.items
let contact_index=0
let contact_id=friends[0].id
let stage="contact_detail"
let auth_state="signed_in"
let auth_generation=1
let ai_context=0
let ai_budget="100"
let ai_occasion="生日，喜欢咖啡"
let demo_mode=false
let ai_busy=false
let ai_text=""
let ai_plan=nil
let ai_plan_snapshot=""
let ai_plan_friend=-1
let notice=""
let backend_calls=0
let model_calls=0
let sent=nil
let fail_path=""
let model_error=""
let changed=false
let delayed=false
let pending=nil
let malformed=false
fn refresh(){}
fn start_timeout(seconds,done){}
fn api_request(args,done){
 backend_calls=backend_calls+1
 if args.path==fail_path {done({is_ok:true,data:{status:401,body:nil}});return}
 done({is_ok:true,data:if args.path=="/friends" {server.friends} else {server.catalog}})
}
fn model_adapter(method,args,done){
 model_calls=model_calls+1;sent=args
 if delayed {pending=done;return}
 if changed {auth_generation=auth_generation+1}
 if model_error!="" {done({is_ok:false,error:model_error});return}
 let id=if malformed {999999} else {args.input.products[0].product_id}
 done({is_ok:true,data:{output:{recommendations:[{product_id:id,reason:"测试适合原因",buying_tip:"测试核对规格",message:"测试寄语"}]}}})
}
'''
checks=r'''
let checks=0
let failures=""
fn check(value,label){checks=checks+1;if !value {failures=failures+label+";"}}
// Deliberately stale local state: the request must use captured server responses.
friends[0].note="local stale"
products=[]
ask_gift_ideas()
check(backend_calls==2 && model_calls==1,"backend reads then model")
check(sent.input.recipient_id==contact_id,"selected server recipient")
check(sent.input.birthday==server.friends.body[0].birthday && sent.input.note==server.friends.body[0].note,"server details forwarded")
check(sent.input.budget_cents==10000 && sent.input.occasion==ai_occasion,"user preferences forwarded")
check(sent.input.products.len()>0 && sent.input.products.len()<=50,"bounded server catalog")
check(sent.input.to_json().search("\"phone\":")<0 && sent.input.to_json().search("\"email\":")<0 && sent.input.to_json().search("\"display_name\":")<0,"no contact fields")
check(sent.input.to_json().search("\"token\":")<0 && sent.input.to_json().search("\"connection\":")<0,"no credentials")
check(ai_plan!=nil && ai_text=="AI 挑礼方案 · 尚未下单","output accepted")
check(sent.class=="fast" && sent.schema.required[0]=="recommendations","host contract")
fail_path="/friends";ask_gift_ideas();check(model_calls==1 && ai_plan==nil && !ai_busy,"friends failure no inference")
fail_path="/catalog?limit=50";ask_gift_ideas();check(model_calls==1 && !ai_busy,"catalog failure no inference")
fail_path="";model_error="no_provider: No usable provider";ask_gift_ideas();check(ai_text.search("AI providers")>=0 && ai_plan==nil,"missing provider actionable")
model_error="provider: network failed";ask_gift_ideas();check(ai_text.search("密钥")>=0 && ai_plan==nil,"provider error actionable")
model_error="";malformed=true;ask_gift_ideas();check(ai_plan==nil,"unknown product refused")
malformed=false;delayed=true;ask_gift_ideas();let calls=model_calls;ask_gift_ideas();check(model_calls==calls,"duplicate click no inference")
ai_context=ai_context+1;ai_busy=false;pending({is_ok:true,data:{output:{recommendations:[]}}});check(ai_plan==nil,"stale callback ignored")
delayed=false;changed=true;ask_gift_ideas();check(ai_plan==nil,"account change ignored");changed=false;ai_busy=false
let before=model_calls;demo_mode=true;ask_gift_ideas();check(model_calls==before && ai_text.search("非实时 AI")>=0,"demo no model request")
check(gift_ai_error("rate: limited").search("频繁")>=0 && gift_ai_error("budget: spent").search("额度")>=0,"quota errors")
View{width: Fill height: Fill Label{text:"REAL_AI_FLOW_CHECKS="+checks+";FAILURES="+failures}}
'''
folder=root/'build/real-ai-flow-check';folder.mkdir(parents=True,exist_ok=True)
(folder/'main.splash').write_text(fixture+'\n'+'\n'.join(function(n) for n in names)+'\n'+checks)
m=json.loads((root/'bundle/manifest.json').read_text());m.pop('integrity',None)
for field in ('requires','backend','host_api','storage'):m.pop(field,None)
m['capabilities']=['model'];m.pop('network',None);(folder/'manifest.json').write_text(json.dumps(m))
harness=Path(os.environ.get('OCTO',str(root.parent/'OctoScript-App-Design-Flow/tools/octo')))
port='8146'
subprocess.run([str(harness),'run',str(folder),'--port',port,'--detach','--app-data',str(root/'build/real-ai-flow-data')],check=True,capture_output=True)
try:
 result=''
 for _ in range(40):
  state=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'))
  result=next((n.get('t','') for n in state['s'] if n.get('ty')=='Label' and n.get('t','').startswith('REAL_AI_FLOW_CHECKS=')),'')
  if result:break
  time.sleep(.1)
 assert result and result.endswith('FAILURES='),result or 'No native result'
 print(result, 'data_source='+('real server PKCE capture' if capture_path else 'synthetic server data')+'; model=explicit synthetic adapter')
finally:
 urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
