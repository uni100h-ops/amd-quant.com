"""Render web and bounded queue. The AMD notebook makes outbound HTTPS calls."""
from collections import deque
from contextlib import asynccontextmanager
import hmac
import json
import math
import os
from pathlib import Path
import threading
import time
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from optimizer.catalog import PRESETS, CATEGORIES
from optimizer.specs import resolve_input, InputError
from .protocol import VERSION, TERMINAL, KNOWN_ERRORS, RunRequest, PollRequest, amd_verified, result_verified, partial_verified
from .alerts import VisitAlerts

ROOT = Path(__file__).resolve().parents[1]
HEARTBEAT_TTL = 45
JOB_TIMEOUT = 300

class Broker:
    def __init__(self):
        self.jobs = {}
        self.active = None
        self.worker = None
        self.recent = deque()
        self.lock = threading.RLock()

    def fresh(self):
        return self.worker is not None and time.monotonic() - self.worker['seen'] < HEARTBEAT_TTL

    def expire(self):
        if self.active:
            job = self.jobs[self.active]
            if not self.fresh() or time.monotonic() - job['_created'] > JOB_TIMEOUT:
                error = 'gpu_worker_unreachable' if not self.fresh() else 'job_timeout'
                job.update(status='failed', stage=error, error=error)
                self.active = None

    def snapshot(self, key):
        with self.lock:
            self.expire()
            if key not in self.jobs:
                raise HTTPException(404, 'job_expired')
            return {k: v for k, v in self.jobs[key].items() if not k.startswith('_')}

    def info(self):
        with self.lock:
            self.expire()
            configured = len(os.getenv('GPU_WORKER_TOKEN', '').strip()) >= 32
            ready = configured and self.fresh()
            return {'version': VERSION, 'ready': ready,
                'error': None if ready else ('gpu_not_connected' if configured else 'gpu_worker_config'),
                'hardware': self.worker['info']['hardware'] if ready else {},
                'amd_configured': self.worker['info']['amd_configured'] if ready else False,
                'presets': PRESETS, 'categories': CATEGORIES, 'storage': 'transient_last_12_jobs',
                'public': os.getenv('PUBLIC_DEMO', '1') == '1', 'role': 'notebook_gateway'}

    def submit(self, req):
        key = req.request_id.hex
        identity = (req.question.strip(), req.seed, req.language)
        if not identity[0]:
            raise HTTPException(422, 'empty_question')
        specification = validate_problem(identity[0])
        with self.lock:
            self.expire()
            if key in self.jobs:
                if self.jobs[key]['_identity'] != identity:
                    raise HTTPException(409, 'request_id_conflict')
                return self.snapshot(key)
            if not self.info()['ready']:
                raise HTTPException(503, 'gpu_not_connected')
            if self.active:
                raise HTTPException(429, 'busy')
            now = time.monotonic()
            while self.recent and self.recent[0] < now - 60:
                self.recent.popleft()
            # A single active job already protects the GPU. Allow an ordinary
            # tour through the examples without the former six-runs limit.
            if len(self.recent) >= 30:
                raise HTTPException(429, 'rate_limit')
            while len(self.jobs) >= 12:
                self.jobs.pop(next(iter(self.jobs)))
            self.recent.append(now)
            self.jobs[key] = {'id': key, 'status': 'queued', 'stage': 'queued',
                'created_at': time.time(), 'question': identity[0], '_identity': identity,
                # Send the validated data model, not a presentation label.
                # Existing v10 notebooks can then resolve renamed/reordered
                # examples even if they still carry the original catalogue.
                '_created': now, '_request': {**req.model_dump(mode='json'),
                    'question': specification.model_dump_json(exclude_none=True)},
                '_lease': uuid4().hex, '_worker': None, '_cancel': False}
            self.active = key
            return self.snapshot(key)

    def cancel(self, key):
        with self.lock:
            self.snapshot(key)
            job = self.jobs[key]
            if job['status'] == 'queued':
                job.update(status='cancelled', stage='cancelled')
                self.active = None
            elif job['status'] == 'running':
                job['_cancel'] = True
                job['stage'] = 'cancelling'
            return self.snapshot(key)

    def poll(self, packet):
        worker_id = packet.worker_id.hex
        info = packet.info.model_dump()
        if not amd_verified(info['hardware']):
            raise HTTPException(422, 'amd_gpu_required')
        with self.lock:
            self.expire()
            if self.fresh() and self.worker['id'] != worker_id:
                raise HTTPException(409, 'worker_already_connected')
            self.worker = {'id': worker_id, 'seen': time.monotonic(), 'info': info}
            report = packet.report
            if report:
                job = self.jobs.get(report.id)
                if not job or job['_lease'] != report.lease or job['_worker'] != worker_id:
                    return {'action': 'discard'}
                if job['status'] in TERMINAL:
                    return {'action': 'ack' if report.status in TERMINAL else 'discard'}
                if report.partial is not None:
                    if not partial_verified(report.partial): raise HTTPException(422, 'gpu_worker_protocol')
                    job['partial'] = report.partial
                if report.status in TERMINAL:
                    if job['_cancel'] or report.status == 'cancelled':
                        job.update(status='cancelled', stage='cancelled')
                    elif report.status == 'completed':
                        if not result_verified(report.result):
                            raise HTTPException(422, 'gpu_worker_protocol')
                        job.update(status='completed', stage='completed', result=report.result)
                    else:
                        error = report.error if report.error in KNOWN_ERRORS else 'run_failed'
                        job.update(status='failed', stage=error, error=error, issues=report.issues)
                    self.active = None
                    return {'action': 'ack'}
                if not job['_cancel']:
                    job['stage'] = report.stage
                return {'action': 'cancel' if job['_cancel'] else 'continue'}
            if self.active:
                job = self.jobs[self.active]
                if job['_worker'] not in (None, worker_id):
                    raise HTTPException(409, 'worker_already_connected')
                job['_worker'] = worker_id
                job.update(status='running', stage='preparing')
                return {'action': 'run', 'job': {'id': job['id'], 'lease': job['_lease'],
                                               'request': job['_request']}}
            return {'action': 'idle'}

    def disconnect(self, worker_id):
        with self.lock:
            if self.worker and self.worker['id'] == worker_id:
                self.worker = None
                self.expire()

@asynccontextmanager
async def lifespan(app):
    app.state.broker = Broker()
    app.state.visit_alerts = VisitAlerts(lambda: app.state.broker.info()['ready'])
    try:
        yield
    finally:
        app.state.visit_alerts.close()

app = FastAPI(title='AmdQuant AMD notebook gateway', version=VERSION, docs_url=None,
              redoc_url=None, openapi_url=None, lifespan=lifespan)

@app.middleware('http')
async def headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    response.headers['Cache-Control'] = 'no-store' if request.url.path.startswith('/api/') else 'no-cache'
    return response

def authorize_public(request):
    if os.getenv('PUBLIC_DEMO', '1') == '1':
        return
    token = os.getenv('APP_TOKEN', '')
    if not token or not hmac.compare_digest(request.headers.get('authorization', ''), 'Bearer ' + token):
        raise HTTPException(401, 'private_mode')

def authorize_worker(request):
    token = os.getenv('GPU_WORKER_TOKEN', '').strip()
    if len(token) < 32 or not hmac.compare_digest(request.headers.get('authorization', ''), 'Bearer ' + token):
        raise HTTPException(401, 'gpu_worker_auth')

async def payload(request, limit):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
            raise HTTPException(413, 'request_too_large')
    try:
        def reject_constant(value):
            raise ValueError('Non-finite JSON')
        def finite_float(value):
            number = float(value)
            if not math.isfinite(number):
                raise ValueError('Non-finite JSON')
            return number
        return json.loads(body, parse_constant=reject_constant, parse_float=finite_float)
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'invalid_request') from None

def validated(model, data):
    try:
        return model.model_validate(data)
    except ValidationError:
        raise HTTPException(422, 'invalid_request') from None

def check_key(key):
    try:
        if UUID(key).hex != key:
            raise ValueError
    except ValueError:
        raise HTTPException(404, 'job_expired') from None

@app.get('/healthz')
def health():
    return {'status': 'ok', 'version': VERSION, 'role': 'notebook_gateway'}

@app.get('/api/public/info')
def info(request: Request):
    alerts = request.app.state.visit_alerts
    return {**request.app.state.broker.info(), 'visit_alert': alerts.status(),
            'waiting_for_gpu': alerts.waiting()}

@app.post('/api/public/visit')
async def visit(request: Request):
    authorize_public(request)
    alerts = request.app.state.visit_alerts
    # Only this page's explicit heartbeat records demand. Monitoring /info
    # never creates demand. No email or visitor identity is involved.
    if request.headers.get('x-amdquant-visit') != '1' or request.headers.get('sec-fetch-site') == 'cross-site':
        raise HTTPException(403, 'invalid_visit')
    origin = request.headers.get('origin')
    if origin and origin not in (str(request.base_url).rstrip('/'), alerts.origin):
        raise HTTPException(403, 'invalid_visit')
    if await payload(request, 200) != {}:
        raise HTTPException(422, 'invalid_visit')
    return {'visit_alert': alerts.visit()}

def validate_problem(question):
    try:
        spec, adapter = resolve_input(question)
        return spec
    except InputError as exc:
        raise HTTPException(422, {'code':str(exc),'issues':exc.issues}) from None

@app.post('/api/public/validate')
async def validate_input(request: Request):
    authorize_public(request)
    data=await payload(request,600000)
    if not isinstance(data,dict) or set(data)!={'question'} or not isinstance(data['question'],str) or not 1<=len(data['question'])<=500000:
        raise HTTPException(422,'invalid_request')
    spec=validate_problem(data['question'])
    return {'valid':True,'spec':spec.model_dump(exclude_none=True),'data_source':'user_supplied' if spec.user_data() else 'synthetic'}

@app.post('/api/public/jobs', status_code=202)
async def submit(request: Request):
    authorize_public(request)
    req = validated(RunRequest, await payload(request, 600000))
    return request.app.state.broker.submit(req)

@app.get('/api/public/jobs/{key}')
def status(key: str, request: Request):
    authorize_public(request)
    check_key(key)
    return request.app.state.broker.snapshot(key)

@app.post('/api/public/jobs/{key}/cancel')
def cancel(key: str, request: Request):
    authorize_public(request)
    check_key(key)
    return request.app.state.broker.cancel(key)

@app.post('/api/worker/poll')
async def poll(request: Request):
    authorize_worker(request)
    packet = validated(PollRequest, await payload(request, 2_000_000))
    return request.app.state.broker.poll(packet)

@app.post('/api/worker/disconnect')
async def disconnect(request: Request):
    authorize_worker(request)
    data = await payload(request, 200)
    try:
        worker_id = UUID(data['worker_id']).hex
    except (TypeError, KeyError, ValueError):
        raise HTTPException(422, 'invalid_request') from None
    request.app.state.broker.disconnect(worker_id)
    return {'status': 'disconnected'}

app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='web')

