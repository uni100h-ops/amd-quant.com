"""Inference for the original Micro checkpoints, without PyTorch or a simulator.

Only the final position is needed: this model has ONE attention block, followed
by position-wise operations. The hybrid path always requires an external core.
"""
import hashlib
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from .text import Tokenizer


class MicroEngine:
    def __init__(self, directory):
        self.models = {}
        self.metadata = {}
        for variant in ('classical', 'hybrid'):
            raw = (Path(directory) / f'{variant}.json').read_bytes()
            data = json.loads(raw)
            if data['variant'] != variant:
                raise ValueError('Checkpoint variant mismatch')
            if self.models and data['vocabulary'] != self.tokenizer.vocabulary:
                raise ValueError('Checkpoint vocabulary mismatch')
            self.tokenizer = Tokenizer(data['vocabulary'])
            self.models[variant] = SimpleNamespace(
                config=SimpleNamespace(**data['config']),
                weights={k: np.asarray(v, dtype=np.float32) for k, v in data['weights'].items()})
            self.metadata[variant] = {k: v for k, v in data.items() if k not in ('weights', 'vocabulary')}
            self.metadata[variant]['sha256'] = hashlib.sha256(raw).hexdigest()
        c = self.models['classical'].config
        q = np.arange(c.qubits, dtype=np.float32)
        self.mixing = np.cos(np.float32(math.pi / c.qubits) * (q[:, None] + .5) * q[None, :])
        self.mixing[:, 0] *= np.float32(1 / math.sqrt(2))
        self.mixing *= np.float32(math.sqrt(2 / c.qubits))

    def info(self):
        return {'profile': 'micro', 'ready': True, 'device': 'cpu', 'gpu': None,
                'rocm': None, 'amd_verified': False, 'models': self.metadata,
                'physical_quantum_hardware': False,
                'scope': 'Original Micro weights. CPU inference; physical IBM core in the hybrid variant. AMD API performs shared question normalization.'}

    def logits(self, variant, ids, core_evaluator=None):
        model = self.models[variant]
        w, c = model.weights, model.config
        def linear(x, name):
            return x @ w[name + '.weight'].T + w[name + '.bias']
        def norm(x, name):
            mean = x.mean(axis=-1, keepdims=True)
            variance = ((x - mean) ** 2).mean(axis=-1, keepdims=True)
            return (x - mean) / np.sqrt(variance + np.float32(1e-5)) * w[name + '.weight'] + w[name + '.bias']
        length = len(ids)
        x = w['token.weight'][ids] + w['position.weight'][:length]
        q, k, v = np.split(linear(norm(x, 'ln1'), 'qkv'), 3, axis=-1)
        head_width = c.width // c.heads
        q, k, v = [a.reshape(length, c.heads, head_width).transpose(1, 0, 2) for a in (q, k, v)]
        scores = q[:, -1:, :] @ k.transpose(0, 2, 1) / np.float32(math.sqrt(head_width))
        weights = np.exp(scores - scores.max(axis=-1, keepdims=True))
        weights /= weights.sum(axis=-1, keepdims=True)
        attention = (weights @ v).transpose(1, 0, 2).reshape(1, c.width)
        x = x[-1:] + linear(attention, 'attn_out')
        angles = np.float32(math.pi) * np.tanh(linear(norm(x, 'ln2'), 'down'))
        if variant == 'hybrid':
            if core_evaluator is None:
                raise ValueError('Physical IBM core is required; no simulator fallback')
            core = np.asarray(core_evaluator(angles[0].tolist(), w['core.theta'].tolist()), dtype=np.float32)
            if core.shape != (4,) or not np.isfinite(core).all() or (np.abs(core) > 1.00001).any():
                raise ValueError('Invalid IBM measurements')
            core = core[None, :]
        else:
            if core_evaluator is not None:
                raise ValueError('Classical model does not accept a quantum core')
            core = angles / np.float32(math.pi)
            for theta in w['core.theta']:
                core = np.tanh(core @ self.mixing + theta)
        return linear(norm(x + linear(core, 'up'), 'lnf'), 'head')[0]

    def generate(self, variant, prompt, max_tokens=16, core_evaluator=None, step_observer=None):
        c = self.models[variant].config
        tokens = self.tokenizer.prompt(prompt)
        if len(tokens) > c.context or not 1 <= max_tokens <= 32:
            raise ValueError('Invalid generation limits')
        ids, generated, first_ms = tokens[:], [], None
        start = time.perf_counter()
        for _ in range(max_tokens):
            next_id = int(self.logits(variant, ids[-c.context:], core_evaluator).argmax())
            if step_observer:
                step_observer(next_id)
            if first_ms is None:
                first_ms = (time.perf_counter() - start) * 1000
            ids.append(next_id)
            generated.append(next_id)
            if next_id == 4:
                break
        elapsed = (time.perf_counter() - start) * 1000
        return {'variant': variant, 'text': self.tokenizer.decode(generated),
                'token_ids': generated, 'generated_tokens': len(generated),
                'ttft_ms': first_ms, 'elapsed_ms': elapsed,
                'stop_reason': 'eos' if generated[-1] == 4 else 'max_tokens',
                'checkpoint_sha256': self.metadata[variant]['sha256'],
                'max_tokens': max_tokens, 'decoding': 'greedy', 'device': 'cpu', 'profile': 'micro'}
