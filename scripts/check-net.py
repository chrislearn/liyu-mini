#!/usr/bin/env python3
"""Verify the real transport with a synthetic host adapter, never raw tokens."""
import json,os,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'bundle/main.splash').read_text()
api=s[s.index('fn api_request('):s.index('let appearance =')].replace('host.request(', 'fixture_backend_request(')
fixture=r'''
let demo_mode=false
let connection="opaque-host-handle"
let auth_generation=1
let last=nil
let method=""
let failure=false
let deferred=nil
let delay=false
let answers=0
let result=nil
fn demo_request(r){return {is_ok:true,data:{status:200,body:{demo:true}}}}
fn fixture_backend_request(name,args,done){
    method=name;last=args
    if delay {deferred=done;return}
    if failure {done({is_ok:false,error:"native review cancelled",data:nil});return}
    done({is_ok:true,data:{status:200,body:{ok:true}}})
}
fn receive(r){answers=answers+1;result=r}
'''
checks=r'''
let checks=0
let failures=""
fn check(value,label){checks=checks+1;if !value {failures=failures+label+";"}}
api_request({path:"/catalog?limit=50"},receive)
check(method=="auth.backend.request" && last.operation=="liyu.read" && last.query.path=="/catalog?limit=50","declared read")
check(last.connection==connection,"opaque connection")
api_request({method:"POST",path:"/orders",body:{items:[]},idempotency_key:"attempt-1",expected_total:3500},receive)
check(last.operation=="liyu.post" && last.body.path=="/orders","declared write")
check(last.body.idempotency_key=="attempt-1" && last.body.expected_total==3500,"quote and retry guard forwarded")
api_request({method:"PUT",path:"/me/profile",body:{}},receive);check(last.operation=="liyu.put","put mapping")
api_request({method:"PATCH",path:"/friends/1",body:{}},receive);check(last.operation=="liyu.patch","patch mapping")
api_request({method:"DELETE",path:"/me/addresses/1",body:{}},receive);check(last.operation=="liyu.delete","delete mapping")
api_request({method:"POST",path:"/browser-authorizations/abc/poll",body:{poll_key:"transaction-only"}},receive)
check(last.operation=="liyu.contact_status" && last.query.poll_key=="transaction-only","contact read is not repeated native write")
api_request({method:"POST",path:"/browser-authorizations/abc/poll?cancel=true",body:{poll_key:"transaction-only"}},receive)
check(last.operation=="liyu.post","contact cancellation remains reviewed")
failure=true;api_request({path:"/me"},receive);check(!result.is_ok && result.data.status==0,"cancel propagated no false success")
failure=false;delay=true;let before=answers;api_request({path:"/me"},receive);auth_generation=auth_generation+1;deferred({is_ok:true,data:{status:200,body:{wrong_account:true}}});check(answers==before,"stale account reply ignored")
View{width:Fill height:Fill Label{text:"HOST_TRANSPORT_CHECKS="+checks+";FAILURES="+failures}}
'''
f=root/'build/host-transport-check';f.mkdir(parents=True,exist_ok=True)
(f/'main.splash').write_text(fixture+api+checks)
(f/'manifest.json').write_text(json.dumps({'schema':1,'id':'liyu-transport-fixture','name':'Host transport fixture','version':'0.0.1','capabilities':[]}))
h=root.parent/'OctoScript-App-Design-Flow/tools/octo';port='8151';env=dict(os.environ)
subprocess.run([str(h),'run',str(f),'--port',port,'--detach','--app-data',str(root/'build/host-transport-check-data')],env=env,check=True,capture_output=True)
try:
 result=''
 for _ in range(40):
  data=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'));result=next((n.get('t','') for n in data['s'] if n.get('t','').startswith('HOST_TRANSPORT_CHECKS=')), '')
  if result:break
  time.sleep(.1)
 assert result and result.endswith('FAILURES='),result or 'transport fixture did not render'
 print(result)
finally:urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
