"""Collect IBM credentials locally, never in the web UI or GitHub."""
import getpass,os,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];directory=root/'.secrets';directory.mkdir(mode=0o700,exist_ok=True)
path=directory/'ibm.env'
if path.exists():raise SystemExit('.secrets/ibm.env already exists; edit it locally. Nothing was replaced.')
key=getpass.getpass('IBM Quantum API key (hidden): ').strip()
crn=input('IBM Quantum instance CRN: ').strip()
backend=input('Physical IBM backend name, exactly as shown in your account: ').strip()
if not re.fullmatch(r'[A-Za-z0-9_-]+',key):raise SystemExit('Invalid API key format')
if not crn.startswith('crn:') or any(c.isspace() for c in crn) or any(c in crn for c in "'$\"#\\"):raise SystemExit('Expected the complete instance CRN')
if not re.fullmatch(r'ibm_[a-z0-9_]+',backend):raise SystemExit('Expected a physical IBM backend name beginning with ibm_')
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:
    f.write(f'IBM_QUANTUM_API_KEY={key}\nIBM_QUANTUM_INSTANCE={crn}\nIBM_QUANTUM_BACKEND={backend}\nIBM_SHOTS=1024\nIBM_MAX_EXECUTION_SECONDS=60\nIBM_WAIT_SECONDS=3600\nIBM_MAX_JOBS_PER_DAY=32\n')
print('Saved private .secrets/ibm.env. No quantum jobs were submitted. Keep this file off GitHub and out of Render.')
