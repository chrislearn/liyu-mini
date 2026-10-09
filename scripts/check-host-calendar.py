#!/usr/bin/env python3
"""Exercise real Splash calendar control flow with an explicit synthetic adapter.
No native service approval, OS calendar or provider credential is emulated.
"""
import json,os,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'bundle/main.splash').read_text()
functions=s[s.index('fn calendar_notice'):s.index('fn open_calendar_export')].replace('host.request(', 'fixture_request(')
fixture=r'''
let auth_generation=1
let device_calendar_generation=0
let contract_edit_id=503
let stage="contract_status"
let demo_mode=false
let notice=""
let device_calendar_busy=false
let device_calendars=[]
let device_calendar_handle="cal-one"
let device_calendar_name="Fixture"
let device_calendar_links={}
let contract_date_loading=false
let contract_schedule={}
let schedule={planned_on:"2028-02-29",title:"一起看电影",start_ms:1835395200000,end_ms:1835481600000}
let native_event=nil
let writes=0
let requests=0
let permission_calls=0
let unsupported=false
let denied=false
let consent=false
let uncertain=false
let truncated=false
let stale=false
fn refresh(){}
fn api_request(input,done){done({is_ok:true,data:{status:200,body:schedule}})}
fn fixture_request(method,args,done){
    requests=requests+1
    if method=="runtime.describe" {done({is_ok:true,data:{supported:!unsupported}});return}
    if method=="device_calendar.permission.status" {done({is_ok:true,data:{supported:true,app_consent:consent,os_permission:if consent {"granted"} else {"not_determined"}}});return}
    if method=="device_calendar.permission.request" {permission_calls=permission_calls+1;if !denied {consent=true};done({is_ok:!denied,error:"fixture denial",data:{}});return}
    if method=="device_calendar.calendars.list" {done({is_ok:true,data:{calendars:[{id:"c1",name:"Fixture",account_name:"Synthetic",writable:true}]}});return}
    if method=="device_calendar.events.list" {done({is_ok:true,data:{events:if native_event==nil {[]} else {[native_event]},truncated:truncated}});return}
    if method=="device_calendar.events.get" {done({is_ok:native_event!=nil,error:"fixture absent",data:native_event});return}
    if method=="device_calendar.events.create" || method=="device_calendar.events.update" {
        writes=writes+1;native_event=args.event;native_event += {id:"event-one",revision:"r"+writes}
        if stale {auth_generation=auth_generation+1;device_calendar_links={}}
        if uncertain {done({is_ok:false,error:"fixture unknown result",data:nil});return}
        done({is_ok:true,data:{event:native_event}});return
    }
    done({is_ok:false,error:"unknown fixture route",data:nil})
}
'''
checks=r'''
let checks=0
let failures=""
fn check(value,label){checks=checks+1;if !value {failures=failures+label+";"}}
unsupported=true;open_device_calendars();check(permission_calls==0 && !device_calendar_busy,"unsupported discovery fallback")
unsupported=false;denied=true;open_device_calendars();check(permission_calls==1 && device_calendars.len()==0 && writes==0,"permission denial no write")
denied=false;open_device_calendars();check(device_calendars.len()==1,"writable calendar list")
demo_mode=true;open_device_calendars();check(writes==0,"demo no calendar");demo_mode=false
schedule.planned_on="";sync_device_calendar();check(writes==0 && !device_calendar_busy,"unconfirmed no write")
schedule.planned_on="2028-02-29";schedule.start_ms=-1;sync_device_calendar();check(writes==0,"unsupported date no write");schedule.start_ms=1835395200000
uncertain=true;sync_device_calendar();check(writes==1 && device_calendar_links["503"].pending,"unknown save tracked")
uncertain=false;sync_device_calendar();check(writes==1 && !device_calendar_links["503"].pending,"retry recovers without duplicate")
sync_device_calendar();check(writes==1,"same event no second write")
schedule.planned_on="2028-03-01";schedule.start_ms=1835481600000;schedule.end_ms=1835568000000;sync_device_calendar();check(writes==2 && !device_calendar_links["503"].pending,"changed confirmed date update/readback")
native_event.revision="external";native_event.title="person edited";sync_device_calendar();check(writes==2,"external change no overwrite")
device_calendar_handle="other";sync_device_calendar();check(writes==2,"other calendar no duplicate")
device_calendar_handle="cal-one";device_calendar_links={};native_event=nil;truncated=true;sync_device_calendar();check(writes==2,"truncated lookup no create")
truncated=false;stale=true;sync_device_calendar();check(writes==3 && device_calendar_links.to_json()=="{}","account switch ignores old callback")
View{width:Fill height:Fill Label{text:"HOST_CALENDAR_CHECKS="+checks+";FAILURES="+failures}}
'''
f=root/'build/host-calendar-check';f.mkdir(parents=True,exist_ok=True)
(f/'main.splash').write_text(fixture+functions+checks)
m={'schema':1,'id':'liyu-calendar-fixture','name':'Calendar flow fixture','version':'0.0.1','capabilities':['storage']}
(f/'manifest.json').write_text(json.dumps(m))
h=root.parent/'OctoScript-App-Design-Flow/tools/octo';env=dict(os.environ);port='8150'
subprocess.run([str(h),'run',str(f),'--port',port,'--detach','--app-data',str(root/'build/host-calendar-check-data')],env=env,check=True,capture_output=True)
try:
 for _ in range(40):
  data=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/snap'));result=next((n.get('t','') for n in data['s'] if n.get('t','').startswith('HOST_CALENDAR_CHECKS=')), '')
  if result:break
  time.sleep(.1)
 assert result and result.endswith('FAILURES='),result or 'fixture did not render'
 print(result)
finally:urllib.request.urlopen('http://127.0.0.1:'+port+'/quit').read()
