"""Creates a local-only .env. Never paste this file into a public repository."""
import os,re,secrets
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'.env'
if path.exists():raise SystemExit('.env already exists. Edit it locally; refusing to replace existing credentials.')
domain=input('AMD API hostname (e.g. api.amd-quant.com), without https://: ').strip()
if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?',domain) or '.' not in domain:raise SystemExit('Use a valid public hostname.')
image=input('AMD PyTorch image recommended by your GPU provider [rocm/pytorch:latest]: ').strip() or 'rocm/pytorch:latest'
if not re.fullmatch(r'rocm/pytorch[:@][a-zA-Z0-9_.:@-]+',image):raise SystemExit('Expected an official rocm/pytorch image tag or digest.')
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:f.write(f'AMD_DOMAIN={domain}\nAMD_ENGINE_TOKEN={secrets.token_urlsafe(36)}\nROCM_IMAGE={image}\n')
print('Created private .env (permissions 600). Copy AMD_ENGINE_TOKEN from that file into Render AMD_API_TOKEN. Do not commit it.')
