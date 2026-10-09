#!/usr/bin/env python3
"""Install a checked copy into a NEW isolated native profile with ephemeral keys."""
import argparse,json,os,shlex,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--app-data',required=True,type=Path)
p.add_argument('--hub-root',type=Path,default=Path(os.environ.get('OCTOSENSE_APP_HUB',str(root.parent/'OctoSense-App-Hub'))))
p.add_argument('--origin')
p.add_argument('--configure-launch',action='store_true')
a=p.parse_args();profile=a.app_data.resolve();hub=a.hub_root.resolve()
if profile.exists() and any(profile.iterdir()):p.error('--app-data must be a new or empty isolated directory')
project=root/'build/native-installer';(project/'src').mkdir(parents=True,exist_ok=True)
shutil.copy(root/'scripts/native-install-fixture.rs',project/'src/main.rs')
manifest={'package':{'name':'liyu-native-fixture','version':'0.0.0','edition':'2021'}}
# JSON quoted strings are TOML basic strings here (filesystem paths only).
q=lambda value:json.dumps(str(value))
(project/'Cargo.toml').write_text('[package]\nname="liyu-native-fixture"\nversion="0.0.0"\nedition="2021"\n[dependencies]\n'+
 'octosense-app-hub={path='+q(hub/'crates/app-hub')+'}\n'+
 'octosense-app-policy={path='+q(hub/'crates/app-policy')+'}\nserde_json="1"\n'+
 '[patch.crates-io]\noctosense-app-contract={path='+q(hub/'crates/app-contract')+'}\n')
bundle=project/'bundle'
if bundle.exists():shutil.rmtree(bundle)
shutil.copytree(root/'bundle',bundle)
if a.origin:subprocess.run(['python3',str(root/'scripts/configure-backend.py'),a.origin,'--bundle',str(bundle)],check=True)
m=json.loads((bundle/'manifest.json').read_text());m.setdefault('integrity',{'bundle_blake3':'0'*64});(bundle/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
hub_bin=Path(os.environ.get('OCTO_HUB',str(hub/'target/debug/hub')))
subprocess.run([str(hub_bin),'stamp',str(bundle)],check=True)
subprocess.run([str(hub_bin),'check',str(bundle),'--allow-unsigned'],check=True)
target=Path(os.environ.get('CARGO_TARGET_DIR',str(project/'target'))).resolve()
subprocess.run(['cargo','build','--manifest-path',str(project/'Cargo.toml'),'--target-dir',str(target)],check=True)
receipt=json.loads(subprocess.check_output([str(target/'debug/liyu-native-fixture'),str(profile),str(bundle)],text=True))
if a.configure_launch:
 local=root/'.local-state';local.mkdir(exist_ok=True)
 settings={'OCTOSENSE_APP_DATA':str(profile),'OCTOSENSE_HUB':str(profile),'OCTOSENSE_HUB_ANCHOR':receipt['anchor'],'OCTOSENSE_HOME':str(profile.parent/'host-home')}
 (local/'runtime.env').write_text(''.join('export '+k+'='+shlex.quote(v)+'\n' for k,v in settings.items()))
print(json.dumps(receipt,indent=2))
