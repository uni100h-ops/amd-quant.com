"""One comparison at a time: AMD normalization, two Micro models, physical IBM."""
import os
import threading
import time
from pathlib import Path
from qchat.ibm import QuantumCancelled, QuantumError
from qchat.amd_api import AMDError
from .job_store import JobStore, BudgetError, BusyError


class JobManager:
    def __init__(self, engine, runner, normalizer, state_dir, max_output=None):
        self.engine, self.runner, self.normalizer = engine, runner, normalizer
        self.store = JobStore(Path(state_dir) / 'jobs.sqlite3')
        self.max_output = int(max_output or os.getenv('MAX_OUTPUT_STEPS', '16'))
        self.deadline_seconds = int(os.getenv('COMPARISON_WAIT_SECONDS', '7200'))
        self.lock = threading.Lock()
        if not 1 <= self.max_output <= 32 or not 60 <= self.deadline_seconds <= 86400:
            raise ValueError('Invalid comparison limits')
        self.recovered = self.store.recover(runner)

    def info(self):
        return {**self.engine.info(), 'amd': self.normalizer.info(),
                'quantum': self.runner.info(), 'accepting_jobs': self.recovered,
                'storage': os.getenv('STATE_STORAGE', 'ephemeral')}

    def create(self, request_id, prompt):
        from uuid import UUID
        prompt = prompt.strip()
        if not prompt or len(prompt) > 2000:
            raise ValueError('Invalid question')
        with self.lock:
            # The same UUID always addresses the same job, including after an
            # ambiguous HTTP response. The browser resumes GET, never POST.
            id = UUID(request_id).hex
            try:
                previous = self.get(id)
            except KeyError:
                previous = None
            if previous is None:
                if not self.recovered or not self.runner.accepting(force=True):
                    raise BusyError('A previous IBM workload is pending or its status is unavailable')
                if self.runner.request_exists(id):
                    raise BusyError('Previous job exists at IBM; local state is no longer available')
            id, created = self.store.create(request_id, prompt)
            if created:
                threading.Thread(target=self.run, args=(id, prompt), daemon=True).start()
        return self.get(id)

    def get(self, id):
        data = self.store.get(id)
        data['ibm_jobs'] = self.store.traces(id)
        return data

    def cancel(self, id):
        self.store.cancel(id)
        return self.get(id)

    def run(self, id, prompt):
        began = time.monotonic()
        pending, step = None, 0
        generated = []
        try:
            self.store.update(id, status='running', stage='amd_normalizing', runtime=self.info())
            if self.store.cancelled(id):
                raise QuantumCancelled('Cancelled')
            normalized, amd = self.normalizer.normalize(prompt)
            self.store.update(id, amd=amd, normalized_prompt=normalized)
            if self.store.cancelled(id):
                raise QuantumCancelled('Cancelled')
            if normalized is None:
                self.store.update(id, status='unsupported', stage='unsupported')
                return
            self.store.update(id, stage='classical')
            classical = self.engine.generate('classical', normalized, self.max_output)
            classical['end_to_end_ms'] = amd['elapsed_ms'] + classical['elapsed_ms']
            self.store.update(id, classical=classical, stage='ibm_submitting')

            def evaluate(angles, theta):
                nonlocal pending, step
                step += 1
                values, reservation, ibm_id, trace = self.runner.evaluate(
                    angles, theta, self.store, id, step, began + self.deadline_seconds)
                pending = (reservation, ibm_id, trace)
                return values

            def consumed(next_id):
                nonlocal pending
                if pending is None:
                    raise QuantumError('Missing physical measurement')
                reservation, ibm_id, trace = pending
                trace.update(consumed_by_model=True, generated_token_id=int(next_id))
                self.store.record(reservation, ibm_id, 'DONE', trace)
                generated.append(int(next_id))
                self.store.update(id, hybrid_partial={'text': self.engine.tokenizer.decode(generated)})
                pending = None

            hybrid = self.engine.generate('hybrid', normalized, self.max_output,
                                          core_evaluator=evaluate, step_observer=consumed)
            hybrid['end_to_end_ms'] = amd['elapsed_ms'] + hybrid['elapsed_ms']
            traces = self.store.traces(id)
            verified = bool(traces) and len(traces) == hybrid['generated_tokens'] and all(
                t.get('ibm_job_id') and t['status'] == 'DONE' and t.get('simulator') is False
                and t.get('consumed_by_model') is True for t in traces)
            if not verified:
                raise QuantumError('Physical provenance is incomplete')
            result = {'prompt': prompt, 'normalized_prompt': normalized, 'amd': amd,
                      'classical': classical, 'hybrid': hybrid,
                      'physical_quantum_hardware': True, 'amd_verified': False,
                      'amd_api_call_succeeded': True, 'ibm_backend': self.runner.backend_name,
                      'ibm_jobs': traces, 'repeats': 1,
                      'comparison_wall_ms': (time.monotonic() - began) * 1000,
                      'timing_note': 'AMD normalization is performed once and shared. Model times exclude this common step. End-to-end per-path time adds AMD to each model. The pair runs sequentially; total wall time is also reported. Hybrid includes IBM queue, submission, execution, network and CPU. No simulator fallback.',
                      'quality_score': None,
                      'quality_note': 'Physical participation is not evidence of speed or quality advantage. Models use different learned weights; this is not an isolated causal test of the circuit.'}
            self.store.update(id, status='completed', stage='completed', result=result)
        except QuantumCancelled:
            self.store.update(id, status='cancelled', stage='cancelled', error_code='cancelled')
        except BudgetError:
            self.store.update(id, status='failed', stage='failed', error_code='daily_limit')
        except AMDError as exc:
            self.store.update(id, status='failed', stage='failed', error_code=exc.code)
        except Exception:
            self.store.update(id, status='failed', stage='failed', error_code='ibm_failed')
