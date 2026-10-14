"""Single Render service. Public UI, private credentials, remote AMD and IBM."""
import asyncio
import hmac
import logging
import os
import re
import time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .job_store import BusyError, ConflictError

ROOT = Path(__file__).resolve().parents[1]
APP_TOKEN = os.getenv('APP_TOKEN', '')
PUBLIC_DEMO = os.getenv('PUBLIC_DEMO', '1') == '1'
PUBLIC_RATE_LIMIT = int(os.getenv('PUBLIC_RATE_LIMIT', '6'))
public_requests = deque()
manager = None
startup_status = 'starting'


def initialize():
    global manager, startup_status
    from qchat.amd_api import AMDNormalizer, AMDError
    try:
        normalizer = AMDNormalizer()
        from qchat.micro_numpy import MicroEngine
        from qchat.ibm_open import IBMOpenRunner
        from .ibm_jobs import JobManager
        engine = MicroEngine(ROOT / 'dist/models')
        runner = IBMOpenRunner()
        manager = JobManager(engine, runner, normalizer, os.getenv('STATE_DIR', '/tmp/amdquant-state'))
        startup_status = 'ready'
    except AMDError:
        startup_status = 'amd_config'
    except Exception:
        startup_status = 'ibm_config'
    # Provider exceptions can contain secrets; log only this fixed status.
    logging.getLogger('amdquant').warning('AMDQUANT_INIT status=%s', startup_status)


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(asyncio.to_thread(initialize))
    yield
    if not task.done():
        task.cancel()


app = FastAPI(title='AmdQuant', version='3.0.0', lifespan=lifespan,
              docs_url=None, redoc_url=None, openapi_url=None)


class Submission(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prompt: str = Field(min_length=1, max_length=2000)
    request_id: UUID


def enabled():
    if not PUBLIC_DEMO:
        raise HTTPException(503, 'Comparison service unavailable')


def authorized(request: Request):
    if not APP_TOKEN or not hmac.compare_digest(request.headers.get('authorization', ''), 'Bearer ' + APP_TOKEN):
        raise HTTPException(401, 'Authentication required')


def valid_id(id):
    if not re.fullmatch(r'[a-f0-9]{32}', id):
        raise HTTPException(404, 'Job not found')
    return id


def local(call):
    if manager is None:
        raise HTTPException(503, startup_status)
    try:
        return call()
    except KeyError:
        raise HTTPException(404, 'Job not found; it may have been interrupted by a restart') from None
    except BusyError:
        raise HTTPException(429, 'Comparison busy or a previous IBM job needs review') from None
    except ConflictError:
        raise HTTPException(409, 'Request identifier already used') from None
    except ValueError:
        raise HTTPException(422, 'Invalid question') from None
    except Exception:
        raise HTTPException(503, 'Provider state could not be verified') from None


@app.middleware('http')
async def api_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.get('/healthz')
def health():
    return {'ok': True, 'role': 'amd-tokenfactory-ibm', 'initialization': startup_status}


@app.get('/api/public/info', dependencies=[Depends(enabled)])
def info():
    if manager is None:
        return {'ready': False, 'status': startup_status}
    data = manager.info()
    return {k: data[k] for k in ('ready', 'profile', 'amd', 'quantum', 'accepting_jobs', 'storage', 'scope')}


@app.post('/api/public/jobs', dependencies=[Depends(enabled)], status_code=202)
async def submit(body: Submission):
    now = time.monotonic()
    while public_requests and now - public_requests[0] >= 60:
        public_requests.popleft()
    if len(public_requests) >= PUBLIC_RATE_LIMIT:
        raise HTTPException(429, 'Please try again shortly')
    public_requests.append(now)
    return await asyncio.to_thread(local, lambda: manager.create(str(body.request_id), body.prompt))


@app.get('/api/public/jobs/{id}', dependencies=[Depends(enabled)])
def get_job(id: str):
    valid_id(id)
    return local(lambda: manager.get(id))


@app.post('/api/public/jobs/{id}/cancel', dependencies=[Depends(enabled)])
def cancel(id: str):
    valid_id(id)
    return local(lambda: manager.cancel(id))


@app.get('/api/admin/status', dependencies=[Depends(authorized)])
def admin_status():
    return {'initialization': startup_status, 'runtime': manager.info() if manager else None}


app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='web')
