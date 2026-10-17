"""Lightweight transport schemas. No numerical packages on Render."""
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

VERSION = '10.0.0'
SCHEMA = 'amdquant-qubo-v10'
TERMINAL = {'completed', 'failed', 'cancelled'}
KNOWN_ERRORS = {
    'structured_problem_required', 'invalid_problem_data', 'cancelled', 'gpu_unavailable', 'invalid_sb_solution', 'amd_gpu_required',
    'amd_rocm_required', 'gpu_verification_failed', 'gpu_tensor_mismatch',
    'objective_verification_failed', 'invalid_problem_json',
    'select_problem_or_configure_amd', 'amd_config', 'amd_auth', 'amd_quota',
    'amd_failed', 'amd_format', 'unsupported_problem', 'run_failed',
}

class RunRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: UUID
    question: str = Field(min_length=1, max_length=500000)
    seed: int = Field(default=2026, ge=0, le=2**31-4, strict=True)
    language: Literal['en', 'es', 'fr', 'de'] = 'en'

class WorkerInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: Literal['10.0.0']
    hardware: dict
    amd_configured: bool = Field(strict=True)

class Report(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(pattern=r'^[a-f0-9]{32}$')
    lease: str = Field(pattern=r'^[a-f0-9]{32}$')
    status: Literal['running', 'completed', 'failed', 'cancelled']
    stage: str = Field(max_length=80, pattern=r'^[a-z0-9_]+$')
    partial: dict | None = None
    result: dict | None = None
    issues: list[dict] = Field(default_factory=list, max_length=6)
    error: str | None = Field(default=None, max_length=80)

class PollRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    worker_id: UUID
    info: WorkerInfo
    report: Report | None = None

def amd_verified(hw):
    return isinstance(hw, dict) and hw.get('sb_gpu_vendor') == 'AMD ROCm' \
        and bool(hw.get('rocm_version')) and hw.get('sb_device') == 'cuda:0' \
        and isinstance(hw.get('sb_device_name'), str) and bool(hw['sb_device_name']) \
        and hw.get('gpu_execution_verified') is True and hw.get('cpu_fallback') is False

def result_verified(result):
    """Reject old CPU results or missing device evidence; authentication is separate."""
    if not isinstance(result, dict) or result.get('schema_version') != SCHEMA:
        return False
    if not amd_verified(result.get('hardware')):
        return False
    try:
        quantum = result['engines']['quantum']
        traditional = result['engines']['traditional']
        for engine in (quantum, traditional):
            if not all(k in engine for k in ('bits', 'decoded', 'energy', 'solver_ms',
                   'median_ms', 'trials', 'optimality_gap_absolute',
                   'optimality_gap_percent', 'at_proven_optimum')):
                return False
            if len(engine['trials']) != 3:
                return False
        for row in [quantum, *quantum['trials']]:
            if row.get('cpu_fallback') is not False or any(row.get(k) != 'cuda:0'
                    for k in ('matrix_device', 'solution_device', 'objective_device')):
                return False
        return all(k in result for k in ('problem', 'reference', 'comparison', 'protocol',
                                        'comparison_wall_ms', 'warmup_ms'))
    except (KeyError, TypeError):
        return False


def partial_verified(result):
    if not isinstance(result,dict) or result.get('schema_version')!=SCHEMA or not amd_verified(result.get('hardware')):
        return False
    engines=result.get('engines')
    if not isinstance(engines,dict) or not engines or not set(engines)<= {'traditional','quantum'}:
        return False
    if not all(k in result for k in ('problem','reference','protocol','warmup_ms','comparison_wall_ms')):
        return False
    for name,engine in engines.items():
        if not isinstance(engine,dict) or not all(k in engine for k in ('bits','decoded','energy','solver_ms','median_ms','trials','optimality_gap_absolute','optimality_gap_percent','at_proven_optimum')):
            return False
        if len(engine['trials'])!=3: return False
        if name=='quantum':
            for row in [engine,*engine['trials']]:
                if row.get('cpu_fallback') is not False or any(row.get(k)!='cuda:0' for k in ('matrix_device','solution_device','objective_device')):
                    return False
    return True
