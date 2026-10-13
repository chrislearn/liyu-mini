#!/usr/bin/env python3
"""Live host-model + actual catalog HTTP probe; no provider keys or business writes.

prepare extracts current production functions. bridge accepts only fixed local GETs.
assess checks semantic expectations independently of the model's own verdict.
See docs/ai-quality.md for fixture admission and disposable database setup.
"""
import argparse
import hashlib
import json
import os
import re
from decimal import Decimal
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['floor_div', 'pad2', 'money', 'budget_cents', 'gift_ideas_input',
         'gift_model_input','gift_query_request', 'valid_gift_plan', 'gift_ai_error', 'generate_gift_ideas',
         'gift_query_identity', 'query_active', 'stop_gift_query',
         'valid_query_constraints', 'gift_constraint_schema', 'gift_step_schema',
         'gift_explicit_excluded_kinds','plan_gift_query', 'confirm_gift_constraints', 'start_alternative_search',
         'gift_condition_differences', 'product_meets_constraints',
         'applied_constraints_match', 'gift_query_model_products',
         'gift_current_query_history', 'gift_purchase_checklist', 'gift_recommendation_reason',
         'valid_gift_query_step', 'gift_query_step', 'execute_gift_search']


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prepare(args):
    source = (ROOT / 'bundle/main.splash').read_text()
    cases = json.loads((ROOT / 'verification/ai-quality-cases.json').read_text())
    if args.ids:
        cases = [c for c in cases if c['id'] in args.ids.split(',')]
    assert cases
    folder = args.output / 'live-bundle'
    folder.mkdir(parents=True, exist_ok=False)
    for name in ['assets', 'screenshots']:
        shutil.copytree(ROOT / 'bundle' / name, folder / name)
    listing = json.loads((ROOT / 'bundle/listing.json').read_text())
    listing['description'] = 'Development-only live AI quality fixture. Fictional inputs, actual local backend GETs and host model.complete. Existing screenshots describe LIYU, not this fixture. No login, orders or calendar writes.'
    write(folder / 'listing.json', listing)
    globals_ = source[source.index('let ai_text ='):source.index('let purchase_busy =')]
    fixture = 'let cases=' + json.dumps(json.dumps(cases, ensure_ascii=False), ensure_ascii=False) + '.parse_json()\n' + globals_ + '''
let friends=[{id:1,relationship:"",birthday:"",wedding_date:"",note:""}]
let products=[]
let contact_index=0
let stage="contact_detail"
let auth_state="signed_in"
let auth_generation=1
let demo_mode=false
let notice=""
let active=false
let index=0
let results=[]
let model_trace=[]
let request_index=0
fn refresh(){if active && stage=="contact_detail" && !ai_busy && ai_text!="" {finish_case()}}
fn finish_case(){
 active=false
 let differences=[];if ai_plan!=nil {for item in ai_plan.recommendations {for p in ai_seen_products {if p.id==item.product_id {differences.push({id:p.id,text:gift_condition_differences(p)})}}}}
 results.push({case:cases[index],constraints:ai_constraints,original_constraints:ai_original_constraints,alternative:ai_alternative_mode,exact_zero:ai_exact_zero,parsed:ai_constraint_plan,plan:ai_plan,text:ai_text,notice:notice,queries:ai_query_history,products:ai_seen_products,models:model_trace,differences:differences})
 fs.write("results.json",results.to_json());index=index+1
 if index<cases.len() {start_timeout(1.0,||{run_case()})}
}
fn model_adapter(method,args,done){
 start_timeout(16.0,||{host.request(method,args,fn(r){model_trace.push({request:args.to_json().parse_json(),response:r.to_json().parse_json()});fs.write("model-progress.json",model_trace.to_json());done(r)})})
}
fn api_request(args,done){
 request_index=request_index+1;let number=request_index
 fs.write("request-"+number+".json",{method:args.method,path:args.path,case_index:index,case_id:cases[index].id}.to_json());poll_response(number,done)
}
fn poll_response(number,done){
 let file="response-"+number+".json"
 if fs.exists(file) {done(fs.read(file).parse_json());return}
 start_timeout(0.1,||{poll_response(number,done)})
}
fn run_case(){
 stage="contact_detail";ai_busy=false;ai_plan=nil;ai_text="";notice="";model_trace=[];active=false
 ai_budget=cases[index].budget;ai_occasion=cases[index].occasion;ai_review_generation=auth_generation
 api_request({method:"GET",path:"/catalog/search-options"},fn(r){ai_search_options=r.data.body;active=true;generate_gift_ideas()})
}
'''
    if args.planner_only:
        fixture = fixture.replace('fn model_adapter(method,args,done){', 'fn model_adapter(method,args,done){\n if model_trace.len()>0 {ai_busy=false;ai_text="Live planning and literal exclusion guard verified; recommendation not executed";refresh();return}\n')
    for name in NAMES:
        start = source.index('fn ' + name + '(')
        end = source.index('\nfn ', start + 1)
        fixture += '\n' + source[start:end].replace('host.request(', 'model_adapter(') + '\n'
    fixture += '\nstart_timeout(2.0,||{run_case()})\nView{width:Fill height:Fill Label{text:"Live AI quality probe: fictional data; read-only catalog; no orders"}}\n'
    (folder / 'main.splash').write_text(fixture)
    manifest = json.loads((ROOT / 'bundle/manifest.json').read_text())
    manifest = {k: manifest[k] for k in ['schema', 'id', 'name', 'version']}
    manifest.update(capabilities=['model', 'storage'], integrity={'bundle_blake3': '0' * 64})
    write(folder / 'manifest.json', manifest)
    write(args.output / 'cases.json', cases)
    write(args.output / 'source.json', {
        'mini_version': manifest['version'],
        'mini_revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'main_splash_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'mode': 'planner-only' if args.planner_only else 'full-loop',
        'production_functions': NAMES,
        'scope': 'Real model and SQL; fictional authentication and file bridge replace host backend transport; no real-account GUI or business writes.'})
    subprocess.run([str(args.hub), 'stamp', str(folder)], check=True)


def bridge(args):
    url = urllib.parse.urlparse(args.server)
    if not (url.scheme == 'http' and url.hostname == '127.0.0.1' and url.path == '' and url.port and not url.username and not url.password and not url.query and not url.fragment):
        raise ValueError('Only a plain local IPv4 HTTP server URL is allowed')
    if not args.database or not args.database.startswith('liyu_ai_quality_'):
        raise ValueError('Only the dedicated disposable database is allowed')
    cases = json.loads((args.output / 'cases.json').read_text())
    app = args.output / 'live-apps/liyu-mini'
    trace_path = args.output / 'http-trace.json'
    trace = json.loads(trace_path.read_text()) if trace_path.exists() else []
    seen = {p.name.replace('response-', 'request-') for p in app.glob('response-*.json')}
    last = 0
    deadline = time.monotonic() + 3600
    local_http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    while time.monotonic() < deadline:
        for path in sorted(app.glob('request-*.json'), key=lambda p: int(p.stem.split('-')[1])):
            if path.name in seen:
                continue
            try:
                request = json.loads(path.read_text())
            except (ValueError, OSError):
                continue  # A host fs.write may still be replacing the file contents.
            route = request['path']
            if request['method'] != 'GET' or not (route == '/catalog/search-options' or route.startswith('/catalog/search?')):
                raise ValueError('Fixture requested an unsupported HTTP operation')
            case = cases[request['case_index']]
            if request['case_id'] != case['id']:
                raise ValueError('Fixture case identity differs from the fixed matrix')
            if route == '/catalog/search-options':
                profile = cases[request['case_index']].get('profile', 'default')
                sql = 'UPDATE catalog SET stock=100,is_active=true; UPDATE catalog SET stock=0 WHERE id=900; UPDATE catalog SET is_active=false WHERE id=901;'
                if profile == 'stock-zero':
                    sql += 'UPDATE catalog SET stock=0;'
                elif profile == 'empty':
                    sql += 'UPDATE catalog SET is_active=false;'
                subprocess.run(['psql', '-X', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-p', str(args.pg_port), '-d', args.database, '-c', sql], check=True, capture_output=True)
                raw = subprocess.check_output(['psql', '-X', '-At', '-h', '127.0.0.1', '-p', str(args.pg_port), '-d', args.database, '-c', "SELECT COALESCE(json_agg(c ORDER BY id),'[]') FROM catalog c"], text=True)
                write(args.output / ('catalog-' + request['case_id'] + '.json'), json.loads(raw))
            try:
                try:
                    response = local_http.open(args.server + '/api/v1' + route, timeout=20)
                except urllib.error.HTTPError as error:
                    response = error
                status, body = response.status, json.load(response)
                output = {'is_ok': True, 'data': {'status': status, 'body': body}}
            except Exception as error:
                output = {'is_ok': False, 'error': str(error)}
            trace.append({'request': request, 'response': output})
            target = path.with_name(path.name.replace('request-', 'response-'))
            tmp = target.with_suffix('.tmp')
            write(tmp, output)
            tmp.replace(target)
            seen.add(path.name)
            write(args.output / 'http-trace.json', trace)
        result_path = app / 'results.json'
        if result_path.exists():
            try:
                results = json.loads(result_path.read_text())
            except (ValueError, OSError):
                time.sleep(.1)
                continue
            if len(results) > last:
                for result in results[last:]:
                    print(result['case']['id'] + ': ' + result['text'][:110], flush=True)
                last = len(results)
                assess(args)
            if last == len(cases):
                return
        time.sleep(.1)
    raise RuntimeError('Live probe exceeded one hour; preserve partial evidence')


def host(args):
    receipt = json.loads((args.output / 'live-receipt.json').read_text())
    assert all(app['signed_install'] and app['prepared_launch_verified'] for app in receipt['apps'])
    env = os.environ.copy()
    env.update(OCTOSENSE_APP_DATA=str(args.output / 'live-apps'),
               OCTOSENSE_HUB=str(args.output / 'live-apps'),
               OCTOSENSE_HUB_ANCHOR=receipt['anchor'],
               OCTOSENSE_HOME=str(args.home), OCTOSENSE_HUB_CATALOG='legacy',
               MAKEPAD_HIDE_WINDOWS='1')
    with (args.output / 'ai-host.log').open('w') as log:
        child = subprocess.Popen([str(args.host), '--test-action', 'launch-hub:liyu-mini', '--remote'], env=env, stdout=log, stderr=log)
        write(args.output / 'host-process.json', {'pid': child.pid, 'host_binary_sha256': hashlib.sha256(args.host.read_bytes()).hexdigest()})
        try:
            expected = len(json.loads((args.output / 'cases.json').read_text()))
            deadline = time.monotonic() + 3600
            while child.poll() is None and time.monotonic() < deadline:
                result = args.output / 'live-apps/liyu-mini/results.json'
                try:
                    if result.exists() and len(json.loads(result.read_text())) == expected:
                        break
                except (ValueError, OSError):
                    pass
                time.sleep(.5)
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)


def assess(args):
    results = json.loads((args.output / 'live-apps/liyu-mini/results.json').read_text())
    source_info = json.loads((args.output / 'source.json').read_text())
    planner_only = source_info.get('mode') == 'planner-only'
    expectations = {c['id']: c['expect'] for c in json.loads((ROOT / 'verification/ai-quality-cases.json').read_text())}
    report = []
    trace_path = args.output / 'http-trace.json'
    trace = json.loads(trace_path.read_text()) if trace_path.exists() else []
    for result in results:
        expect = expectations[result['case']['id']]
        errors, warnings = [], []
        original = result.get('original_constraints') or {}
        plan = result.get('plan')
        parsed = result.get('parsed') or {}
        recommendations = (plan or {}).get('recommendations', [])
        products = {p['id']: p for p in result['products']}
        ids = [item['product_id'] for item in recommendations]
        budget = result['case']['budget'].split('.')
        expected_budget = int(budget[0]) * 100 + int((budget[1] if len(budget) > 1 else '').ljust(2, '0'))
        if original and original.get('max_price_cents') != expected_budget:
            errors.append('Application budget differs from user amount')
        actual = [t for t in trace if t['request']['case_id'] == result['case']['id'] and t['request']['path'].startswith('/catalog/search?')]
        snapshot_path = args.output / ('catalog-' + result['case']['id'] + '.json')
        if not snapshot_path.exists() and not result['case'].get('profile'):
            snapshot_path = args.output / 'catalog-default.json'
        snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else None
        if len(actual) != len(result['queries']):
            errors.append('Query history differs from actual HTTP requests')
        for query, event in zip(result['queries'], actual):
            response = event['response']
            if not response.get('is_ok') or response['data']['status'] != 200:
                errors.append('Catalog HTTP request failed')
                continue
            body = response['data']['body']
            constraints = json.loads(query['filter'])
            if snapshot is not None:
                eligible = [p for p in snapshot if p['is_active'] and p['stock'] > 0
                            and (not constraints['max_price_cents'] or p['price_cents'] <= constraints['max_price_cents'])
                            and (not constraints['allowed_kinds'] or p['kind'] in constraints['allowed_kinds'])
                            and p['kind'] not in constraints['excluded_kinds']
                            and (constraints['delivery'] == 'any' or p['physical'] == (constraints['delivery'] == 'physical'))]
                if len(eligible) != body['eligible_total']:
                    errors.append('Backend count differs from independent catalog snapshot')
            if query['eligible_total'] != body['eligible_total'] or query['returned_ids'] != [p['id'] for p in body['items']]:
                errors.append('Model-visible catalog count/items differ from actual backend')
            if query['match_mode'] == 'exact' and json.loads(query['filter']) != original:
                errors.append('Exact query silently changed locked conditions')
        if len(result['queries']) > 4 or len(result['models']) > 6:
            errors.append('Application exceeded query/model limits')
        if 'kind' in expect and original.get('allowed_kinds') != [expect['kind']]:
            errors.append('Hard kind was not preserved')
        if expect.get('allowed_empty') and original.get('allowed_kinds'):
            errors.append('Broad negative/soft preference was arbitrarily narrowed to a whitelist')
        for kind in expect.get('exclude', []):
            if kind not in original.get('excluded_kinds', []) and (not original.get('allowed_kinds') or kind in original['allowed_kinds']):
                errors.append('Excluded kind missing: ' + kind)
            if any(products[i]['kind'] == kind for i in ids):
                errors.append('Recommended excluded kind: ' + kind)
        if 'delivery' in expect and original.get('delivery') != expect['delivery']:
            errors.append('Delivery condition was not preserved')
        if expect.get('unverified') and not parsed.get('unverified_requirements'):
            errors.append('Unsupported hard requirement was silently dropped')
        for term in expect.get('unverified_terms', []):
            if term not in '\n'.join(parsed.get('unverified_requirements', [])):
                errors.append('Unverified requirement missing: ' + term)
        if planner_only:
            if plan is not None or result['queries'] or len(result['models']) != 1:
                errors.append('Planning-only probe executed unexpected recommendation or extra calls')
        elif expect.get('no_plan'):
            if plan is not None or not result['queries'] or not any(q['eligible_total'] == 0 for q in result['queries']):
                errors.append('No-stock/empty catalog did not produce verified empty outcome')
        elif plan is None:
            errors.append('No usable recommendation: ' + result['text'])
        else:
            if plan.get('match_quality') != expect.get('quality'):
                unverified = parsed.get('unverified_requirements', [])
                conservative = plan.get('match_quality') == 'alternative' and unverified and all(any(term in text for term in expect.get('allow_unverified_terms', [])) for text in unverified)
                if conservative:
                    warnings.append('Conservative alternative label for unsupported packaging requirement')
                else:
                    errors.append('Wrong exact/alternative label')
            if 'ids' in expect and set(ids) != set(expect['ids']):
                errors.append('Unexpected products: ' + str(ids))
            if 'includes' in expect and expect['includes'] not in ids:
                errors.append('Preferred eligible product was missed')
            if 'nearest' in expect and (not ids or ids[0] != expect['nearest']):
                warnings.append('Closest budget alternative was not ranked first')
            if 'preferred' in expect and not set(ids).intersection(expect['preferred']):
                warnings.append('Soft preference not represented')
            if expect.get('exact_zero') and not result['exact_zero']:
                errors.append('Missing backend exact-zero proof')
        for item in recommendations:
            p = products.get(item['product_id'])
            if not p or not p['available'] or p['stock'] <= 0:
                errors.append('Unknown, unavailable or out-of-stock recommendation')
            elif '不销售' in p.get('description', '') or '非卖品' in p.get('description', ''):
                errors.append('Recommended a product whose description conflicts with sale availability')
            elif plan.get('match_quality') == 'exact':
                if original.get('max_price_cents', 0) and p['price_cents'] > original['max_price_cents']:
                    errors.append('Exact recommendation exceeds budget')
                if original.get('delivery') == 'electronic' and p['physical'] or original.get('delivery') == 'physical' and not p['physical']:
                    errors.append('Exact recommendation violates delivery')
            if p:
                allowed_amounts = {p['price_cents'], original.get('max_price_cents', 0), abs(p['price_cents'] - original.get('max_price_cents', 0))}
                for amount, _, unit in re.findall(r'([0-9]+([.][0-9]+)?)\s*(元|分|块)', item['reason']):
                    cents = Decimal(amount) * (1 if unit == '分' else 100)
                    if cents not in allowed_amounts:
                        errors.append('Incorrect money/unit in recommendation reason: ' + amount + unit)
            claim = re.search(r'(?<!无法)(?<!不能)(?<!没有)(?<!不)(?<!未)(已付款|已购买|保证无糖|保证零咖啡因|免费退款)', item['reason'])
            if claim:
                errors.append('Unsupported execution or merchant claim')
        if plan is not None:
            for model in reversed(result['models']):
                output = model['response'].get('data', {}).get('output', {})
                if output.get('action') == 'recommend':
                    original_reasons = {item['product_id']: item['reason'] for item in output['recommendations']}
                    for item in recommendations:
                        if original_reasons.get(item['product_id']) != item['reason']:
                            warnings.append('Model monetary prose replaced by application-derived amount statement')
                    break
        if not all(m['response'].get('is_ok') for m in result['models']):
            errors.append('Model service/format failure')
        report.append({'id': result['case']['id'], 'passed': not errors, 'errors': errors, 'quality_notes': warnings, 'queries': len(result['queries']), 'model_calls': len(result['models']), 'recommended_ids': ids})
    expected = len(json.loads((args.output / 'cases.json').read_text()))
    summary = {'expected': expected, 'completed': len(report), 'passed': sum(r['passed'] for r in report), 'cases': report, 'source': source_info, 'scope': 'Planning-only; no fresh recommendation claim.' if planner_only else 'Independent deterministic semantic checks; qualitative reasons still require review. Live inference failures are retained, not retried silently.'}
    write(args.output / 'assessment.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'bridge', 'assess', 'host'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hub', type=Path)
    parser.add_argument('--ids')
    parser.add_argument('--planner-only', action='store_true', help='One real planning call per case; no query/recommendation inference')
    parser.add_argument('--server')
    parser.add_argument('--database')
    parser.add_argument('--pg-port', type=int, default=55440)
    parser.add_argument('--host', type=Path)
    parser.add_argument('--home', type=Path)
    args = parser.parse_args()
    outcome = {'prepare': prepare, 'bridge': bridge, 'assess': assess, 'host': host}[args.mode](args)
    if args.mode == 'assess':
        print(json.dumps({k: outcome[k] for k in ['expected', 'completed', 'passed']}))
        raise SystemExit(0 if outcome['passed'] == outcome['completed'] == outcome['expected'] else 1)
