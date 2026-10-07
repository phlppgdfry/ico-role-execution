"""Best-effort graceful shutdown of only processes created by this lab."""
import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
for path,args in [('deployment/scripts/wildfly_lab.py',['stop']),('src/scripts/manage.py',['stop'])]:
    result=subprocess.run([sys.executable,path]+args,cwd=ROOT)
    if result.returncode:print('Graceful cleanup reported a problem; inspect owned runtime.',file=sys.stderr)
