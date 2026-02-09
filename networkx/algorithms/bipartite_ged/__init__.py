"""
This module allows to compute an upper bound
of the **Graph Edit Distance** (*GED*).

This bipartite *GED* approximation algorithm is based on
*Structural Pattern Recognition with Graph Edit Distance* [1]_.

It uses a node matching between the graphs to
approximate the *GED*, by solving a Linear Sum
Assignment Problem (*LSAP*) instead of a
Quadratic Assignment Problem.

A *LSAP* can be solved by using a cost matrix
containing the assignment cost of each pair of
nodes, with which we want to minimize the
final assignment cost [2]_.

This implementation offers some cost functions to build
the cost matrix, each gathering more or less local
structural information to improve the matching.

Example :

>>> import networkx as nx
>>> g1, g2 = nx.Graph(), nx.Graph()
>>> g1.add_nodes_from(
...     [
...         ("u1", {"Label": 1}),
...         ("u2", {"Label": 2}),
...         ("u3", {"Label": 1}),
...         ("u4", {"Label": 3}),
...     ]
... )
>>> g1.add_edges_from(
...     [
...         ("u1", "u2", {"edge_attr": 1}),
...         ("u2", "u3", {"edge_attr": 2}),
...         ("u2", "u4", {"edge_attr": 1}),
...         ("u3", "u4", {"edge_attr": 1}),
...     ]
... )
>>> g2.add_nodes_from(
...     [("v1", {"Label": 3}), ("v2", {"Label": 2}), ("v3", {"Label": 3})]
... )
>>> g2.add_edges_from([("v1", "v2", {"edge_attr": 1}), ("v2", "v3", {"edge_attr": 1})])
>>> # Here we use a basic constant cost function with all edit costs to 1
>>> # We also use custom functions to evaluate nodes and edges similarities
>>> bpged = nx.BipartiteGED(
...     "const",
...     1,
...     1,
...     1,
...     1,
...     lambda u, v, g1, g2: g1.nodes[u]["Label"] == g2.nodes[v]["Label"],
...     lambda e1, e2, g1, g2: g1[e1[0]][e1[1]]["edge_attr"]
...     == g2[e2[0]][e2[1]]["edge_attr"],
... )
>>> bpged.ged(g1, g2)
4

References
----------
.. [1] K. Riesen, Structural Pattern Recognition with
   Graph Edit Distance, Switzerland, Springer, 2015,
   ISBN : 978-3-319-27251-1, https://doi.org/10.1007/978-3-319-27252-8

.. [2] Linear Sum Assignment Problem, Wikipedia,
   https://en.wikipedia.org/wiki/Assignment_problem


See Also
--------

`scipy.optimize.linear_sum_assignment`
   An easy to use function to solve the *LSAP*
`networkx.algorithms.bipartite_ged.costfunctions`
   Some cost functions classes for node matching
`networkx.algorithms.bipartite_ged.solvers`
   Some *LSAP* solvers classes
`networkx.algorithms.similarity.graph_edit_distance`
   The `networkx` function to compute exact graph edit distance
"""

from .costfunctions import (
    ConstantCostFunction,
    RiesenCostFunction,
    NeighborhoodCostFunction,
)
from .solvers import SolverLSAP
from .bpged_utils import compute_bipartite_cost_matrix, convert_mapping
from networkx.algorithms.bipartite_ged.bipartite_ged import *
