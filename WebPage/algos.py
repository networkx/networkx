# algos.py
"""
Thin wrapper so we can `from algos import minimal_fraction_max_matching`
without touching the NetworkX namespace elsewhere in the app.
"""
from networkx.algorithms.matching import minimal_fraction_max_matching  # type: ignore

__all__ = ["minimal_fraction_max_matching"]
