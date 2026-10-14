"""Persistent request identity and QPU submission budget. Never stores secrets."""
import json,secrets,sqlite3,time
from datetime import datetime,timezone
from pathlib import Path
from contextlib import contextmanager

class BusyError(RuntimeError):pass
class BudgetError(RuntimeError):pass
class ConflictError(RuntimeError):pass

class JobStore:
    def __init__(self,path):
        self.path=str(path);Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, request_id TEXT UNIQUE, prompt TEXT, status TEXT, created REAL, updated REAL, payload TEXT, cancel INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY, job_id TEXT, day TEXT, ibm_job_id TEXT, status TEXT, evidence TEXT);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
            ''')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()
    def get(self,id):
        with self.connect() as db:r=db.execute('SELECT * FROM jobs WHERE id=?',(id,)).fetchone()
        if r is None:raise KeyError(id)
        return {'job_id':r['id'],'status':r['status'],'created_at':r['created'],'updated_at':r['updated'],**json.loads(r['payload'])}
    def create(self,request_id,prompt):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT id,prompt FROM jobs WHERE request_id=?',(request_id,)).fetchone()
            if existing:
                if existing['prompt']!=prompt:raise ConflictError('Request ID is already bound to another question')
                return existing['id'],False
            if db.execute("SELECT 1 FROM settings WHERE key='unresolved_submission'").fetchone():raise BusyError('A previous IBM submission needs administrator review')
            if db.execute("SELECT 1 FROM jobs WHERE status IN ('queued','running')").fetchone():raise BusyError('Another comparison is running')
            id=secrets.token_urlsafe(24);now=time.time()
            db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,0)',(id,request_id,prompt,'queued',now,now,json.dumps({'prompt':prompt,'stage':'queued'})))
        return id,True
    def update(self,id,status=None,**fields):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT payload,status FROM jobs WHERE id=?',(id,)).fetchone()
            data=json.loads(row['payload']);data.update(fields)
            db.execute('UPDATE jobs SET status=?,updated=?,payload=? WHERE id=?',(status or row['status'],time.time(),json.dumps(data),id))
    def cancel(self,id):
        with self.connect() as db:
            row=db.execute('SELECT status FROM jobs WHERE id=?',(id,)).fetchone()
            if row is None:raise KeyError(id)
            if row['status'] in ('queued','running'):db.execute('UPDATE jobs SET cancel=1 WHERE id=?',(id,))
    def cancelled(self,id):
        with self.connect() as db:return bool(db.execute('SELECT cancel FROM jobs WHERE id=?',(id,)).fetchone()['cancel'])
    def reserve(self,id,limit):
        day=datetime.now(timezone.utc).date().isoformat()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            count=db.execute('SELECT COUNT(*) AS n FROM submissions WHERE day=?',(day,)).fetchone()['n']
            if count>=limit:raise BudgetError('Daily IBM submission limit reached')
            row=db.execute('INSERT INTO submissions(job_id,day,status,evidence) VALUES (?,?,?,?)',(id,day,'submitting','{}'))
            return row.lastrowid
    def record(self,reservation,ibm_job_id,status,evidence):
        with self.connect() as db:db.execute('UPDATE submissions SET ibm_job_id=?,status=?,evidence=? WHERE id=?',(ibm_job_id,status,json.dumps(evidence),reservation))
    def traces(self,id):
        with self.connect() as db:rows=db.execute('SELECT ibm_job_id,status,evidence FROM submissions WHERE job_id=? ORDER BY id',(id,)).fetchall()
        return [{'ibm_job_id':r['ibm_job_id'],'status':r['status'],**json.loads(r['evidence'])} for r in rows]
    def unresolved(self):
        with self.connect() as db:return [dict(r) for r in db.execute("SELECT * FROM submissions WHERE status NOT IN ('DONE','CANCELLED','ERROR')")]
    def mark_unresolved(self):
        with self.connect() as db:db.execute("INSERT OR REPLACE INTO settings VALUES ('unresolved_submission','1')")
    def recover(self,runner):
        unresolved=False
        for row in self.unresolved():
            if not row['ibm_job_id']:
                unresolved=True;continue
            try:
                status=runner.cancel_remote(row['ibm_job_id'])
                if status not in ('DONE','CANCELLED','ERROR'):unresolved=True
                self.record(row['id'],row['ibm_job_id'],status,json.loads(row['evidence']))
            except Exception:unresolved=True
        with self.connect() as db:
            if unresolved:db.execute("INSERT OR REPLACE INTO settings VALUES ('unresolved_submission','1')")
            else:db.execute("DELETE FROM settings WHERE key='unresolved_submission'")
            rows=db.execute("SELECT id,payload FROM jobs WHERE status IN ('queued','running')").fetchall()
            for row in rows:
                payload=json.loads(row['payload']);payload.update(stage='interrupted',error_code='interrupted')
                db.execute('UPDATE jobs SET status=?,updated=?,payload=? WHERE id=?',('failed',time.time(),json.dumps(payload),row['id']))
        return not unresolved
