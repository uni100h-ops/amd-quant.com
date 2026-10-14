"""One durable comparison at a time; physical results feed the language model."""
import os,threading,time
from pathlib import Path
from qchat.ibm import QuantumCancelled,QuantumError
from .job_store import JobStore,BudgetError

class JobManager:
    def __init__(self,engine,runner,state_dir,max_output=None):
        self.engine=engine;self.runner=runner
        self.store=JobStore(Path(state_dir)/'jobs.sqlite3')
        self.max_output=int(max_output or os.getenv('MAX_OUTPUT_STEPS','12'))
        self.deadline_seconds=int(os.getenv('COMPARISON_WAIT_SECONDS','7200'))
        if not 1<=self.max_output<=32 or not 60<=self.deadline_seconds<=86400:raise ValueError('Invalid comparison limits')
        self.recovered=self.store.recover(runner)
    def info(self):
        return {**self.engine.info(),'quantum':self.runner.info(),'accepting_jobs':self.recovered,
                'physical_quantum_hardware':False,'scope':'Educational Micro models; physical IBM execution is verified separately for each completed response.'}
    def create(self,request_id,prompt):
        prompt=prompt.strip()
        if not prompt:raise ValueError('Enter a question')
        if len(self.engine.tokenizer.prompt(prompt))>self.engine.models['hybrid'].config.context:raise ValueError('Question exceeds the Micro context')
        id,created=self.store.create(request_id,prompt)
        if created:threading.Thread(target=self.run,args=(id,prompt),daemon=True).start()
        return self.get(id)
    def get(self,id):
        data=self.store.get(id);data['ibm_jobs']=self.store.traces(id);return data
    def cancel(self,id):self.store.cancel(id);return self.get(id)
    def run(self,id,prompt):
        began=time.monotonic();pending=None;step=0
        try:
            self.store.update(id,status='running',stage='classical',runtime=self.info())
            if self.store.cancelled(id):raise QuantumCancelled('Cancelled')
            classical=self.engine.generate('classical',prompt,self.max_output)
            self.store.update(id,classical=classical,stage='ibm_submitting')
            def evaluate(angles,theta):
                nonlocal pending,step
                step+=1
                values,reservation,ibm_id,trace=self.runner.evaluate(angles,theta,self.store,id,step,began+self.deadline_seconds)
                pending=(reservation,ibm_id,trace)
                return values
            def consumed(next_id):
                nonlocal pending
                if pending is None:raise QuantumError('Missing physical measurement')
                reservation,ibm_id,trace=pending
                trace.update(consumed_by_model=True,generated_token_id=int(next_id))
                self.store.record(reservation,ibm_id,'DONE',trace);pending=None
            hybrid=self.engine.generate('hybrid',prompt,self.max_output,core_evaluator=evaluate,step_observer=consumed)
            traces=self.store.traces(id)
            verified=bool(traces) and len(traces)==hybrid['generated_tokens'] and all(t.get('ibm_job_id') and t['status']=='DONE' and t.get('simulator') is False and t.get('consumed_by_model') is True for t in traces)
            if not verified:raise QuantumError('Physical measurement provenance is incomplete')
            result={'prompt':prompt,'classical':classical,'hybrid':hybrid,'physical_quantum_hardware':True,
                    'amd_verified':self.engine.info()['amd_verified'],'ibm_backend':self.runner.backend_name,
                    'ibm_jobs':traces,'repeats':1,'comparison_wall_ms':(time.monotonic()-began)*1000,
                    'timing_note':'One run per model. Hybrid elapsed time includes IBM submission, queue, execution, network and local computation. No simulator fallback or quantum warmup.',
                    'quality_score':None,'quality_note':'Physical QPU participation does not establish speed or quality advantage.'}
            self.store.update(id,status='completed',stage='completed',result=result)
        except QuantumCancelled:
            self.store.update(id,status='cancelled',stage='cancelled',error_code='cancelled')
        except BudgetError:
            self.store.update(id,status='failed',stage='failed',error_code='daily_limit')
        except Exception:
            # No provider exception, token, URL or stack trace is exposed to visitors.
            self.store.update(id,status='failed',stage='failed',error_code='ibm_failed',error='Comparison failed. No simulated replacement was used.')
