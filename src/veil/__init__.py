"""Veil (Ω-10), the Liminal Boundary Regulator.

The initial package provides an isolated signal ledger and lifecycle primitives.
It intentionally has no Canonical Vault write client.
"""

from .models import Disposition, Observation, SignalRecord, TransitionProposal
from .store import VeilStore

__all__ = [
    "Disposition",
    "Observation",
    "SignalRecord",
    "TransitionProposal",
    "VeilStore",
]

__version__ = "0.1.0"
