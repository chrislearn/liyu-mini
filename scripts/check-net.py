#!/usr/bin/env python3
"""Verify the actual app transport using only the standard net capability."""
import json,os,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'bundle/main.splash').read_text();api=s[s.index('fn api_request('):s.index('fn flush_revocations(')]
f=root/'build/net-proof';f.mkdir(parents=True,exist_ok=True)
origin=s.split('let service_origin = ',1)[1].split('\n',1)[0]
(f/'main.splash').write_text('let service_origin='+origin+'\nlet demo_mode=false\nlet session_token=""\nfn demo_request(r){return nil}\nlet result="pending"\n'+api+'''
start_timeout(0.1, || api_request({path:"/catalog"}, fn(r){if r.is_ok {result="NET_STATUS="+r.data.status+";PRODUCTS="+r.data.body.items.len()} else {result=r.error};ui.content.render()}))
View{width:Fill height:Fill flow:Down content:=View{width:Fill height:Fill on_render:||{Label{width:Fill height:Fit text:result draw_text.color:#x111111 draw_text.text_style.font_size:20}}}}
''')
m=json.loads((root/'bundle/manifest.json').read_text());m.pop('integrity',None);m['capabilities']=['net'];(f/'manifest.json').write_text(json.dumps(m))
env = dict(os.environ)
# Respect configured runtime paths; otherwise let the harness discover releases.
for key, binary in [('OCTO_HUB', 'hub'), ('OCTO_CARD_HOST', 'card-host')]:
 candidate = root.parent / 'OctoSense-App-Hub/target/debug' / binary
 if key not in env and candidate.is_file():
  env[key] = str(candidate)
h=root.parent/'OctoScript-App-Design-Flow/tools/octo'
subprocess.run([str(h),'run',str(f),'--port','8144','--detach'],env=env,check=True,capture_output=True)
try:
 for _ in range(50):
  data=json.load(urllib.request.urlopen('http://127.0.0.1:8144/snap'));labels=[n.get('t','') for n in data['s'] if n.get('ty')=='Label']
  if any('NET_STATUS=' in l for l in labels):break
  time.sleep(.2)
 print(labels)
 assert any('NET_STATUS=200' in l for l in labels)
 subprocess.run([str(h),'shot','8144',str(root/'build/net-proof.png')],env=env,check=True,capture_output=True)
finally:urllib.request.urlopen('http://127.0.0.1:8144/quit').read()
