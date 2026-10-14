"""Explicit IBM hardware test; consumes the selected instance's quota or credit."""
import argparse,json,os,uuid
from pathlib import Path
import torch
from qchat.ibm import IBMRunner
from qchat.inference import MicroEngine
from server.ibm_jobs import JobManager

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt',default='what is a qubit?');p.add_argument('--steps',type=int,default=1,choices=range(1,13))
    p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    p.add_argument('--state-dir',default=os.getenv('STATE_DIR','/state'))
    p.add_argument('--ibm-env',default='.secrets/ibm.env')
    a=p.parse_args()
    private=Path(a.ibm_env)
    if private.exists():
        for line in private.read_text().splitlines():
            if not line.strip() or line.startswith('#'):continue
            key,separator,value=line.partition('=')
            if not separator or not key.startswith('IBM_'):raise SystemExit('Invalid IBM environment file')
            os.environ[key]=value
    if a.device=='cuda' and not (torch.version.hip and torch.cuda.is_available()):raise SystemExit('A real AMD ROCm GPU is required for --device cuda. Use --device cpu explicitly for an IBM-only test.')
    torch.set_num_threads(2)
    root=Path(__file__).resolve().parents[1];state=Path(a.state_dir)
    manager=JobManager(MicroEngine(root/'dist/models',a.device),IBMRunner(),state,max_output=a.steps)
    id,created=manager.store.create(str(uuid.uuid4()),a.prompt)
    print('Submitting physical IBM work. Application job:',id,flush=True)
    manager.run(id,a.prompt)
    report=manager.get(id);folder=state/'evidence';folder.mkdir(exist_ok=True)
    path=folder/f'ibm-{id}.json';path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2));print('Evidence file:',path)
    if report['status']!='completed' or report['result'].get('physical_quantum_hardware') is not True:raise SystemExit(1)
    print('PASS: physical IBM measurements fed the Micro model. Classical host:',a.device)
    print('One step is a hardware smoke test, not a complete answer or quality benchmark. CPU execution is not AMD GPU evidence.')
if __name__=='__main__':main()
