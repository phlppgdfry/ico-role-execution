#!/usr/bin/env python3
"""Pinned real application-server rehearsal. Does not touch any external production host."""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,signal,subprocess,sys,time,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2];RUN=ROOT/'runtime';VERSION='41.0.1.Final';DIGEST='cc88fdb81b94d225c0f8259adeb9cbcc57aa8195e4f94de8be9de2fc33a21539';ZIP=RUN/'wildfly-ee10.zip'
spec=importlib.util.spec_from_file_location('manage',ROOT/'src/scripts/manage.py');cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
def home():
    found=list((RUN/'wildfly').glob('wildfly*'))
    if len(found)!=1:raise RuntimeError('Run install first')
    return found[0]
def env():
    result=cli.environment();result['ROLEOS_DB_URL']=f'jdbc:h2:file:{RUN}/wildfly-db/terminal;MODE=Oracle;DB_CLOSE_DELAY=-1';result['JAVA_OPTS']='-Xms64m -Xmx384m -Djava.net.preferIPv4Stack=true';result['ROLEOS_BASE_URL']='http://127.0.0.1:8280/terminal-flow';return result
def install():
    cli.initialize();RUN.mkdir(exist_ok=True)
    if not ZIP.exists():urllib.request.urlretrieve(f'https://github.com/wildfly/wildfly/releases/download/{VERSION}/wildfly-ee-10-{VERSION}.zip',ZIP)
    if hashlib.sha256(ZIP.read_bytes()).hexdigest()!=DIGEST:raise RuntimeError('Official pinned SHA256 mismatch; extraction aborted')
    dest=RUN/'wildfly';dest.mkdir(exist_ok=True)
    if list(dest.glob('wildfly*')):print('Pinned server already installed');return
    with zipfile.ZipFile(ZIP) as archive:
        for info in archive.infolist():
            path=(dest/info.filename).resolve()
            if not path.is_relative_to(dest.resolve()):raise RuntimeError('Unsafe archive path')
        archive.extractall(dest)
        for info in archive.infolist():
            mode=(info.external_attr>>16)&0o777
            if mode and not info.is_dir():(dest/info.filename).chmod(mode)
    print('Official EE10 server extracted with verified SHA256.')
def running():
    path=RUN/'wildfly.pid'
    if not path.exists():return False
    args=subprocess.run(['ps','-p',path.read_text().strip(),'-o','args='],capture_output=True,text=True)
    return args.returncode==0 and ('jboss-modules' in args.stdout or 'standalone.sh' in args.stdout) and str(RUN/'wildfly') in args.stdout
def status_wait():
    for _ in range(180):
        try:
            code,_=cli.request('/health',base='http://127.0.0.1:8280/terminal-flow')
            if code==200:return
        except OSError:pass
        failed=home()/'standalone/deployments/terminal-flow.war.failed'
        if failed.exists():raise RuntimeError('Deployment failed; inspect server log and .failed marker (no secrets)')
        time.sleep(.2)
    raise RuntimeError('Timed out waiting for deployed application')
def start():
    if running():raise RuntimeError('WildFly lab is already running')
    if not cli.pid_running('partner'):raise RuntimeError('Start local lab/partner first, or run mock_partner with generated env')
    artifact=ROOT/'target/terminal-flow.war'
    if not artifact.exists():raise RuntimeError('Run mvn package first')
    target=home()/'standalone/deployments/terminal-flow.war';shutil.copy(artifact,target);(target.with_suffix('.war.dodeploy')).touch()
    with (RUN/'wildfly.log').open('a') as log:
        child=subprocess.Popen(['bash',str(home()/'bin/standalone.sh'),'-b','127.0.0.1','-bmanagement','127.0.0.1','-Djboss.socket.binding.port-offset=200','-Djboss.management.http.port=9995'],cwd=ROOT,env=env(),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (RUN/'wildfly.pid').write_text(str(child.pid));status_wait();print('Actual WAR ready: http://127.0.0.1:8280/terminal-flow/')
def stop():
    if not running():return
    # standalone.sh launches Java as a child; the isolated process group belongs to this lab.
    os.killpg(int((RUN/'wildfly.pid').read_text()),signal.SIGTERM)
    for _ in range(100):
        if not running():return
        time.sleep(.1)
    raise RuntimeError('Graceful WildFly shutdown did not complete')
def redeploy():
    if not running():raise RuntimeError('Start lab first')
    target=home()/'standalone/deployments/terminal-flow.war';deployed=target.with_suffix('.war.deployed')
    if not deployed.exists():raise RuntimeError('No deployed marker')
    deployed.unlink()
    for _ in range(100):
        if target.with_suffix('.war.undeployed').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Undeploy not confirmed; do not force another instance')
    shutil.copy(ROOT/'target/terminal-flow.war',target);target.with_suffix('.war.dodeploy').touch();status_wait();print('Actual WAR undeploy/redeploy passed; database survived and worker lifecycle restarted.')
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['install','start','test','redeploy','stop']);args=parser.parse_args();os.chdir(ROOT)
    if args.command=='test':subprocess.run([sys.executable,'-m','unittest','discover','-s','tests/acceptance','-v'],cwd=ROOT,env=env(),check=True)
    else:globals()[args.command]()
if __name__=='__main__':main()
