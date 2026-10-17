"""Run in the AMD notebook: one GPU job, authenticated outbound HTTPS only."""
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import signal
import threading
import time
from urllib.parse import urlsplit
from uuid import uuid4
import httpx
from .protocol import VERSION, KNOWN_ERRORS, RunRequest, amd_verified


def validate_connection(url, token):
    url = url.strip().rstrip('/')
    parts = urlsplit(url)
    if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
            or parts.path or parts.query or parts.fragment):
        raise ValueError('Use the HTTPS origin of your Render website, without a path.')
    if len(token.strip()) < 32:
        raise ValueError('GPU_WORKER_TOKEN must contain at least 32 characters.')
    return url, token.strip()


def calculate(request, progress, cancelled, partial=None):
    from optimizer.amd import resolve
    from optimizer.problems import build_problem
    from optimizer.engines import compare
    started = time.perf_counter()
    spec, adapter = resolve(request.question)
    if cancelled():
        raise RuntimeError('cancelled')
    result = compare(build_problem(spec), seed=request.seed, progress=progress, cancelled=cancelled, partial=partial)
    result['input_adapter'] = adapter
    result['request_wall_ms'] = (time.perf_counter() - started) * 1000
    return result


class NotebookWorker:
    def __init__(self, info, client):
        if not amd_verified(info.get('hardware')) or info.get('version') != VERSION:
            raise RuntimeError('amd_gpu_required')
        self.info, self.client = info, client
        self.id = uuid4().hex
        self.lock = threading.RLock()
        self.report = None
        self.future = None
        self.cancelled = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='amdquant')
        self.stopping = threading.Event()
        self.connected = False
        self.changed = threading.Event()

    def run_job(self, command):
        req = RunRequest.model_validate(command['request'])
        if req.request_id.hex != command['id']:
            raise RuntimeError('Invalid job identity')
        self.cancelled.clear()
        with self.lock:
            self.report = {'id': command['id'], 'lease': command['lease'],
                           'status': 'running', 'stage': 'preparing'}
        print('RUN: ' + command['id'], flush=True)
        self.future = self.executor.submit(self.compute, req)

    def compute(self, req):
        def progress(stage):
            with self.lock:
                self.report['stage'] = stage
            self.changed.set()
        def partial(result):
            with self.lock:
                self.report['partial'] = result
            self.changed.set()
        try:
            result = calculate(req, progress, self.cancelled.is_set, partial)
            if self.cancelled.is_set():
                raise RuntimeError('cancelled')
            # Keep evidence in the notebook even if a later network request fails.
            folder = Path('mediciones')
            try:
                folder.mkdir(exist_ok=True)
                (folder / (req.request_id.hex + '.json')).write_text(
                    json.dumps(result, ensure_ascii=False, allow_nan=False), encoding='utf-8')
            except OSError:
                print('Evidence file could not be saved; use the website export.', flush=True)
            with self.lock:
                self.report.pop('partial',None)
                self.report.update(status='completed', stage='completed', result=result)
            self.changed.set()
            print('DONE: ' + req.request_id.hex, flush=True)
        except Exception as exc:
            from optimizer.amd import InputError
            error = str(exc) if isinstance(exc, (RuntimeError, InputError)) and str(exc) in KNOWN_ERRORS else 'run_failed'
            if self.cancelled.is_set():
                error = 'cancelled'
            with self.lock:
                self.report.update(status='cancelled' if error == 'cancelled' else 'failed',
                                   stage=error, error=error, issues=getattr(exc,'issues',[]))
            self.changed.set()
            print('JOB: ' + error, flush=True)

    def tick(self):
        with self.lock:
            report = dict(self.report) if self.report else None
        response = self.client.post('/api/worker/poll', json={
            'worker_id': self.id, 'info': self.info, 'report': report})
        if response.status_code in (401, 403):
            raise RuntimeError('The GPU_WORKER_TOKEN does not match the value on Render.')
        if response.status_code == 409:
            raise RuntimeError('Another notebook is connected. Stop it before starting this one.')
        if response.status_code in (404, 422) or 300 <= response.status_code < 400:
            raise RuntimeError('Incompatible website or rejected result. Deploy the complete v10 ZIP.')
        response.raise_for_status()
        command = response.json()
        action = command.get('action')
        if action not in ('idle', 'run', 'ack', 'discard', 'cancel', 'continue'):
            raise RuntimeError('Incompatible response from the website.')
        if not self.connected:
            print('LISTO: GPU conectada a la web. Ya puedes elegir Problem 1 y pulsar Run.', flush=True)
            self.connected = True
        if action == 'run':
            if self.report is None:
                self.run_job(command['job'])
        elif action == 'ack':
            if self.future:
                self.future.result()
            with self.lock:
                self.report = None
            self.future = None
        elif action == 'cancel':
            self.cancelled.set()
        elif action == 'discard':
            self.cancelled.set()
            if not self.future or self.future.done():
                with self.lock:
                    self.report = None
                self.future = None

    def serve(self):
        failures = 0
        try:
            while not self.stopping.is_set():
                try:
                    self.changed.clear()
                    self.tick()
                    failures = 0
                except (httpx.HTTPError, ValueError):
                    failures += 1
                    if failures == 1:
                        print('Connection interrupted. Retrying without resubmitting the calculation.', flush=True)
                    self.connected = False
                self.changed.wait(min(15, 2 ** min(failures, 4)) if failures else 2)
        finally:
            self.cancelled.set()
            try:
                self.client.post('/api/worker/disconnect', json={'worker_id': self.id}, timeout=5)
            except httpx.HTTPError:
                pass
            self.executor.shutdown(wait=True, cancel_futures=True)
            from optimizer.live import close
            close()


def main():
    url, token = validate_connection(os.getenv('RENDER_URL', ''), os.getenv('GPU_WORKER_TOKEN', ''))
    # Fail before announcing availability on any CPU-only or NVIDIA environment.
    from optimizer.engines import verify_gpu
    from optimizer.amd import configured
    print('Checking AMD GPU and warming up both solvers...', flush=True)
    hw = verify_gpu()
    from optimizer.live import prepare
    print("Preparing independent CPU and AMD GPU processes...", flush=True)
    prepare()
    print('GPU: ' + hw['sb_device_name'] + ' | ROCm: ' + hw['rocm_version'], flush=True)
    with httpx.Client(base_url=url, headers={'Authorization': 'Bearer ' + token},
                      timeout=httpx.Timeout(25, connect=10), follow_redirects=False,
                      trust_env=False) as client:
        worker = NotebookWorker({'version': VERSION, 'hardware': hw,
                                 'amd_configured': bool(configured())}, client)
        for name in (signal.SIGINT, signal.SIGTERM):
            signal.signal(name, lambda *_: worker.stopping.set())
        worker.serve()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Never print request headers, environment, URLs with credentials or input data.
        safe = str(exc) if isinstance(exc, (RuntimeError, ValueError)) else type(exc).__name__
        print('STOP: ' + safe, flush=True)
        raise SystemExit(1)
