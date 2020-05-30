"""
Algorithm for testing d-separation in DAGs.

*d-separation* is a test for conditional independence in probability
distributions that can be factorized using DAGs.  It is a purely
graphical test that uses the underlying graph and makes no reference
to the actual distribution parameters.  For a detailed treatment see
[1]_, [2]_.
"""

from collections import deque
from typing import Hashable, AbstractSet

import networkx as nx
from networkx.utils import not_implemented_for, UnionFind

__all__ = ["d_separated"]


@not_implemented_for("undirected")
def d_separated(G: nx.DiGraph, x: AbstractSet[Hashable],
                y: AbstractSet[Hashable], z: AbstractSet[Hashable]) -> bool:
    """
    Return whether node sets ``x`` and ``y` are separated by ``z``.

    Parameters
    ----------
    G : graph
        A NetworkX DAG.

    x : set
        First set of nodes in ``G``.

    y : set
        Second set of nodes in ``G``.

    z : set
        Set of conditioning nodes in `G`.

    Returns
    -------
    bool : True if ``x`` is d-separated from ``y`` given ``z`` in ``G``.

    Raises
    ------
    NetworkXError
        The *d-separation* test is commonly used with directed
        graphical models which are acyclic.  Accordingly, the algorithm
        raises a :exc:`NetworkXError` if the input graph is not a DAG.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    Examples
    --------
    >>> import networkx as nx
    >>> g = nx.path_graph(10, nx.DiGraph)
    >>> assert nx.d_separated(g, {0,1,2,3}, {5,6,7,8,9}, {4})

    Notes
    -----
    While there are other algorithms for testing *d-separation* (for
    e.g. [3]_), the algorithm presented in [1]_ is perhaps the simplest
    linear time algorithm and is therefore used in this implementation.


    References
    ----------
    ..  [1] Darwiche, A.  (2009).  Modeling and reasoning with
        Bayesian networks.  Cambridge: Cambridge University Press.

    ..  [2] Pearl, J. (2009). Causality. Cambridge: Cambridge University Press.

    ..  [2] Shachter, R. D. (1998). Bayes-ball: rational pastime (for
        determining irrelevance and requisite information in belief networks
        and influence diagrams). In , Proceedings of the Fourteenth Conference
        on Uncertainty in Artificial Intelligence (pp. 480–487). San
        Francisco, CA, USA: Morgan Kaufmann Publishers Inc.

    """

    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xyz = x.union(y).union(z)

    if any((n not in G.nodes for n in union_xyz)):
        raise nx.NodeNotFound(
            "one or more specified nodes not found in the graph")

    G_copy = G.copy()

    # transform the graph by removing leaves that are not in x | y | z
    # until no more leaves can be removed.
    leaves = deque([n for n in G_copy.nodes if G_copy.out_degree[n] == 0])
    while len(leaves) > 0:
        leaf = leaves.popleft()
        if leaf not in union_xyz:
            for p in G_copy.predecessors(leaf):
                if G_copy.out_degree[p] == 1:
                    leaves.append(p)
            G_copy.remove_node(leaf)

    # transform the graph by removing outgoing edges from the
    # conditioning set.
    edges_to_remove = list(G_copy.out_edges(z))
    G_copy.remove_edges_from(edges_to_remove)

    # use disjoint-set data structure to check if any node in `x`
    # occurs in the same weakly connected component as a node in `y`.
    disjoint_set = UnionFind(G_copy.nodes())
    for component in nx.weakly_connected_components(G_copy):
        disjoint_set.union(*component)
    disjoint_set.union(*x)
    disjoint_set.union(*y)

    if x and y and disjoint_set[next(iter(x))] == disjoint_set[next(iter(y))]:
        return False
    else:
        return True
