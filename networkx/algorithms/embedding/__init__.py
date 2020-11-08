"""
Subpackages related to embedding (i.e. minor) problems.

TODO
----
- [ ] should this be combined with the minors sub-package?

"""

__devnotes__ = """


tree_embedding.py - defines reduction from tree problem to balanced sequence
problems.

CommandLine
-----------
# Run all tests in this subpackage
pytest networkx/algorithms/embedding --doctest-modules

# Autogenerate the `__init__.py` file for this subpackage with `mkinit`.
mkinit ~/code/networkx/networkx/algorithms/embedding/__init__.py -w
"""

__submodules__ = [
    "tree_embedding",
]

from networkx.algorithms.embedding import tree_embedding

from networkx.algorithms.embedding.tree_embedding import (
    maximum_common_ordered_tree_embedding,
)

__all__ = ["maximum_common_ordered_tree_embedding", "tree_embedding"]
