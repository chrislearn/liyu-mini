#!/usr/bin/env python3
"""Execute production AI planner/tool loop in Splash with explicit synthetic adapters.
This validates control flow, not real inference. Live inference is recorded separately.
"""
import json,os,subprocess,time,urllib.request
from pathlib import Path
r=Path(__file__).resolve().parents[1];s=(r/'bundle/main.splash').read_text()
def fn(name):
 a=s.index('fn '+name+'(');b=s.index('\nfn ',a+1);return s[a:b].replace('host.request(', 'model_adapter(')
names=['pad2','money','budget_cents','gift_ideas_input','gift_model_input','review_gift_ideas','cancel_gift_review','confirm_gift_review','valid_gift_result','valid_gift_plan','gift_ai_error','ask_gift_ideas','generate_gift_ideas','gift_query_identity','query_active','stop_gift_query','valid_query_constraints','gift_constraint_schema','gift_step_schema','plan_gift_query','confirm_gift_constraints','cancel_gift_constraints','start_alternative_search','gift_condition_differences','product_meets_constraints','applied_constraints_match','gift_query_model_products','gift_current_query_history','gift_purchase_checklist','valid_gift_query_step','gift_query_step','execute_gift_search','adopt_gift_idea','verify_and_adopt_query_idea']
seed=json.loads(json.loads(s.split('fn demo_seed(){ return ',1)[1].split('.parse_json()',1)[0].strip()))
globals=s[s.index('let ai_text ='):s.index('let purchase_busy =')]
fixture='let seed='+json.dumps(json.dumps(seed,ensure_ascii=False),ensure_ascii=False)+'.parse_json()\n'+globals+'''
let friends=seed.friends
let products=seed.products
let contact_index=0
let contact_id=friends[0].id
let stage="contact_detail"
let auth_state="signed_in"
let auth_generation=1
let demo_mode=false
let notice=""
let draft_recipient_ids=[]
let draft_message=""
let draft_calls=0
let query_calls=0
let backend_paths=[]
let model_calls=0
let sent=[]
let failure_path=""
let model_error=""
let delayed=false
let pending=nil
let changed=false
let source_friend=nil
let planner=nil
let steps=[]
let pages=[]
let api_index=0
let step_index=0
let coffee=seed.products[0]
let options={version:1,kinds:["咖啡","奶茶","电影票"],tool:{name:"catalog_search"}}
let candidate={product_id:coffee.id,reason:"符合硬条件",buying_tip:"核对有效期",message:"祝你开心"}
fn refresh(){}
fn start_timeout(seconds,done){}
fn begin(kind,index){draft_calls=draft_calls+1}
fn api_request(args,done){
 backend_paths.push(args.path)
 if args.path==failure_path {done({is_ok:true,data:{status:401,body:nil}});return}
 if args.path=="/friends" {done({is_ok:true,data:{status:200,body:[source_friend]}});return}
 if args.path=="/catalog/search-options" {done({is_ok:true,data:{status:200,body:options}});return}
 if args.path.search("/catalog/search?")==0 {query_calls=query_calls+1;let page=pages[api_index];api_index=api_index+1;done({is_ok:true,data:{status:200,body:page}});return}
 done({is_ok:true,data:{status:200,body:coffee}})
}
fn model_adapter(method,args,done){
 model_calls=model_calls+1;sent.push(args)
 if delayed {pending=done;return}
 if changed {auth_generation=auth_generation+1}
 if model_error!="" {done({is_ok:false,error:model_error});return}
 if args.schema.required[0]=="allowed_kinds" {done({is_ok:true,data:{output:planner}});return}
 let step=steps[step_index];step_index=step_index+1;done({is_ok:true,data:{output:step}})
}
fn search_step(q,cursor){return {action:"search",q:q,cursor:cursor,reason:"查询",recommendations:[]}}
fn recommend(){return {action:"recommend",q:"",cursor:-1,reason:"找到",recommendations:[candidate]}}
fn page(items,eligible,total,next,revision){return {items:items,eligible_total:eligible,total_matches:total,next_cursor:next,catalog_revision:revision,applied:{max_price_cents:3500,allowed_kinds:["咖啡"],excluded_kinds:["奶茶"],delivery:"any"}}}
fn reset(){
 ai_context=ai_context+1;auth_generation=1;auth_state="signed_in";stage="contact_detail";demo_mode=false;contact_index=0;friends=seed.friends.to_json().parse_json();products=seed.products.to_json().parse_json();source_friend=friends[0];contact_id=friends[0].id
 ai_budget="35";ai_occasion="只要咖啡，不要奶茶";ai_share_relationship=false;ai_share_note=false;ai_busy=false;ai_plan=nil;ai_constraints=nil;ai_search_options=nil;ai_query_history=[];ai_constraint_plan=nil;ai_text="";notice="";ai_locked_json="";ai_query_snapshot="";ai_plan_snapshot="";ai_plan_friend=-1
 query_calls=0;model_calls=0;draft_calls=0;backend_paths=[];sent=[];failure_path="";model_error="";delayed=false;changed=false;api_index=0;step_index=0
 planner={allowed_kinds:["咖啡"],excluded_kinds:["奶茶"],delivery:"any",summary:"只要咖啡，排除奶茶",unverified_requirements:[]}
 steps=[search_step("",-1),recommend()];pages=[page([coffee],1,1,nil,"r1")]
}
fn parse(){ask_gift_ideas();confirm_gift_review()}
fn run(){parse()}
'''
checks='''
let checks=0
let failures=""
fn check(value,label){checks=checks+1;if !value {failures=failures+label+";"}}
reset();ask_gift_ideas()
check(model_calls==0 && stage=="ai_review" && backend_paths.len()==2,"preview before model; reads friends and tool contract")
check(backend_paths[1]=="/catalog/search-options","does not preload arbitrary first catalog page")
cancel_gift_review();check(model_calls==0,"cancel preview zero models")
reset();parse();check(stage=="contact_detail" && ai_plan!=nil && query_calls==1,"automatic interpretation and query; no hard-condition confirmation")
for field in ["recipient_id","birthday","wedding_date","phone","email","display_name","relationship","note","token","connection"] {check(sent[0].input.to_json().search("\\\""+field+"\\\":")<0,"default excludes "+field)}
check(sent[0].input.search_options.tool.name=="catalog_search","only approved read tool description sent")
check(ai_plan!=nil && ai_search_round==1 && query_calls==1,"query then recommend")
check(ai_plan.recommendations[0].buying_tip.search("政策未核验")>=0,"purchase policy is never an AI assertion")
let longspec=coffee.to_json().parse_json();longspec.spec="";for i in 250 {longspec.spec=longspec.spec+"长"};check(gift_purchase_checklist(longspec).split("").len()<200,"long specs cannot break adoption result limits")
check(ai_constraints.max_price_cents==3500 && ai_constraints.allowed_kinds[0]=="咖啡","app locks budget and kinds")
check(sent[1].input.products.len()==0 && sent[2].input.products[0].product_id==coffee.id,"model receives actual returned products next round")
adopt_gift_idea(ai_plan.recommendations[0]);check(draft_calls==1 && draft_recipient_ids[0]==contact_id,"adoption rechecks backend detail")
reset();ask_gift_ideas();ai_share_note=true;ai_share_relationship=true;confirm_gift_review()
check(sent[0].input.note==source_friend.note && sent[0].input.relationship==source_friend.relationship,"optional fields explicitly shared")
reset();delayed=true;parse();ai_context=ai_context+1;pending({is_ok:true,data:{output:planner}});check(query_calls==0 && ai_plan==nil,"cancel during parsing no search")
reset();delayed=true;parse();ai_budget="30";pending({is_ok:true,data:{output:planner}});check(query_calls==0 && ai_plan==nil,"changed budget invalidates pending parsing")
reset();planner.unverified_requirements=["必须无糖，目录无成分信息"];parse();check(query_calls==1 && ai_plan.match_quality=="alternative" && ai_text.search("无法确认")>=0 && gift_condition_differences(coffee).search("无法核验")>=0,"unverifiable conditions produce explicitly uncertain alternatives")
reset();planner.allowed_kinds=["编造种类"];parse();check(ai_constraint_plan==nil && query_calls==0,"unknown kind refused")
reset();planner.excluded_kinds=["咖啡"];parse();check(ai_constraint_plan==nil,"contradictory constraints refused")
reset();planner.allowed_kinds=["咖啡","咖啡"];parse();check(ai_constraint_plan==nil,"duplicate kinds refused")
reset();let broad=page([coffee],1,1,nil,"r1");broad.applied={max_price_cents:0,allowed_kinds:[],excluded_kinds:[],delivery:"any"};steps=[search_step("",-1),search_step("",-1),recommend()];pages=[page([],0,0,nil,"r1"),broad];run();check(ai_plan!=nil && query_calls==2 && ai_exact_zero && ai_plan.match_quality=="alternative" && ai_text.search("没有找到完全符合")>=0,"full zero starts separately labelled alternative query")
check(sent[2].input.history.len()==0 && sent[2].input.eligible_total==-1 && sent[2].input.original_scope_empty,"alternative model sees only current-scope history")
check(ai_original_constraints.max_price_cents==3500 && ai_constraints.max_price_cents==0,"original conditions preserved when searching alternatives")
check(ai_query_history[0].filter!=ai_query_history[1].filter,"duplicate keywords permitted only in separate search scope")
let higher=coffee.to_json().parse_json();higher.price_cents=4500;higher.kind="奶茶";higher.physical=true;ai_original_constraints.delivery="electronic";check(gift_condition_differences(higher).search("超过预算")>=0 && gift_condition_differences(higher).search("排除")>=0 && gift_condition_differences(higher).search("配送")>=0,"alternative differences are computed from actual product fields")
reset();ai_budget="30";let exactempty=page([],0,0,nil,"r1");exactempty.applied.max_price_cents=3000;let nearby=page([coffee],1,1,nil,"r1");nearby.applied={max_price_cents:0,allowed_kinds:[],excluded_kinds:[],delivery:"any"};steps=[search_step("",-1),search_step("",-1),recommend()];pages=[exactempty,nearby];run();check(ai_plan!=nil && gift_condition_differences(coffee).search("超过预算")>=0,"over-budget alternative always labelled");adopt_gift_idea(ai_plan.recommendations[0]);check(draft_calls==1 && ai_budget=="30","explicit alternative adoption retains original budget and rechecks stock")
reset();let emptybroad=page([],0,0,nil,"r1");emptybroad.applied={max_price_cents:0,allowed_kinds:[],excluded_kinds:[],delivery:"any"};steps=[search_step("",-1),search_step("",-1)];pages=[page([],0,0,nil,"r1"),emptybroad];run();check(ai_plan==nil && query_calls==2 && ai_text.search("也没有")>=0,"empty entire in-stock catalog gives no alternatives")
reset();steps=[search_step("找不到的软品牌",-1),search_step("",-1),recommend()];pages=[page([],1,0,nil,"r1"),page([coffee],1,1,nil,"r1")];run()
check(ai_plan!=nil && query_calls==2 && ai_constraints.max_price_cents==3500,"soft refinement uses multiple rounds without loosening")
check(ai_query_history[0].eligible_total==1 && ai_query_history[0].total_matches==0,"soft emptiness not total emptiness")
reset();steps=[search_step("软品牌",-1),{action:"no_match",q:"",cursor:-1,reason:"关键词没有命中",recommendations:[]}];pages=[page([],1,0,nil,"r1")];run()
check(ai_plan==nil && ai_text.search("不能断言")>=0,"model no match cannot override positive eligible total")
reset();steps=[search_step("",-1),search_step("",-1)];run();check(query_calls==1 && ai_text.search("重复")>=0,"duplicate query refused")
reset();steps=[search_step("",999)];run();check(query_calls==0 && ai_text.search("游标")>=0,"invented cursor refused")
reset();steps=[search_step("",-1),search_step("咖啡",coffee.id)];pages=[page([coffee],2,2,""+coffee.id,"r1")];run();check(query_calls==1,"cursor bound to same query")
reset();steps=[search_step("",-1),search_step("",coffee.id),recommend()];pages=[page([coffee],1,1,""+coffee.id,"r1"),page([],1,1,nil,"r1")];run();check(ai_plan!=nil && query_calls==2,"known same-query pagination permitted")
reset();steps=[search_step("",-1),search_step("品牌",-1)];pages=[page([coffee],1,1,nil,"r1"),page([coffee],1,1,nil,"r2")];run();check(ai_plan==nil && ai_text.search("目录发生变化")>=0,"catalog revision change stops")
reset();pages[0].applied.max_price_cents=99900;run();check(ai_plan==nil && ai_text.search("硬条件不一致")>=0,"server widened budget refused")
reset();let expensive=coffee.to_json().parse_json();expensive.price_cents=3501;pages=[page([expensive],1,1,nil,"r1")];run();check(ai_plan==nil,"over budget returned row refused")
reset();let unavailable=coffee.to_json().parse_json();unavailable.stock=0;pages=[page([unavailable],1,1,nil,"r1")];run();check(ai_plan==nil,"stock zero refused")
reset();let tea=coffee.to_json().parse_json();tea.kind="奶茶";pages=[page([tea],1,1,nil,"r1")];run();check(ai_plan==nil,"wrong kind refused")
reset();pages[0].eligible_total=0;run();check(ai_plan==nil && ai_text.search("不一致")>=0,"false zero with rows refused")
reset();pages[0].next_cursor="999";run();check(ai_plan==nil,"invalid next cursor refused")
reset();steps=[search_step("a",-1),search_step("b",-1),search_step("c",-1),search_step("d",-1),search_step("e",-1)];pages=[page([],1,0,nil,"r1"),page([],1,0,nil,"r1"),page([],1,0,nil,"r1"),page([],1,0,nil,"r1")];run();check(query_calls==4 && ai_plan==nil && ai_text.search("不能判断")>=0,"bounded loops do not claim no match")
reset();steps=[search_step("a",-1),search_step("b",-1),search_step("c",-1),search_step("",-1),recommend()];pages=[page([],1,0,nil,"r1"),page([],1,0,nil,"r1"),page([],1,0,nil,"r1"),page([coffee],1,1,nil,"r1")];run();check(query_calls==4 && ai_plan!=nil,"can recommend after fourth query")
reset();steps=[{action:"recommend",q:"",cursor:-1,reason:"猜的",recommendations:[candidate]}];run();check(ai_plan==nil && query_calls==0,"no unqueried product recommendation")
reset();steps[1].recommendations[0].product_id=99999;run();check(ai_plan==nil,"invented recommendation refused");candidate.product_id=coffee.id
reset();run();coffee.stock=0;adopt_gift_idea(ai_plan.recommendations[0]);check(draft_calls==0 && ai_plan==nil,"stock lost before adoption refused");coffee.stock=100
reset();failure_path="/friends";ask_gift_ideas();check(model_calls==0 && !ai_busy,"friends failure prevents model")
reset();failure_path="/catalog/search-options";ask_gift_ideas();check(model_calls==0 && ai_text.search("升级")>=0,"old backend explicit unavailable")
reset();model_error="no_provider: missing";parse();check(ai_plan==nil && ai_text.search("AI providers")>=0,"provider error actionable")
reset();delayed=true;parse();ai_context=ai_context+1;pending({is_ok:true,data:{output:planner}});check(ai_constraint_plan==nil,"stale planner ignored")
reset();changed=true;parse();check(ai_constraint_plan==nil,"account generation change ignored")
reset();ask_gift_ideas();auth_state="signed_out";confirm_gift_review();check(model_calls==0,"signed out preview refused")
reset();ask_gift_ideas();ai_occasion="改变条件";confirm_gift_review();check(model_calls==0,"stale preview refused")
reset();demo_mode=true;ask_gift_ideas();confirm_gift_review();check(model_calls==0 && query_calls==0 && ai_text.search("非实时 AI")>=0,"demo stays local fixed example")
View{width:Fill height:Fill Label{text:"REAL_AI_FLOW_CHECKS="+checks+";FAILURES="+failures}}
'''
# Each fixture has its own normal host instruction budget; avoid aggregating dozens of flows into one VM tick.
marker='reset();pages=[page([],0,0,nil,"r1")];run()'
# Split at a top-level scenario boundary, preserving shared fixture setup.
marker='reset();let broad='
cut=checks.index(marker)
header=checks[:checks.index('reset();ask_gift_ideas()')]
view='View{width:Fill height:Fill Label{text:"REAL_AI_FLOW_CHECKS="+checks+";FAILURES="+failures}}'
parts=[checks[:cut]+view,header+checks[cut:]]
b=r/'build/real-ai-flow-check';b.mkdir(parents=True,exist_ok=True)
m=json.loads((r/'bundle/manifest.json').read_text());[m.pop(k,None) for k in ['integrity','requires','backend','host_api','storage','network']];m['capabilities']=['model'];(b/'manifest.json').write_text(json.dumps(m))
h=Path(os.environ.get('OCTO',str(r.parent/'OctoScript-App-Design-Flow/tools/octo')));port='8146'
for part in parts:
 (b/'main.splash').write_text(fixture+'\n'+'\n'.join(fn(n) for n in names)+'\n'+part)
 subprocess.run([str(h),'run',str(b),'--port',port,'--detach','--app-data',str(r/'build/real-ai-flow-data')],check=True,capture_output=True)
 try:
  result=''
  for _ in range(40):
   state=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'));result=next((n.get('t','') for n in state['s'] if n.get('ty')=='Label' and n.get('t','').startswith('REAL_AI_FLOW_CHECKS=')),'')
   if result:break
   time.sleep(.1)
  assert result and result.endswith('FAILURES='),result or 'No result; inspect build/real-ai-flow-data/card-host.log'
  print(result+'; model=explicit synthetic adapter')
 finally:
  try:urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
  except OSError:pass
