"""Free-plan guard and provider-side checks that survive Render Free restarts."""
from datetime import datetime, timezone
import os
import threading
import time
from .ibm import IBMRunner, QuantumError


class IBMOpenRunner(IBMRunner):
    def __init__(self):
        super().__init__()
        instance = os.environ['IBM_QUANTUM_INSTANCE']
        selected = [i for i in self.service.instances() if i.get('crn') == instance]
        if len(selected) != 1 or selected[0].get('plan') != 'open':
            raise QuantumError('IBM instance must be a verified Open Plan CRN')
        self.guard_lock = threading.Lock()
        self.last_guard = 0
        self.blocked = True
        self.recently_submitted = set()

    def info(self):
        return {**super().info(), 'plan': 'open'}

    def accepting(self, force=False):
        with self.guard_lock:
            if force or time.monotonic() - self.last_guard > 20:
                try:
                    pending = self.service.jobs(limit=1, pending=True, job_tags=['amdquant'])
                    self.blocked = bool(pending)
                except Exception:
                    self.blocked = True
                self.last_guard = time.monotonic()
            return not self.blocked

    def request_exists(self, request_id):
        # Prevent resubmission of an acknowledged IBM job after local storage loss.
        try:
            return bool(self.service.jobs(limit=1, job_tags=['amdquant-' + request_id]))
        except Exception:
            raise QuantumError('Cannot establish previous IBM request state') from None

    def evaluate(self, angles, theta, store, request_job_id, step, deadline):
        from server.job_store import BudgetError
        day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            jobs = self.service.jobs(limit=self.daily_limit, created_after=day, job_tags=['amdquant'])
            remote_ids = {job.job_id() for job in jobs}
        except Exception:
            raise QuantumError('Unable to verify IBM daily allowance') from None
        today = day.date().isoformat()
        local_ids = {id for id, date in self.recently_submitted if date == today}
        if len(remote_ids | local_ids) >= self.daily_limit:
            raise BudgetError('Daily IBM job allowance reached')
        result = super().evaluate(angles, theta, store, request_job_id, step, deadline)
        self.recently_submitted.add((result[2], today))
        return result
