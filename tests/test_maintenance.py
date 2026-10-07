import importlib.util,json,os,pathlib,subprocess,tempfile,unittest,uuid,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cutover',ROOT/'deployment/scripts/cutover.py');cutover=importlib.util.module_from_spec(spec);spec.loader.exec_module(cutover)
class Maintenance(unittest.TestCase):
    def test_cutover_refuses_bad_and_accepts_same(self):
        source=cutover.load(ROOT/'deployment/environments/source-snapshot.json');good=cutover.load(ROOT/'deployment/environments/target-good.json');bad=cutover.load(ROOT/'deployment/environments/target-bad.json')
        self.assertEqual(cutover.compare(source,good),[]);self.assertTrue(cutover.compare(source,bad))
    def test_snapshot_duplicates_rejected(self):
        row=next(iter(cutover.load(ROOT/'deployment/environments/source-snapshot.json').values()))
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'duplicate.json';p.write_text(json.dumps([row,row]));self.assertRaises(ValueError,cutover.load,p)
    def test_h2_migration_snapshot_fresh_restore(self):
        name='maintenance-'+uuid.uuid4().hex; folder=ROOT/'runtime'/name;folder.mkdir(parents=True);migration=folder/'V002.sql';migration.write_text((ROOT/'src/main/resources/schema.sql').read_text()+'\n'+(ROOT/'database/migrations/V002__error_lookup_index.sql').read_text());snapshot=folder/'snapshot.sql'
        env=os.environ.copy();env['ROLEOS_DB_URL']=f'jdbc:h2:file:{folder}/source;MODE=Oracle;DB_CLOSE_DELAY=-1';base=['java','-cp',str(ROOT/'target/classes')+os.pathsep+str(ROOT/'target/dependency/*'),'roleos.DbTool']
        def run(*args):return subprocess.run(base+list(args),cwd=ROOT,env=env,capture_output=True,text=True)
        self.assertEqual(run('migrate',str(migration)).returncode,0);self.assertEqual(run('migrate',str(migration)).returncode,0)
        self.assertEqual(run('backup',str(snapshot)).returncode,0);self.assertTrue(snapshot.stat().st_size>100);self.assertIn('IDX_MESSAGES_ERROR',snapshot.read_text());self.assertIn('SCHEMA_VERSION',snapshot.read_text());self.assertNotEqual(run('backup',str(snapshot)).returncode,0)
        env['ROLEOS_DB_URL']=f'jdbc:h2:file:{folder}/restored;MODE=Oracle;DB_CLOSE_DELAY=-1';restored=run('restore',str(snapshot));self.assertEqual(restored.returncode,0,restored.stderr)
        self.assertNotEqual(run('restore',str(snapshot)).returncode,0)
        backup2=folder/'restored.sql';self.assertEqual(run('backup',str(backup2)).returncode,0);self.assertIn('IDX_MESSAGES_ERROR',backup2.read_text())
if __name__=='__main__':unittest.main(verbosity=2)
