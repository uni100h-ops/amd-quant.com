"""Visitor-triggered owner email. HTTPS only; no AMD login or GPU provisioning."""
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
import re
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

log = logging.getLogger('uvicorn.error.amdquant.alerts')
INTERVAL = 30  # Repeated owner alert while a visitor is still waiting.
PRESENCE_TTL = 60  # Stop when all page heartbeats have disappeared.


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send_email(api_key, message, idempotency_key):
    request = Request('https://api.resend.com/emails', method='POST',
        data=json.dumps(message, ensure_ascii=False, sort_keys=True).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json',
                 'User-Agent': 'AmdQuant-Visit-Alert/1.0', 'Idempotency-Key': idempotency_key})
    with build_opener(NoRedirect()).open(request, timeout=10) as response:
        result = json.loads(response.read(16384))
        if not result.get('id'):
            raise ValueError('missing_email_id')


class VisitAlerts:
    def __init__(self, ready, *, grace=20, sender=send_email, clock=time.time, monotonic=time.monotonic):
        self.ready, self.grace, self.sender, self.clock = ready, grace, sender, clock
        self.monotonic = monotonic
        self.api_key = os.getenv('RESEND_API_KEY', '').strip()
        self.recipient = os.getenv('GPU_ALERT_TO', '').strip()
        self.from_address = os.getenv('GPU_ALERT_FROM', 'AmdQuant <onboarding@resend.dev>').strip()
        self.site_url = os.getenv('GPU_ALERT_SITE_URL', 'https://amdquant.onrender.com').strip().rstrip('/')
        url = urlsplit(self.site_url)
        self.configured = bool(self.api_key and re.fullmatch(r'[^\s@<>,;]+@[^\s@<>,;]+\.[^\s@<>,;]+', self.recipient)
            and self.from_address and not any(c in self.from_address + self.api_key for c in '\r\n')
            and url.scheme == 'https' and url.hostname and not url.username and not url.password
            and not url.query and not url.fragment and not any(c.isspace() for c in self.site_url))
        self.origin = f'{url.scheme}://{url.netloc}'
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.thread = None
        self.first_seen = None
        self.last_seen = None
        self.last_attempt = float('-inf')
        self.accepted = False
        self.failed = False
        self.sending = False

    def close(self):
        self.stop.set()

    def status(self):
        # Provider acceptance does not prove inbox delivery or GPU activation.
        with self.lock:
            if self.ready():
                return 'online'
            if not self.configured:
                return 'disabled'
            if self.failed:
                return 'failed'
            if self.accepted:
                return 'accepted'
            return 'checking' if self.first_seen is not None else 'idle'

    def visit(self):
        with self.lock:
            if self.ready() or not self.configured or self.stop.is_set():
                return self.status()
            now = self.monotonic()
            if self.last_seen is None or now - self.last_seen >= PRESENCE_TTL:
                self.first_seen = now
                self.accepted = self.failed = False
            self.last_seen = now
            # One monitor for all browsers; opening extra tabs never resets the
            # countdown or creates additional email loops.
            if self.thread is None:
                self.thread = threading.Thread(target=self._monitor, daemon=True)
                self.thread.start()
            return self.status()

    def _monitor(self):
        while not self.stop.is_set():
            self._tick()
            if self.stop.wait(0.5):
                break

    def _tick(self):
        with self.lock:
            now = self.monotonic()
            if self.stop.is_set() or not self.configured:
                return
            if self.ready() or self.last_seen is None or now - self.last_seen >= PRESENCE_TTL:
                self.first_seen = self.last_seen = None
                self.accepted = self.failed = False
                return
            if self.sending or now - self.first_seen < self.grace or now - self.last_attempt < INTERVAL:
                return
            self.sending = True
            self.last_attempt = now
        try:
            # Recheck immediately before sending; the worker may have returned
            # while the UI was waiting. A message already in transit cannot be recalled.
            if self.stop.is_set() or self.ready():
                return
            bucket = int(self.clock() // INTERVAL)
            message, key = self.message(bucket)
            self.sender(self.api_key, message, key)
            with self.lock:
                self.accepted, self.failed = True, False
            log.info('GPU_VISIT_ALERT accepted_by_provider')
        except Exception as exc:
            code = str(exc.code) if isinstance(exc, HTTPError) else type(exc).__name__
            log.warning('GPU_VISIT_ALERT failed code=%s', code)
            with self.lock:
                self.failed = True
        finally:
            with self.lock:
                self.sending = False

    def message(self, bucket):
        # Stable payload + key let Resend deduplicate within a 30-second window even when
        # Render loses process memory. No visitor IP, question or identity used.
        start = datetime.fromtimestamp(bucket * INTERVAL, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        message = {'from': self.from_address, 'to': [self.recipient],
            'subject': 'AmdQuant: una visita encuentra la GPU desconectada',
            'text': (
                f'Alguien ha abierto {self.site_url} y el motor GPU no estaba conectado.\n\n'
                f'Intervalo del aviso: {start} (30 segundos; no es la hora exacta de la visita).\n'
                'Se ha comprobado que la GPU sigue desconectada y hay una visita reciente esperando.\n\n'
                'Abre https://notebooks.amd.com/tutorials y recupera o solicita tu notebook AMD.\n'
                'Ejecuta el notebook INICIAR_AMDQUANT_V10 con la URL de tu web y el mismo GPU_WORKER_TOKEN de Render.\n'
                'Cuando el worker se conecte, la web habilitara Run automaticamente.\n\n'
                'Este correo no crea una GPU. No sabemos si la visita era de un juez ni si sigue esperando.\n'
                'Los avisos se repiten cada 30 segundos mientras haya una visita esperando y la GPU siga desconectada.\n'
            )}
        digest = hashlib.sha256(json.dumps(message, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        return message, f'amdquant-gpu-wait30/{bucket}/{digest}'

