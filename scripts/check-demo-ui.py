#!/usr/bin/env python3
"""Drive the full bundle in a fresh official host's 412x892 Android phone view.

Start an isolated installed app with --test-action phone:android and --remote=PORT,
leave it on the welcome page, then run this script. Only explicitly selected local
fictional demo data is used; no login, external model, native approval, calendar
write or payment is performed. Screenshots and per-action error checks are retained.
The caller owns starting/stopping the host. This is an optional GUI regression,
separate from the synthetic card-host tests used by CI.
"""
import argparse,json,urllib.request,urllib.parse,time
from pathlib import Path
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, required=True)
parser.add_argument('--output', type=Path, default=Path('build/demo-ui'))
args = parser.parse_args()
R = args.output.resolve()
R.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:' + str(args.port)
assert not (R/'actions.jsonl').exists(), 'Use a new output directory to avoid mixing runs'

def get(p):return urllib.request.urlopen(BASE+p,timeout=20).read()
def snap():return [x for x in json.loads(get('/snap')).get('s',[]) if x.get('ty') not in ('Splash','Root','Window') and x.get('t') and x.get('r',[0,0,0,0])[3]>5]
def labels():return [x.get('t') for x in snap()]
def errors():
 cursor=R/'log-cursor.txt';n=cursor.read_text() if cursor.exists() else '0';j=json.loads(get('/log?since='+n));cursor.write_text(str(j['n']));return [s for s in j.get('l',[]) if '[E]' in str(s) or 'script time budget exceeded' in str(s)]
def record(action):
 s=snap()
 # Native snapshots can catch the frame between clearing/rebuilding the tree.
 for _ in range(20):
  if any(x.get('t')=='本地演示 · 虚构数据，退出后重置' for x in s):break
  time.sleep(.1);s=snap()
 bad=errors()
 assert any(x.get('t')=='本地演示 · 虚构数据，退出后重置' for x in s), 'Local demo banner absent; stop'
 row=dict(action=action,labels=[x.get('t') for x in s],errors=bad,time=time.time())
 with (R/'actions.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 if bad:
  (R/('failure-'+str(int(time.time()))+'.png')).write_bytes(get('/g?raw=1'));raise AssertionError(bad)
 return s
def scroll(dy):get('/m?'+urllib.parse.urlencode(dict(k='scroll',x=210,y=530,dy=dy,wait=1)));time.sleep(.1)
def find(t,ty=None,index=0,bottom=False,search=True):
 def matches():return [x for x in snap() if (t==x.get('t')) and (ty is None or x.get('ty')==ty) and (not bottom or x['r'][1]>800)]
 m=matches()
 if not m and search:
  scroll(-4000);m=matches()
  for _ in range(14):
   if m:break
   scroll(210);m=matches()
 assert len(m)>index,('missing',t,labels());return m[index]
def point(x,y):get('/click?'+urllib.parse.urlencode(dict(x=x,y=y,wait=1)));time.sleep(.12)
def click(t,index=0,ty=None,bottom=False):
 m=find(t,ty,index,bottom);x,y,w,h=m['r'];point(x+w/2,y+h/2);return record('click '+t)
def nav(t):return click(t,bottom=True)
def back():
 j=json.loads(get('/snap'));m=[x for x in j['s'] if x.get('ty')=='Button' and not x.get('t') and x['r'][1]<165 and x['r'][0]<80]
 assert m,('no back control',[(x['i'],x['ty'],x.get('t'),x['r']) for x in j['s'] if x['r'][1]<165]);x,y,w,h=m[0]['r'];point(x+w/2,y+h/2);return record('back')
def expect(t):
 s=find(t);record('expect '+t);return s
def type_text(t,value,index=0):
 m=find(t,'TextInput',index);x,y,w,h=m['r']
 if y>470:
  scroll(y-350);m=find(t,'TextInput',index,search=False);x,y,w,h=m['r']
 point(x+w/2,y+h/2)
 get('/k?'+urllib.parse.urlencode(dict(k='press',c='KeyA',cmd=1,wait=1)))
 if value: get('/t?'+urllib.parse.urlencode(dict(t=value,wait=1)))
 else: get('/k?'+urllib.parse.urlencode(dict(k='press',c='Backspace',wait=1)))
 time.sleep(.1);point(385,590);s=record('type '+t+'='+value)
 if value and not any(x.get('ty')=='TextInput' and x.get('t')==value for x in s): find(value,'TextInput');s=record('input retained '+value)
 return s
def shot(name):(R/name).write_bytes(get('/g?raw=1'))

initial = json.loads(get('/snap'))
windows = [s for s in initial.get('s', []) if s.get('ty')=='Window']
assert any(s['r'][2:]==[412.0,892.0] for s in windows), 'Requires a 412x892 Android phone view'
assert '本地演示' in labels(), 'Requires a fresh welcome page; no active account is accepted'
click('本地演示');
nav('熟人');
click('林舟');
m=find('单件预算（元，可留空）','TextInput');
x,y,w,h=m['r'];
point(x+w/2,y+h/2)
for t in ['3','0']:get('/t?'+urllib.parse.urlencode(dict(t=t,wait=1)))
assert any(x.get('t')=='30' for x in snap());
record('budget separate keystrokes retained');
point(385,590);
click('预览 AI 挑礼请求');
expect('当前预算内没有可选商品，请调整预算或刷新商品目录。');
expect('预览 AI 挑礼请求')
type_text('30','35');
type_text('送礼场景与偏好，例如生日、喜欢咖啡','喜欢');
m=find('喜欢','TextInput');
x,y,w,h=m['r'];
point(x+w/2,y+h/2);
get('/t?'+urllib.parse.urlencode(dict(t='咖啡',wait=1)));
record('preference continues typing');
point(385,590);
expect('喜欢咖啡');
click('预览 AI 挑礼请求');
expect('AI 发送预览');
click('不发送关系 · 点击加入');
click('不发送备注 · 点击加入');
expect('将发送的完整备注：喜欢咖啡，周末一起打羽毛球。');
click('返回修改或取消');
click('预览 AI 挑礼请求');
click('生成本地演示建议');
expect('演示挑礼方案（非实时 AI）');
shot('fixed-ai-result.png');
type_text('35','50');
expect('预览 AI 挑礼请求');
click('采纳并设置礼盒');
expect('资料、预算或目录已变化，请重新生成建议。');
record('editing budget prevents stale adoption');
click('预览 AI 挑礼请求');
click('生成本地演示建议');
click('采纳并设置礼盒');
expect('设置礼盒');
expect('林舟');
click('去结算');
expect('确认订单');
click('返回修改礼盒');
click('直接打开');
click('去结算');
click('确认并测试支付');
time.sleep(1);
expect('1 个礼盒已保存并读回核验（本次演示）。');
print('AI preview, cancel, generate, continuous typing, stale adoption rejection, adoption and order passed')

nav('礼盒')
click('收到的')
click('文具盲盒')
click('打开礼盒')
type_text('输入问题答案','错误')
for _ in range(3):
 click('回答并拆盒');time.sleep(.2)
expect('还没猜中，可以继续猜。')
expect('送礼人待揭晓')
type_text('错误','蓝色')
click('回答并拆盒');time.sleep(.3)
expect('送礼人  陈晓')
click('发货给我')
expect('提交收货信息')
click('提交收货信息')
expect('请填写收货人、11 位手机号和完整地址。')
type_text('收货人','演示收件人')
type_text('手机号','123')
type_text('完整地址','演示路 15 号')
click('提交收货信息')
expect('请填写收货人、11 位手机号和完整地址。')
type_text('123','13800000000')
click('提交收货信息');time.sleep(.4)
expect('物流信息')
click('确认收货');time.sleep(.3)
expect('已确认收货')
shot('fixed-shipment-confirmed.png')
back()
click('文具盲盒')
expect('已确认收货')
nav('礼盒')
click('收到的')
click('星巴克中杯拿铁电子券')
click('打开礼盒')
click('AI 帮我分析线索')
type_text('猜猜送礼人姓名','错误')
for _ in range(3):
 click('回答并拆盒');time.sleep(.2)
type_text('错误','林舟')
click('回答并拆盒');time.sleep(.3)
expect('送礼人  林舟')
click('送给别人')
click('确认转赠')
expect('请选择一位熟人。')
click('周知夏')
click('回答问题')
click('确认转赠')
expect('请填写题目和答案。')
type_text('留一点提示或题目','喜欢的颜色？')
type_text('问题答案','蓝色')
click('确认转赠');time.sleep(.3)
expect('查看转赠礼盒')
click('查看转赠礼盒')
expect('送给 周知夏')
shot('fixed-transfer.png')
print('Question/guess retry, shipping validation, receipt persistence and transfer passed')


# Re-use the contact name helper after editing shipping recipient form state.
nav('我');click('关于礼遇');click('一句话开始')
type_text('例如：送林舟一份咖啡','送林舟一份咖啡')
click('生成待确认卡片');expect('林舟');expect('设置礼盒')
nav('约定');click('周末陪我看一场电影', index=0)
click('标记已兑现');expect('状态已改为“已兑现”。')
click('改为待兑现');expect('状态已改为“待兑现”。')
click('选择设备日历');expect('本地演示不会访问设备日历。')
click('导出到日历（.ics）');expect('请先由双方确认日期，再导出日历。')
type_text('YYYY-MM-DD；留空清除','2027-02-29')
click('提议日期 / 改期');expect('请输入有效日期 YYYY-MM-DD；留空表示提议清除日期。')
type_text('2027-02-29','2028-02-29')
click('提议日期 / 改期');expect('当前生效日期：尚未确认')
click('撤回我的日期提议');expect('日期提议已撤回，原生效日期保留。')
type_text('YYYY-MM-DD；留空清除','2028-02-29')
click('提议日期 / 改期');click('模拟对方确认（本地演示）')
expect('当前生效日期：2028-02-29')
click('重新读取日期');expect('当前生效日期：2028-02-29')
click('导出到日历（.ics）');expect('本地演示只模拟双方确认；日历导出需要真实账号。')
shot('fixed-contract-confirmed.png')
type_text('2028-02-29','2028-03-01')
click('提议日期 / 改期');expect('当前生效日期：2028-02-29')
click('模拟对方确认（本地演示）');expect('当前生效日期：2028-03-01')
type_text('2028-03-01','')
click('提议日期 / 改期');expect('当前生效日期：2028-03-01')
click('模拟对方确认（本地演示）');expect('当前生效日期：尚未确认')
click('重新读取日期');expect('当前生效日期：尚未确认')
records = [json.loads(line) for line in (R/'actions.jsonl').read_text().splitlines()]
report = {'host_mode':'official host; full bundle; local fictional demo',
          'actions':len(records), 'new_runtime_errors':sum(len(r['errors']) for r in records),
          'assertions':sum(r['action'].startswith('expect ') for r in records),
          'scope':['AI preview/adoption/order','continued typing and stale adoption',
                   'retry after three misses','shipping/receipt readback','transfer',
                   'recipient helper after shipping','agreement dates/calendar demo isolation']}
(R/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
