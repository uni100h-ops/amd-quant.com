"""Small causal Transformer with matched classical / state-vector FFN cores.

The hybrid core simulates RY gates and a CNOT ring exactly. It is classical
computation of a quantum circuit, not execution on a physical quantum processor.
Only four measured Z expectations return to the classical network.
"""
from dataclasses import dataclass, asdict
import math
import torch
from torch import nn
from torch.nn import functional as F


@dataclass
class Config:
    vocab_size: int
    context: int = 48
    width: int = 48
    heads: int = 3
    qubits: int = 4
    depth: int = 2


class QuantumCore(nn.Module):
    def __init__(self, qubits=4, depth=2):
        super().__init__()
        if not 2 <= qubits <= 8:
            raise ValueError('This implementation supports 2–8 simulated qubits.')
        self.qubits, self.depth = qubits, depth
        self.theta = nn.Parameter(torch.randn(depth, qubits) * 0.05)
        size = 2 ** qubits
        self.register_buffer('zero', F.one_hot(torch.tensor(0), size).float(), persistent=False)
        indices = torch.arange(size)
        signs = torch.stack([1 - 2 * ((indices >> (qubits - 1 - q)) & 1) for q in range(qubits)]).float()
        self.register_buffer('signs', signs, persistent=False)
        for control in range(qubits):
            target = (control + 1) % qubits
            permutation = indices ^ (((indices >> (qubits - 1 - control)) & 1) << (qubits - 1 - target))
            self.register_buffer(f'cx_{control}', permutation, persistent=False)

    def ry(self, state, angle, wire):
        # q0 is the most significant bit; batched real amplitudes.
        shape = state.shape
        pair = state.reshape(-1, 2 ** wire, 2, 2 ** (self.qubits-wire-1))
        c, s = torch.cos(angle / 2).reshape(-1, 1, 1), torch.sin(angle / 2).reshape(-1, 1, 1)
        a, b = pair[:, :, 0, :], pair[:, :, 1, :]
        return torch.stack((c*a-s*b, s*a+c*b), dim=2).reshape(shape)

    def statevector(self, angles):
        x = angles.reshape(-1, self.qubits)
        state = self.zero.to(x).expand(len(x), -1)
        for q in range(self.qubits):
            state = self.ry(state, x[:, q], q)
        for layer in range(self.depth):
            for q in range(self.qubits):
                state = self.ry(state, self.theta[layer, q].expand(len(x)), q)
            for q in range(self.qubits):
                state = state[:, getattr(self, f'cx_{q}')]
        return state

    def forward(self, angles):
        state = self.statevector(angles)
        return (state.square() @ self.signs.to(state).T).reshape(angles.shape)


class ClassicalCore(nn.Module):
    """Same number of learned core scalars as the quantum core (depth*qubits).

Fixed dense orthogonal mixing plus learned biases and tanh; avoids granting
either variant extra learned core parameters. Not an optimized LLM baseline.
"""
    def __init__(self, qubits=4, depth=2):
        super().__init__()
        self.theta = nn.Parameter(torch.randn(depth, qubits) * 0.05)
        q = torch.arange(qubits).float()
        mixing = torch.cos(math.pi / qubits * (q[:, None] + .5) * q[None, :])
        mixing[:, 0] *= 1 / math.sqrt(2)
        mixing *= math.sqrt(2 / qubits)
        self.register_buffer('mixing', mixing, persistent=False)

    def forward(self, angles):
        x = angles / math.pi
        for theta in self.theta:
            x = torch.tanh(x @ self.mixing + theta)
        return x


class MicroLM(nn.Module):
    def __init__(self, config: Config, variant: str):
        super().__init__()
        if variant not in ('classical', 'hybrid'):
            raise ValueError('Unknown model variant')
        self.config, self.variant = config, variant
        c = config
        self.token = nn.Embedding(c.vocab_size, c.width)
        self.position = nn.Embedding(c.context, c.width)
        self.ln1, self.ln2, self.lnf = [nn.LayerNorm(c.width) for _ in range(3)]
        self.qkv = nn.Linear(c.width, 3*c.width)
        self.attn_out = nn.Linear(c.width, c.width)
        self.down = nn.Linear(c.width, c.qubits)
        self.core = QuantumCore(c.qubits, c.depth) if variant == 'hybrid' else ClassicalCore(c.qubits, c.depth)
        self.up = nn.Linear(c.qubits, c.width)
        self.head = nn.Linear(c.width, c.vocab_size)

    def forward(self, tokens, ablate=False, core_evaluator=None):
        c = self.config
        b, length = tokens.shape
        if length > c.context:
            raise ValueError('Context length exceeded')
        x = self.token(tokens) + self.position(torch.arange(length, device=tokens.device))
        q, k, v = self.qkv(self.ln1(x)).chunk(3, dim=-1)
        def split(t):
            return t.view(b, length, c.heads, c.width//c.heads).transpose(1, 2)
        q, k, v = map(split, (q,k,v))
        scores = q @ k.transpose(-2,-1) / math.sqrt(c.width//c.heads)
        mask = torch.ones(length,length,device=tokens.device,dtype=torch.bool).triu(1)
        scores = scores.masked_fill(mask, -float('inf'))
        attention = (scores.softmax(-1) @ v).transpose(1,2).reshape(b,length,c.width)
        x = x + self.attn_out(attention)
        angles = math.pi * torch.tanh(self.down(self.ln2(x)))
        if core_evaluator is not None:
            if self.variant != 'hybrid' or ablate or b != 1:
                raise ValueError('Hardware core requires one non-ablated hybrid sequence')
            # Only the final position contributes to the next output. Attention has
            # already mixed the entire context; later operations are positionwise.
            # No simulated QuantumCore.forward/statevector is called on this path.
            values = core_evaluator(angles[0, -1].detach().cpu().tolist(),
                                    self.core.theta.detach().cpu().tolist())
            core = torch.as_tensor(values, device=x.device, dtype=x.dtype).reshape(1, 1, c.qubits)
            if not torch.isfinite(core).all():raise ValueError('Invalid hardware measurements')
            x = x[:, -1:, :]
        else:
            core = torch.zeros_like(angles) if ablate else self.core(angles)
        x = x + self.up(core)
        return self.head(self.lnf(x))

    def export(self):
        return {'config': asdict(self.config), 'variant': self.variant,
                'parameters': sum(p.numel() for p in self.parameters()),
                'weights': {k: v.detach().cpu().tolist() for k,v in self.state_dict().items()}}
