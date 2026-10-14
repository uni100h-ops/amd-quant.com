"""Render gateway and authenticated AMD/IBM engine. One worker per engine."""
import asyncio,hmac,os,re,time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID
import httpx
from fastapi import FastAPI,HTTPException,Request,Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,ConfigDict
from .job_store import BusyError,ConflictError

ROOT=Path(__file__).resolve().parents[1]
ROLE=os.getenv('QCHAT_ROLE','gateway');APP_TOKEN=os.getenv('APP_TOKEN','')
AMD_URL=os.getenv('AMD_API_URL','').rstrip('/');AMD_TOKEN=os.getenv('AMD_API_TOKEN','')
PUBLIC_DEMO=os.getenv('PUBLIC_DEMO','0')=='1'
PUBLIC_RATE_LIMIT=int(os.getenv('PUBLIC_RATE_LIMIT','12'))
public_requests=deque();manager=None

@asynccontextmanager
async def lifespan(app):
    global manager
    if ROLE=='engine':
        if not APP_TOKEN:raise RuntimeError('APP_TOKEN is required')
        if os.getenv('QUANTUM_BACKEND','ibm')!='ibm' or os.getenv('QCHAT_PROFILE','micro')!='micro':raise RuntimeError('This server supports physical IBM execution with Micro only')
        import torch
        torch.set_num_threads(int(os.getenv('CPU_THREADS','2')))
        device=os.getenv('QCHAT_DEVICE','cuda')
        if os.getenv('REQUIRE_AMD','1')=='1' and not (device.startswith('cuda') and torch.cuda.is_available() and torch.version.hip):raise RuntimeError('A working AMD ROCm GPU is required')
        from qchat.inference import MicroEngine
        from qchat.ibm import IBMRunner
        from .ibm_jobs import JobManager
        manager=JobManager(MicroEngine(os.getenv('MODEL_DIR',str(ROOT/'dist/models')),device),IBMRunner(),os.getenv('STATE_DIR','/state'))
    elif ROLE!='gateway':raise RuntimeError('Unknown QCHAT_ROLE')
    if PUBLIC_DEMO and ROLE!='gateway':raise RuntimeError('Public access belongs on the gateway')
    if PUBLIC_RATE_LIMIT<1:raise RuntimeError('Invalid request limit')
    if AMD_URL:
        url=urlsplit(AMD_URL)
        if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path:raise RuntimeError('AMD_API_URL must be a credential-free HTTPS origin')
    yield

app=FastAPI(title='AmdQuant',version='2.0.0',lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
async def authorized(request:Request):
    if not APP_TOKEN or not hmac.compare_digest(request.headers.get('authorization',''),'Bearer '+APP_TOKEN):raise HTTPException(401,'Authentication required')

def enabled():
    if not PUBLIC_DEMO or ROLE!='gateway':raise HTTPException(503,'Comparison service is not configured')

def valid_job_id(id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{32}',id):raise HTTPException(404,'Job not found')
    return id

class Submission(BaseModel):
    model_config=ConfigDict(extra='forbid')
    prompt:str=Field(min_length=1,max_length=2000)
    request_id:UUID

async def remote(path,payload=None):
    if not AMD_URL or not AMD_TOKEN:raise HTTPException(503,'AMD service is not configured')
    try:
        async with httpx.AsyncClient(timeout=30,follow_redirects=False) as client:
            headers={'Authorization':'Bearer '+AMD_TOKEN}
            r=await client.get(AMD_URL+path,headers=headers) if payload is None else await client.post(AMD_URL+path,json=payload,headers=headers)
        if r.status_code not in (200,202):
            code=r.status_code if r.status_code in (404,409,422,429,503) else 502
            raise HTTPException(code,'Engine request unavailable')
        return r.json()
    except (httpx.HTTPError,ValueError):raise HTTPException(502,'AMD engine unavailable') from None

def local(call):
    if manager is None:raise HTTPException(503,'Engine is not ready')
    try:return call()
    except KeyError:raise HTTPException(404,'Job not found') from None
    except BusyError:raise HTTPException(429,'Engine busy or a previous submission needs review') from None
    except ConflictError:raise HTTPException(409,'Request identifier already used') from None
    except ValueError:raise HTTPException(422,'Question is too long or invalid') from None

@app.middleware('http')
async def private_api(request,call_next):
    response=await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control']='no-store'
        response.headers['Referrer-Policy']='no-referrer'
    return response

@app.get('/healthz')
def health():return {'ok':True,'role':ROLE}

@app.get('/api/info',dependencies=[Depends(authorized)])
async def info():return local(lambda:manager.info()) if ROLE=='engine' else await remote('/api/info')

@app.post('/api/jobs',dependencies=[Depends(authorized)],status_code=202)
async def submit(body:Submission):
    return local(lambda:manager.create(str(body.request_id),body.prompt)) if ROLE=='engine' else await remote('/api/jobs',body.model_dump(mode='json'))

@app.get('/api/jobs/{id}',dependencies=[Depends(authorized)])
async def get_job(id:str):
    valid_job_id(id)
    return local(lambda:manager.get(id)) if ROLE=='engine' else await remote('/api/jobs/'+id)

@app.post('/api/jobs/{id}/cancel',dependencies=[Depends(authorized)])
async def cancel(id:str):
    valid_job_id(id)
    return local(lambda:manager.cancel(id)) if ROLE=='engine' else await remote('/api/jobs/'+id+'/cancel',{})

@app.get('/api/public/info',dependencies=[Depends(enabled)])
async def public_info():
    data=await remote('/api/info')
    quantum=data.get('quantum',{})
    if data.get('amd_verified') is not True or not data.get('ready') or not data.get('accepting_jobs') or quantum.get('configured') is not True or quantum.get('simulator') is not False:raise HTTPException(503,'AMD and IBM are not ready')
    return {k:data[k] for k in ('ready','profile','gpu','amd_verified','rocm','quantum','scope') if k in data}

@app.post('/api/public/jobs',dependencies=[Depends(enabled)],status_code=202)
async def public_submit(body:Submission):
    now=time.monotonic()
    while public_requests and now-public_requests[0]>=60:public_requests.popleft()
    if len(public_requests)>=PUBLIC_RATE_LIMIT:raise HTTPException(429,'Please try again shortly')
    public_requests.append(now)
    await public_info()
    return await remote('/api/jobs',body.model_dump(mode='json'))

@app.get('/api/public/jobs/{id}',dependencies=[Depends(enabled)])
async def public_job(id:str):return await remote('/api/jobs/'+valid_job_id(id))

@app.post('/api/public/jobs/{id}/cancel',dependencies=[Depends(enabled)])
async def public_cancel(id:str):return await remote('/api/jobs/'+valid_job_id(id)+'/cancel',{})

app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='web')
