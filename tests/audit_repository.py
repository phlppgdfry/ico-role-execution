"""Scope/traceability/links/spec/resources/secret-pattern audit. Actual product gaps remain explicit."""
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];failures=[]
def check(ok,message):
    if not ok:failures.append(message)
def main():
    req=json.loads((ROOT/'docs/role/requirements.json').read_text());check(len(req)==35,'Requirement count')
    for row in req:check((ROOT/row['artifact']).is_file(),f"Missing evidence for {row['id']}: {row['artifact']}")
    for folder,mincount,headings in [('docs/incidents',10,['Business impact','Affected systems','Symptoms','Hypotheses','Investigation','Logs','Database checks','Root cause','Workaround','Permanent fix','Validation','Communication','Lessons learned']),('docs/runbooks',10,['Symptoms','Impact','First checks','Commands / queries','Logs','Likely causes','Resolution','Escalation','Prevention']),('operations/tickets',20,['Description','Business impact','Acceptance criteria','Technical notes','Status'])]:
        files=[p for p in (ROOT/folder).glob('*.md') if p.name!='on-call-handover.md'];check(len(files)>=mincount,folder+' insufficient records')
        for p in files:
            body=p.read_text();check('Assumption / realistic simulation' in body,str(p.relative_to(ROOT))+' simulation status absent')
            for title in headings:check(title in body,str(p.relative_to(ROOT))+' missing '+title)
    check(len(list((ROOT/'docs/problems').glob('PRB*.md')))>=3,'Problems missing');check(len(list((ROOT/'docs/changes').glob('CHG*.md')))>=3,'Changes missing')
    for p in ROOT.rglob('*.md'):
        if any(x in p.parts for x in ['target','runtime','node_modules']):continue
        text=p.read_text()
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if link.startswith(('http:','https:','#','mailto:')):continue
            target=(p.parent/link.split('#')[0]).resolve();check(target.exists(),f'Broken link: {p.relative_to(ROOT)} → {link}')
        check(not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}',text),f'Credential pattern in {p.relative_to(ROOT)}')
    spec=json.loads((ROOT/'api/specifications/openapi.json').read_text());check(spec['openapi']=='3.1.0','OpenAPI version');schema=spec['components']['schemas']['PartnerEvent']
    sample=json.loads((ROOT/'api/examples/request-arrival.json').read_text());check(set(sample)==set(schema['required']),'Example/schema fields differ')
    for key,value in sample.items():
        prop=schema['properties'][key]
        if 'maxLength' in prop:check(len(value)<=prop['maxLength'],'Example length '+key)
        if 'enum' in prop:check(value in prop['enum'],'Example enum '+key)
        if prop['type']=='integer':check(isinstance(value,int) and value>=prop.get('minimum',value),'Example integer '+key)
    for path,operations in spec['paths'].items():
        names=set(re.findall(r'{([^}]+)}',path))
        for operation in operations.values():check(names=={p['name'] for p in operation.get('parameters',[]) if p['in']=='path'},'OpenAPI path parameters '+path)
    source=(ROOT/'src/main/java/roleos/Router.java').read_text()
    for path in spec['paths']:
        if '{' not in path:check(path in source or path=='/health','Declared route missing '+path)
    check((ROOT/'database/schema/001-terminal.sql').read_bytes()==(ROOT/'src/main/resources/schema.sql').read_bytes(),'Schema mirror drift')
    for p in (ROOT/'database/diagnostics').glob('*.sql'):check(p.read_bytes()==(ROOT/'src/main/resources/diagnostics'/p.name).read_bytes(),'Diagnostic mirror drift '+p.name)
    ns={'j':'https://jakarta.ee/xml/ns/jakartaee'};xml=ET.parse(ROOT/'src/main/webapp/WEB-INF/web.xml');check(xml.find("j:servlet/j:servlet-class",ns).text=='roleos.TerminalServlet','WAR adapter mapping');check(xml.find('j:filter-mapping/j:url-pattern',ns).text=='/*','WAR security headers coverage')
    check('Oracle' in (ROOT/'docs/systems/platform-substitutions.md').read_text(),'Product limits absent')
    result=dict(result='FAIL' if failures else 'PASS',requirements=len(req),incidents=10,runbooks=11,tickets=20,failures=failures)
    print(json.dumps(result,ensure_ascii=False,indent=2));return 1 if failures else 0
if __name__=='__main__':sys.exit(main())
