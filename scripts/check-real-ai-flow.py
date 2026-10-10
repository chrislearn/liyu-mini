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
names=['budget_cents','gift_ideas_input','gift_model_input','review_gift_ideas','cancel_gift_review','confirm_gift_review','valid_gift_result','valid_gift_plan','gift_ai_error','ask_gift_ideas','generate_gift_ideas','adopt_gift_idea']
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
let ai_share_relationship=false
let ai_share_note=false
let ai_review_generation=-1
let ai_review_snapshot=""
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
let model_output=nil
let draft_calls=0
let draft_recipient_ids=[]
let draft_message=""
fn begin(kind,index){draft_calls=draft_calls+1}
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
 if model_output!=nil {done({is_ok:true,data:{output:model_output}});return}
 let id=if malformed {999999} else {args.input.products[0].product_id}
 done({is_ok:true,data:{output:{status:"matched",no_match_reason:"",recommendations:[{product_id:id,reason:"测试适合原因",buying_tip:"测试核对规格",message:"测试寄语"}]}}})
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
check(backend_calls==2 && model_calls==0 && stage=="ai_review","fresh data preview before inference")
check(gift_ideas_input().note==server.friends.body[0].note,"preview uses refreshed server details")
let default_payload=gift_model_input(gift_ideas_input()).to_json()
for field in ["recipient_id","birthday","wedding_date","relationship","note","phone","email","display_name"] {check(default_payload.search("\""+field+"\":")<0,"default excludes "+field)}
cancel_gift_review();check(model_calls==0 && stage=="contact_detail","cancel zero inference")
ask_gift_ideas();confirm_gift_review()
check(model_calls==1 && ai_plan_friend==contact_id,"local recipient binding retained")
check(sent.input.to_json()==default_payload,"exact preview payload sent")
check(sent.input.budget_cents==10000 && sent.input.occasion==ai_occasion,"user preferences forwarded")
check(sent.input.products.len()>0 && sent.input.products.len()<=50,"bounded server catalog")
check(sent.input.to_json().search("\"phone\":")<0 && sent.input.to_json().search("\"email\":")<0 && sent.input.to_json().search("\"display_name\":")<0,"no contact fields")
check(sent.input.to_json().search("\"token\":")<0 && sent.input.to_json().search("\"connection\":")<0,"no credentials")
check(ai_plan!=nil && ai_text=="AI 挑礼方案 · 尚未下单","output accepted")
check(sent.class=="fast" && sent.schema.required[0]=="recommendations","host contract")
// Empty result is an explicit outcome, never an adoptable draft.
let candidate=ai_plan.recommendations[0]
let matched_plan=ai_plan.to_json().parse_json()
let input=gift_ideas_input()
let no_match={status:"no_match",no_match_reason:"预算内只有奶茶，不符合只要咖啡的条件。",recommendations:[]}
check(valid_gift_result(no_match,input) && !valid_gift_plan(no_match,input),"no match valid result but not plan")
for result in [
 {status:"matched",no_match_reason:"",recommendations:[]},
 {status:"no_match",no_match_reason:"",recommendations:[]},
 {status:"no_match",no_match_reason:"   ",recommendations:[]},
 {status:"no_match",no_match_reason:"不匹配",recommendations:[candidate]},
 {status:"matched",no_match_reason:"不匹配",recommendations:[candidate]},
 {status:"unexpected",no_match_reason:"",recommendations:[candidate]},
 {recommendations:[candidate]}
] {check(!valid_gift_result(result,input),"contradictory or legacy result rejected")}
model_output=no_match;ask_gift_ideas();confirm_gift_review()
check(ai_plan==nil && !ai_busy && ai_text.search("只要咖啡")>=0 && ai_text.search("未生成礼盒草稿")>=0,"no match rendered with reason")
let text=ai_text;adopt_gift_idea(candidate)
check(draft_calls==0 && ai_plan==nil,"no match cannot adopt old candidate")
model_output={status:"no_match",no_match_reason:"冲突",recommendations:[candidate]};ask_gift_ideas();confirm_gift_review()
check(ai_plan==nil && ai_text.search("可核验")>=0 && ai_text!=text,"contradictory result not shown as no match")
model_output=nil;ask_gift_ideas();confirm_gift_review()
check(ai_plan!=nil && ai_text=="AI 挑礼方案 · 尚未下单","matching result recovers after no match")
let counterfeit={product_id:candidate.product_id,reason:candidate.reason,buying_tip:candidate.buying_tip,message:"篡改寄语"}
adopt_gift_idea(counterfeit);check(draft_calls==0,"unreviewed recommendation refused")
adopt_gift_idea(ai_plan.recommendations[0]);check(draft_calls==1 && draft_recipient_ids[0]==contact_id,"matching recommendation can adopt")
// Delayed no-match from old conditions must not replace the latest state.
delayed=true;ask_gift_ideas();confirm_gift_review();ai_occasion="改变条件";pending({is_ok:true,data:{output:no_match}})
check(ai_plan==nil && ai_text.search("旧建议已丢弃")>=0,"stale no match ignored")
ai_occasion="生日，喜欢咖啡";delayed=false
let after_nomatch_calls=model_calls
fail_path="/friends";ask_gift_ideas();check(model_calls==after_nomatch_calls && ai_plan==nil && !ai_busy,"friends failure no inference")
fail_path="/catalog?limit=50";ask_gift_ideas();check(model_calls==after_nomatch_calls && !ai_busy,"catalog failure no inference")
fail_path="";model_error="no_provider: No usable provider";ask_gift_ideas();confirm_gift_review();check(ai_text.search("AI providers")>=0 && ai_plan==nil,"missing provider actionable")
model_error="provider: network failed";ask_gift_ideas();confirm_gift_review();check(ai_text.search("密钥")>=0 && ai_plan==nil,"provider error actionable")
model_error="";malformed=true;ask_gift_ideas();confirm_gift_review();check(ai_plan==nil,"unknown product refused")
malformed=false;delayed=true;ask_gift_ideas();confirm_gift_review();let calls=model_calls;ask_gift_ideas();check(model_calls==calls,"duplicate click no inference")
ai_context=ai_context+1;ai_busy=false;pending({is_ok:true,data:{output:{status:"matched",no_match_reason:"",recommendations:[]}}});check(ai_plan==nil,"stale callback ignored")
delayed=false;changed=true;ask_gift_ideas();confirm_gift_review();check(ai_plan==nil,"account change ignored");changed=false;ai_busy=false
let before=model_calls;demo_mode=true;ask_gift_ideas();confirm_gift_review();check(model_calls==before && ai_text.search("非实时 AI")>=0,"demo no model request")
demo_mode=false;ai_busy=false;stage="contact_detail";ask_gift_ideas()
ai_share_relationship=true;ai_share_note=true
let optin=gift_model_input(gift_ideas_input())
let optin_before=model_calls;confirm_gift_review()
check(sent.input.to_json()==optin.to_json() && model_calls==optin_before+1,"explicit optional fields match preview")
check(sent.input.relationship==server.friends.body[0].relationship && sent.input.note==server.friends.body[0].note,"optional server fields")
check(sent.input.to_json().search("\"recipient_id\":")<0 && sent.input.to_json().search("\"birthday\":")<0,"optin still excludes id and dates")
ask_gift_ideas();let stale_before=model_calls;ai_occasion="条件已变";confirm_gift_review()
check(model_calls==stale_before && stage=="contact_detail","stale preview refuses sending")
ask_gift_ideas();auth_generation=auth_generation+1;confirm_gift_review()
check(model_calls==stale_before,"account generation change refuses confirmation")
ask_gift_ideas();auth_state="signed_out";confirm_gift_review()
check(model_calls==stale_before,"expired auth refuses preview confirmation")
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
