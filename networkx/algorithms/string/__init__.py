"""
Subpackages related to string based problems.
"""


__devnotes__ = """

balanced_sequence.py - core python implementations for the longest common
    balanced sequence subproblem, this is used by
    :module:`networkx.algorithms.embedding.tree_embedding`.

balanced_sequence_cython.pyx - faster alternative implementations for
    balanced_sequence.py

CommandLine
-----------
# Run all tests in this subpackage
pytest networkx/algorithms/string --doctest-modules

# Autogenerate the `__init__.py` file for this subpackage with `mkinit`.
mkinit networkx/networkx/algorithms/string/__init__.py -w
"""
from networkx.algorithms.string import balanced_sequence

from networkx.algorithms.string.balanced_sequence import (
    available_impls_longest_common_balanced_sequence,
    longest_common_balanced_sequence,
    random_balanced_sequence,
)

__all__ = [
    "available_impls_longest_common_balanced_sequence",
    "balanced_sequence",
    "longest_common_balanced_sequence",
    "random_balanced_sequence",
]
