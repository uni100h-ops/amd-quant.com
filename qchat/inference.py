import hashlib, json, time
from pathlib import Path
import torch
from .model import Config, MicroLM
from .text import Tokenizer

def synchronize(device):
    if str(device).startswith('cuda'):torch.cuda.synchronize()

class MicroEngine:
    def __init__(self, directory, device='cpu'):
        self.directory=Path(directory);self.device=device;self.models={};self.metadata={}
        for variant in ('classical','hybrid'):
            path=self.directory/f'{variant}.json'
            raw=path.read_bytes();data=json.loads(raw)
            if data.get('variant')!=variant:raise ValueError('Checkpoint variant mismatch')
            if self.models and data['vocabulary']!=self.tokenizer.vocabulary:raise ValueError('Checkpoint vocabulary mismatch')
            model=MicroLM(Config(**data['config']),variant)
            model.load_state_dict({k:torch.tensor(v) for k,v in data['weights'].items()})
            self.models[variant]=model.to(device).eval()
            self.tokenizer=Tokenizer(data['vocabulary'])
            self.metadata[variant]={k:v for k,v in data.items() if k not in ('weights','vocabulary')}
            self.metadata[variant]['sha256']=hashlib.sha256(raw).hexdigest()

    def info(self):
        return {'profile':'micro','ready':True,'device':str(self.device),
            'gpu':torch.cuda.get_device_name(0) if str(self.device).startswith('cuda') else None,
            'rocm':torch.version.hip,
            'amd_verified':bool(str(self.device).startswith('cuda') and torch.version.hip),
            'physical_quantum_hardware':False,'models':self.metadata,
            'scope':'Small educational corpus: definitions, translation and single-digit addition. Not a general assistant.'}

    @torch.inference_mode()
    def generate(self, variant, prompt, max_tokens=32, ablate=False, core_evaluator=None, step_observer=None):
        model=self.models[variant];c=model.config
        tokens=self.tokenizer.prompt(prompt)
        if len(tokens)>c.context:raise ValueError(f'Prompt exceeds {c.context-2} tokens')
        ids=tokens[:];generated=[];first_ms=None
        synchronize(self.device);t0=time.perf_counter()
        for _ in range(max_tokens):
            logits=model(torch.tensor([ids[-c.context:]],device=self.device),ablate=ablate,core_evaluator=core_evaluator)
            next_id=int(logits[0,-1].argmax().item())
            if step_observer is not None:step_observer(next_id)
            synchronize(self.device)
            if first_ms is None:first_ms=(time.perf_counter()-t0)*1000
            generated.append(next_id);ids.append(next_id)
            if next_id==4:break
        synchronize(self.device);elapsed=(time.perf_counter()-t0)*1000
        return {'variant':variant,'text':self.tokenizer.decode(generated),'token_ids':generated,
            'generated_tokens':len(generated),'ttft_ms':first_ms,'elapsed_ms':elapsed,
            'tokens_per_second':len(generated)/(elapsed/1000) if elapsed else None,
            'prompt_tokens':len(tokens),'unknown_prompt_tokens':tokens.count(1),
            'stop_reason':'eos' if generated[-1]==4 else 'max_tokens','ablation':ablate,
            'checkpoint_sha256':self.metadata[variant]['sha256'],
            'max_tokens':max_tokens,'decoding':'greedy','device':str(self.device),'profile':'micro'}
