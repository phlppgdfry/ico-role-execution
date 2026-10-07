"""Same acceptance contract against fast adapter or actual deployed WAR. No test secrets logged."""
import importlib.util,json,os,pathlib,time,unittest,uuid
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('manage',ROOT/'src/scripts/manage.py');cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
class LiveContract(unittest.TestCase):
    def call(self,path,method='GET',body=None,role='ADMIN'):return cli.request(path,method,body,role)
    def controls(self,**values):code,value=self.call('/api/admin/controls','PATCH',values);self.assertEqual(code,200,value)
    def tearDown(self):self.controls(worker_paused=False,dependency_unavailable=False,ack_timeout=False,force_api_failure=False,mapping_version='1')
    def wait(self,id,status):
        for _ in range(100):
            code,value=self.call('/api/messages/'+id,role='ALPHA')
            if value.get('status')==status:return value
            time.sleep(.1)
        self.fail(f'No {status}: {value}')
    def test_01_health_headers_and_happy_path_both_sites(self):
        self.assertEqual(self.call('/health')[0],200)
        result=cli.smoke();self.assertEqual(result['smoke'],'PASS')
    def test_02_scope_duplicate_conflict_and_malformed(self):
        event=cli.demo_event();code,r=self.call('/api/messages','POST',event,'ALPHA');self.assertEqual(code,202)
        self.assertEqual(self.call('/api/messages/'+r['id'],role='BETA')[0],404)
        self.assertEqual(self.call('/api/messages','POST',event,'BETA')[0],403)
        event['message_id']='another-delivery';self.assertEqual(self.call('/api/messages','POST',event,'ALPHA')[0],200)
        event['location']='ZEE-A02';self.assertEqual(self.call('/api/messages','POST',event,'ALPHA')[0],409)
        event['event_key']='new-'+uuid.uuid4().hex;event['extra']=True;self.assertEqual(self.call('/api/messages','POST',event,'ALPHA')[0],400)
    def test_03_mapping_change_redrive_and_no_partial_commit(self):
        event=cli.demo_event();event['location']='ZEE-A-01';code,r=self.call('/api/messages','POST',event,'ALPHA');self.assertEqual(code,202);self.wait(r['id'],'REJECTED')
        self.controls(mapping_version='2');self.assertEqual(self.call('/api/messages/'+r['id']+'/redrive','POST',{'reason':'Acceptance CHG-003 mapping fix'})[0],200);self.wait(r['id'],'PROCESSED')
        self.assertEqual(self.call('/api/messages/'+r['id']+'/redrive','POST',{'reason':'Unsafe second replay'})[0],409)
    def test_04_pause_dependency_and_safe_recovery(self):
        self.controls(worker_paused=True);event=cli.demo_event();_,r=self.call('/api/messages','POST',event,'ALPHA');time.sleep(.4);self.assertEqual(self.call('/api/messages/'+r['id'],role='ALPHA')[1]['status'],'RECEIVED')
        self.controls(worker_paused=False,dependency_unavailable=True);self.wait(r['id'],'RETRY_WAIT');self.controls(dependency_unavailable=False);self.wait(r['id'],'PROCESSED')
    def test_05_portal_authorization_conflict_and_hold(self):
        event=cli.demo_event();_,r=self.call('/api/messages','POST',event,'ALPHA');self.wait(r['id'],'PROCESSED');path='/api/vehicles/'+event['vin']
        correction={'expected_version':1,'location':'ZEE-A02','reason':'Physical check in acceptance lab'}
        self.assertEqual(self.call(path+'/location','PUT',correction,'READER')[0],403);self.assertEqual(self.call(path+'/location','PUT',correction,'OPERATOR')[0],200);self.assertEqual(self.call(path+'/location','PUT',correction,'OPERATOR')[0],409)
        hold={'expected_version':2,'hold':True,'reason':'Await physical release'};self.assertEqual(self.call(path+'/hold','PUT',hold,'OPERATOR')[0],200)
        release={'expected_version':3,'hold':False,'reason':'Verified','decision_ref':'BUS-ACCEPT-01'};self.assertEqual(self.call(path+'/hold','PUT',release,'OPERATOR')[0],403);self.assertEqual(self.call(path+'/hold','PUT',release)[0],200)
    def test_06_api_unavailable_health_and_admin_recovery(self):
        self.controls(force_api_failure=True);self.assertEqual(self.call('/health')[0],503);self.assertEqual(self.call('/api/vehicles',role='READER')[0],503);self.controls(force_api_failure=False);self.assertEqual(self.call('/health')[0],200)
    def test_07_diagnostics_reporting_and_reconciliation(self):
        for name in ['failed-messages','duplicate-records','recent-errors','reconciliation','slow-query-plan','outbox-status']:
            code,value=self.call('/api/admin/diagnostics/'+name);self.assertEqual(code,200,(name,value))
        self.assertEqual(self.call('/api/admin/diagnostics/arbitrary-sql')[0],404)
        self.assertEqual(self.call('/api/admin/diagnostics/failed-messages',role='READER')[0],403)
        self.assertEqual(self.call('/api/admin/diagnostics/reconciliation')[1],[])
        code,csv=self.call('/api/reports/occupancy.csv',role='READER');self.assertEqual(code,200);self.assertTrue(csv.startswith('site_id,partner_id'))
if __name__=='__main__':unittest.main(verbosity=2)
