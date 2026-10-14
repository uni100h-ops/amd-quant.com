"""Physical IBM QPU adapter. No simulator backend and no fallback path."""
import hashlib,json,math,os,time
from datetime import datetime,timezone
import numpy as np

class QuantumError(RuntimeError):pass
class QuantumCancelled(QuantumError):pass

def circuit_template(theta):
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    theta=np.asarray(theta,dtype=float)
    if theta.ndim!=2 or theta.shape[1]!=4 or not np.isfinite(theta).all():raise ValueError('Expected trained four-qubit angles')
    inputs=ParameterVector('input',4);circuit=QuantumCircuit(4)
    for q in range(4):circuit.ry(inputs[q],q)
    for layer in theta:
        for q in range(4):circuit.ry(float(layer[q]),q)
        for q in range(4):circuit.cx(q,(q+1)%4)
    circuit.measure_all()
    return circuit,inputs

def expectations_from_counts(counts):
    if not counts:raise QuantumError('Empty IBM measurement result')
    total=0;values=np.zeros(4,dtype=float)
    for bits,count in counts.items():
        if not isinstance(bits,str) or len(bits)!=4 or any(c not in '01' for c in bits):raise QuantumError('Unexpected IBM register ordering')
        if not isinstance(count,(int,np.integer)) or count<0:raise QuantumError('Invalid IBM counts')
        total+=int(count)
        # Qiskit bit strings are c3,c2,c1,c0; our output is q0,q1,q2,q3.
        values+=int(count)*np.array([1 if bits[-1-q]=='0' else -1 for q in range(4)])
    if total<=0:raise QuantumError('No IBM measurements')
    return (values/total).tolist(),total

class IBMRunner:
    def __init__(self):
        from qiskit_ibm_runtime import QiskitRuntimeService,IBMBackend,SamplerV2
        from qiskit.transpiler import generate_preset_pass_manager
        token=os.environ.get('IBM_QUANTUM_API_KEY','')
        instance=os.environ.get('IBM_QUANTUM_INSTANCE','')
        backend_name=os.environ.get('IBM_QUANTUM_BACKEND','')
        if not token or not instance or not backend_name:raise QuantumError('Configure IBM API key, instance CRN and physical backend')
        self.shots=int(os.environ.get('IBM_SHOTS','1024'))
        self.max_execution=int(os.environ.get('IBM_MAX_EXECUTION_SECONDS','60'))
        self.wait_seconds=int(os.environ.get('IBM_WAIT_SECONDS','3600'))
        self.daily_limit=int(os.environ.get('IBM_MAX_JOBS_PER_DAY','32'))
        if not 128<=self.shots<=8192 or not 1<=self.max_execution<=600 or not 30<=self.wait_seconds<=86400 or self.daily_limit<1:raise QuantumError('Invalid IBM limits')
        self.service=QiskitRuntimeService(channel='ibm_quantum_platform',token=token,instance=instance)
        self.backend=self.service.backend(backend_name)
        if not isinstance(self.backend,IBMBackend) or self.backend.configuration().simulator or self.backend.num_qubits<4:
            raise QuantumError('A physical IBM backend with at least four qubits is required')
        if not self.backend.status().operational:raise QuantumError('Selected IBM backend is not operational')
        self.backend_name=self.backend.name
        self.pass_manager=generate_preset_pass_manager(optimization_level=1,backend=self.backend,seed_transpiler=42)
        self.sampler=SamplerV2(mode=self.backend,options={'default_shots':self.shots,'max_execution_time':self.max_execution})
        self.cache={}
    def info(self):
        return {'provider':'IBM Quantum','backend':self.backend_name,'simulator':False,'configured':True,'execution_verified':False,'logical_qubits':4,'shots':self.shots}
    def cancel_remote(self,id):
        job=self.service.job(id);status=str(job.status())
        if status not in ('DONE','CANCELLED','ERROR'):
            job.cancel();status=str(job.status())
        return status
    def evaluate(self,angles,theta,store,request_job_id,step,deadline):
        if store.cancelled(request_job_id):raise QuantumCancelled('Cancelled')
        if time.monotonic()>=deadline:raise QuantumError('Comparison deadline exceeded')
        if len(angles)!=4 or not all(math.isfinite(x) for x in angles):raise QuantumError('Invalid model input')
        key=hashlib.sha256(json.dumps(theta,separators=(',',':')).encode()).hexdigest()
        if key not in self.cache:
            template,parameters=circuit_template(theta)
            self.cache[key]=(self.pass_manager.run(template),parameters)
        template,parameters=self.cache[key]
        circuit=template.assign_parameters(dict(zip(parameters,map(float,angles))))
        reservation=store.reserve(request_job_id,self.daily_limit)
        tag='amdquant-'+request_job_id
        self.sampler.options.environment.job_tags=['amdquant',tag]
        trace={'backend':self.backend_name,'simulator':False,'step':step,'logical_qubits':4,'requested_shots':self.shots,'angles':list(angles),'trained_angles_sha256':key,'submitted_at':datetime.now(timezone.utc).isoformat(),'consumed_by_model':False,'transpiled_depth':circuit.depth(),'transpiled_operations':dict(circuit.count_ops())}
        job=None;started=time.monotonic()
        try:
            # Never automatically retry submission: an ambiguous network failure can
            # mean IBM accepted the job. Reserve budget first and persist ID at once.
            job=self.sampler.run([circuit],shots=self.shots)
            ibm_id=job.job_id();store.record(reservation,ibm_id,'SUBMITTED',trace)
            limit=min(deadline,time.monotonic()+self.wait_seconds)
            previous=None
            while True:
                status=str(job.status())
                if status!=previous:
                    store.record(reservation,ibm_id,status,trace)
                    store.update(request_job_id,stage='ibm_'+status.lower(),step=step,ibm_job_id=ibm_id,ibm_backend=self.backend_name)
                    previous=status
                if status=='DONE':break
                if status in ('ERROR','CANCELLED'):raise QuantumError('IBM job did not complete')
                if store.cancelled(request_job_id):raise QuantumCancelled('Cancelled')
                if time.monotonic()>=limit:raise QuantumError('IBM queue or execution deadline exceeded')
                time.sleep(3)
            actual=job.backend()
            if actual is None or actual.name!=self.backend_name or actual.configuration().simulator:raise QuantumError('IBM result backend mismatch')
            pub=job.result(timeout=30)[0]
            counts=pub.data.meas.get_counts();values,shots=expectations_from_counts(counts)
            if shots!=self.shots:raise QuantumError('IBM returned an unexpected measurement count')
            trace.update(counts={k:int(v) for k,v in counts.items()},z_expectations=values,actual_shots=shots,wall_ms=(time.monotonic()-started)*1000,completed_at=datetime.now(timezone.utc).isoformat())
            try:
                metrics=job.metrics();trace['qpu_usage_seconds']=metrics.get('usage',{}).get('quantum_seconds');trace['provider_timestamps']=metrics.get('timestamps',{})
            except Exception:trace['qpu_usage_seconds']=None
            store.record(reservation,ibm_id,'DONE',trace)
            return values,reservation,ibm_id,trace
        except Exception as exc:
            if job is None:
                store.mark_unresolved();trace['submission_uncertain']=True
                store.record(reservation,None,'UNKNOWN',trace)
            else:
                try:
                    status=str(job.status())
                    if status not in ('DONE','ERROR','CANCELLED'):job.cancel();status=str(job.status())
                except Exception:status='UNKNOWN'
                if status not in ('DONE','ERROR','CANCELLED'):store.mark_unresolved()
                store.record(reservation,job.job_id(),status,trace)
            if isinstance(exc,QuantumCancelled):raise
            raise QuantumError('IBM execution failed; no simulated result was used') from None
