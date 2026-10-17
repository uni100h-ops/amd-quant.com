"""Transient visitor presence for the recovery agent. No email is sent."""
import os
import threading
import time
from urllib.parse import urlsplit

PRESENCE_TTL = 60


class VisitAlerts:
    # Keep the existing interface so the gateway and frontend remain compatible.
    def __init__(self, ready, *, monotonic=time.monotonic):
        self.ready = ready
        self.monotonic = monotonic
        self.lock = threading.RLock()
        self.last_seen = None
        self.closed = False
        site = urlsplit(os.getenv('GPU_ALERT_SITE_URL', 'https://amd-quant.com').strip())
        self.origin = f'{site.scheme}://{site.netloc}'

    def close(self):
        with self.lock:
            self.closed = True
            self.last_seen = None

    def waiting(self):
        with self.lock:
            if self.closed or self.ready():
                self.last_seen = None
                return False
            return self.last_seen is not None and self.monotonic() - self.last_seen < PRESENCE_TTL

    def status(self):
        with self.lock:
            if self.ready():
                self.last_seen = None
                return 'online'
            return 'checking' if self.waiting() else 'idle'

    def visit(self):
        with self.lock:
            if not self.closed and not self.ready():
                self.last_seen = self.monotonic()
            return self.status()


