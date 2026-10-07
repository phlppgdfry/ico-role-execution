#!/usr/bin/env python3
"""Actual loopback ACK receiver: verifies HMAC and journals duplicate-safe receipts."""
import hashlib,hmac,json,os,pathlib,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=pathlib.Path(__file__).resolve().parents[2]; journal=pathlib.Path(os.environ.get('ROLEOS_ACK_JOURNAL',str(ROOT/'runtime/ack-journal.jsonl')));journal.parent.mkdir(parents=True,exist_ok=True)
secret=os.environ['ROLEOS_ACK_SECRET'].encode();lock=threading.Lock();seen=set()
if journal.exists():
    for line in journal.read_text().splitlines():seen.add(json.loads(line)['ack_id'])
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        if self.path!='/ack':self.send_error(404);return
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:self.send_error(400);return
        if length<=0 or length>16384:self.send_error(413);return
        raw=self.rfile.read(length);signature=hmac.new(secret,raw,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature,self.headers.get('X-RoleOS-Signature','')):self.send_error(401);return
        try:payload=json.loads(raw);ack_id=payload['ack_id'];assert isinstance(ack_id,str) and payload['status']=='PROCESSED'
        except (ValueError,KeyError,AssertionError):self.send_error(400);return
        with lock:
            duplicate=ack_id in seen
            if not duplicate:
                with journal.open('a') as f:f.write(json.dumps(payload)+'\n');f.flush();os.fsync(f.fileno())
                seen.add(ack_id)
        data=json.dumps(dict(received=True,duplicate=duplicate)).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('ROLEOS_ACK_PORT','8091'))),Handler).serve_forever()
