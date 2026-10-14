"""Verify actual AMD ROCm execution. Does not submit an IBM job."""
import argparse,datetime,json,platform,subprocess,time
from pathlib import Path
import torch

def main():
    p=argparse.ArgumentParser();p.add_argument('--require-amd',action='store_true');p.add_argument('--output',default='/state/amd-hardware.json');a=p.parse_args()
    amd=bool(torch.version.hip and torch.cuda.is_available())
    if a.require_amd and not amd:raise SystemExit('No AMD ROCm GPU detected. Refusing to produce AMD evidence.')
    device='cuda' if amd else 'cpu';x=torch.randn(64,48,device=device,requires_grad=True);w=torch.randn(48,48,device=device)
    start=time.perf_counter();y=x@w;y.square().mean().backward()
    if amd:torch.cuda.synchronize()
    report={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),'torch':torch.__version__,'rocm':torch.version.hip,'device':device,'gpu':torch.cuda.get_device_name(0) if amd else None,'amd_verified':amd,'physical_quantum_hardware':False,'gpu_tensor_test_ok':bool(torch.isfinite(x.grad).all()),'elapsed_ms':1000*(time.perf_counter()-start),'note':'Actual tensor calculation on the selected device. This check is not an IBM hardware test or an independent certification.'}
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
