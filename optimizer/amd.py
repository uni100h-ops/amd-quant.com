"""Compatibility entry point; v10 accepts presets and validated JSON."""
from .specs import InputError, resolve_input
def configured():
    return False
def resolve(question, transport=None):
    return resolve_input(question)
