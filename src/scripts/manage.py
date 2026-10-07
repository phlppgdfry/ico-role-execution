#!/usr/bin/env python3
"""Local operations CLI: explicit actions, generated secrets, no production targets."""
import argparse, collections, datetime, hashlib, json, os, pathlib, secrets, signal, subprocess, sys, time, urllib.request, urllib.error, uuid
ROOT=pathlib.Path(__file__).resolve().parents[2]; RUN=ROOT/'runtime'
def environment():
    env=os.environ.copy()
    if (RUN/'.env').exists():
        for line in (RUN/'.env').read_text().splitlines():
            if line and not line.startswith('#'):
                k,v=line.split('=',1); env.setdefault(k,v)
    return env
def initialize():
    RUN.mkdir(mode=0o700,exist_ok=True)
    if (RUN/'.env').exists(): return
    env={f'ROLEOS_{role}_TOKEN':secrets.token_urlsafe(32) for role in ['ALPHA','BETA','READER','OPERATOR','ADMIN']}
    env.update(ROLEOS_ACK_SECRET=secrets.token_urlsafe(32),ROLEOS_DB_URL=f'jdbc:h2:file:{RUN}/terminal;MODE=Oracle;DB_CLOSE_DELAY=-1',ROLEOS_ACK_URL='http://127.0.0.1:8091/ack',ROLEOS_PORT='8090')
    path=RUN/'.env'; path.write_text(''.join(f'{k}={v}\n' for k,v in env.items())); path.chmod(0o600)
def request(path,method='GET',body=None,role='ADMIN',base=None):
    env=environment(); base=base or env.get('ROLEOS_BASE_URL',f"http://127.0.0.1:{env.get('ROLEOS_PORT','8090')}")
    from urllib.parse import urlparse
    if urlparse(base).hostname not in ['127.0.0.1','localhost']:raise ValueError('CLI is restricted to a local lab host')
    headers={'Authorization':'Bearer '+env[f'ROLEOS_{role}_TOKEN'],'X-Correlation-ID':'cli-'+uuid.uuid4().hex}
    if body is not None:headers['Content-Type']='application/json'
    req=urllib.request.Request(base.rstrip('/')+path,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=5) as r: raw=r.read(); return r.status,json.loads(raw) if r.headers.get('Content-Type','').startswith('application/json') else raw.decode()
    except urllib.error.HTTPError as e:
        with e:
            raw=e.read()
            try:value=json.loads(raw)
            except ValueError:value=dict(error=f'HTTP_{e.code}',message='Non-JSON response from local runtime; inspect deployment/route',status=e.code)
            return e.code,value
def pid_running(name):
    path=RUN/f'{name}.pid'
    if not path.exists():return False
    pid=int(path.read_text()); result=subprocess.run(['ps','-p',str(pid),'-o','args='],capture_output=True,text=True)
    marker='roleos.LocalServer' if name=='app' else 'mock_partner.py'
    return result.returncode==0 and marker in result.stdout
def start():
    initialize()
    if pid_running('app'):raise RuntimeError('App is already running; use health or stop')
    if not (ROOT/'target/classes/roleos/LocalServer.class').exists():raise RuntimeError('Run mvn package first')
    env=environment()
    for name,command in [('partner',[sys.executable,str(ROOT/'src/scripts/mock_partner.py')]),('app',['java','-cp',str(ROOT/'target/classes')+os.pathsep+str(ROOT/'target/dependency/*'),'roleos.LocalServer'])]:
        if pid_running(name):continue
        with (RUN/f'{name}.log').open('a') as log:
            child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            (RUN/f'{name}.pid').write_text(str(child.pid))
    for _ in range(50):
        try:
            code,_=request('/health')
            if code==200: print('Local lab ready: http://127.0.0.1:'+env['ROLEOS_PORT']);return
        except (OSError,ValueError):pass
        time.sleep(.1)
    raise RuntimeError('Startup failed; inspect runtime/app.log and runtime/partner.log')
def stop():
    for name in ['app','partner']:
        if pid_running(name):os.kill(int((RUN/f'{name}.pid').read_text()),signal.SIGTERM)
    for _ in range(50):
        if not any(pid_running(n) for n in ['app','partner']):return
        time.sleep(.1)
    raise RuntimeError('Graceful stop did not complete; inspect owned processes. No forced kill performed.')
def demo_event(site='ZEE'):
    suffix=uuid.uuid4().hex[:16].upper();return dict(message_id='transport-'+suffix,event_key='arrival-'+suffix,partner_id='ALPHA',site_id=site,vin='D'+suffix,event_type='ARRIVAL',location='ZEE-A01' if site=='ZEE' else 'KAL-B01',event_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),expected_version=0)
def smoke():
    result=[]
    for site in ['ZEE','KAL']:
        event=demo_event(site); code,receipt=request('/api/messages','POST',event,'ALPHA');assert code==202,receipt
        duplicate_code,duplicate=request('/api/messages','POST',event,'ALPHA');assert duplicate_code==200 and duplicate['duplicate'],duplicate
        for _ in range(50):
            _,status=request('/api/messages/'+receipt['id'],role='ALPHA')
            if status['status']=='PROCESSED':break
            time.sleep(.1)
        assert status['status']=='PROCESSED',status
        result.append(dict(site=site,message_id=receipt['id'],vin=event['vin'],status=status['status'],duplicate_suppressed=True))
    code,diffs=request('/api/admin/diagnostics/reconciliation');assert code==200 and not diffs,diffs
    return dict(smoke='PASS',simulation=True,results=result)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['init','start','stop','health','smoke','demo','alerts','failed','reconcile','log-summary','request','release-manifest']);parser.add_argument('extra',nargs='*');args=parser.parse_args();os.chdir(ROOT)
    if args.command=='init':initialize();print('Generated local runtime/.env (0600); no secrets printed.');return
    if args.command=='start':start();return
    if args.command=='stop':stop();print('Owned lab processes stopped.');return
    if args.command in ['smoke','demo']:value=smoke()
    elif args.command=='log-summary':
        counter=collections.Counter();bad=0
        for line in (RUN/'app.log').read_text().splitlines():
            try:entry=json.loads(line);counter[entry.get('event','unknown')]+=1
            except json.JSONDecodeError:bad+=1
        value=dict(events=dict(counter),non_json_lines=bad)
    elif args.command=='release-manifest':
        artifact=ROOT/'target/terminal-flow.war';digest=hashlib.sha256(artifact.read_bytes()).hexdigest();rev=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip() or 'uncommitted-lab'
        source=hashlib.sha256()
        for file in sorted([ROOT/'pom.xml',*(ROOT/'src/main').rglob('*')]):
            if file.is_file():source.update(str(file.relative_to(ROOT)).encode()+b'\0'+file.read_bytes())
        dirty=bool(subprocess.run(['git','status','--porcelain','--','src/main','pom.xml'],capture_output=True,text=True).stdout.strip())
        value=dict(release='1.4.0',artifact='terminal-flow.war',sha256=digest,bytes=artifact.stat().st_size,revision=rev,source_sha256=source.hexdigest(),source_git_dirty=dirty,mapping_versions=['1','2'],schema_versions=[1,2],simulation=True)
        (RUN/'release-manifest.json').write_text(json.dumps(value,indent=2)+'\n')
    else:
        if args.command=='request':
            if len(args.extra)<3:raise ValueError('request ROLE METHOD /path [JSON]')
            code,value=request(args.extra[2],args.extra[1],json.loads(args.extra[3]) if len(args.extra)>3 else None,args.extra[0])
        else:
            path={'health':'/health','alerts':'/api/metrics','failed':'/api/admin/diagnostics/failed-messages','reconcile':'/api/admin/diagnostics/reconciliation'}[args.command];code,value=request(path)
        if code>=400:print(json.dumps(value,indent=2));sys.exit(1)
        if args.command=='alerts':
            config=json.loads((ROOT/'monitoring/alerts/thresholds.json').read_text()); value=dict(metrics=value,active_alerts=[a for a in config if isinstance(value.get(a['metric']), (int,float)) and value[a['metric']]>=a['threshold']]);print(json.dumps(value,indent=2));sys.exit(2 if value['active_alerts'] else 0)
        if args.command=='reconcile' and value:print(json.dumps(value,indent=2));sys.exit(2)
    print(json.dumps(value,indent=2,ensure_ascii=False))
if __name__=='__main__':
    try:main()
    except (RuntimeError,ValueError,AssertionError,OSError) as e:print(f'Lab command failed: {e}',file=sys.stderr);sys.exit(1)
