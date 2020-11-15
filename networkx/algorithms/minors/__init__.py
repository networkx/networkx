"""
Subpackages related to graph-minor problems.

In graph theory, an undirected graph H is called a minor of the graph G if H
can be formed from G by deleting edges and vertices and by contracting edges
[1]_.

References
----------
.. [1] https://en.wikipedia.org/wiki/Graph_minor
"""

__devnotes__ = """
CommandLine
-----------
# Run all tests in this subpackage
pytest networkx/algorithms/minors --doctest-modules

# Autogenerate the `__init__.py` file for this subpackage with `mkinit`.
mkinit ~/code/networkx/networkx/algorithms/minors/__init__.py -w
"""

__submodules__ = [
    "contraction",
]

from networkx.algorithms.minors import contraction

from networkx.algorithms.minors.contraction import (
    contracted_edge,
    contracted_nodes,
    equivalence_classes,
    identified_nodes,
    quotient_graph,
)

__all__ = [
    "contracted_edge",
    "contracted_nodes",
    "contraction",
    "equivalence_classes",
    "identified_nodes",
    "quotient_graph",
]
