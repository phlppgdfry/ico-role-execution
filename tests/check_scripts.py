import json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];results=[]
for command in ['health','smoke','failed','reconcile','log-summary','release-manifest','alerts']:
    r=subprocess.run([sys.executable,'src/scripts/manage.py',command],cwd=ROOT,capture_output=True,text=True)
    allowed=[0,2] if command=='alerts' else [0]
    if r.returncode not in allowed:raise RuntimeError(f'{command} failed: {r.stderr} {r.stdout}')
    parsed=json.loads(r.stdout);results.append(dict(command=command,exit_code=r.returncode,valid_json=True))
print(json.dumps(dict(result='PASS',scripts=results),indent=2))
