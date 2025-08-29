"""
Ramsey numbers.
"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["ramsey_R2"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def ramsey_R2(G):
    r"""Compute a maximum clique and maximum independent set in a graph.

    A clique/independent set is said to be maximum if it has the largest
    possible number of nodes. This can be used to estimate bounds for
    the 2-color Ramsey number ``R(2; s, t)`` for `G`.

    Self-loop edges are ignored.

    Parameters
    ----------
    G : NetworkX graph
        Undirected simple graph.

    Returns
    -------
    max_pair : (set, set) tuple
        Maximum clique, maximum independent set.

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.
    """
    # Stack entries: (subgraph, clique, independent set).
    stack = [(G, set(), set())]
    best_clique = set()
    best_indep = set()
    lbi = lbc = 0

    while stack:
        graph, clique, indep = stack.pop()

        if not graph:
            # Graph is empty, no more nodes to distribute.
            if lbc < len(clique):
                best_clique = clique
                lbc = len(best_clique)
            if lbi < len(indep):
                best_indep = indep
                lbi = len(best_indep)
        else:
            # Pick arbitrary node and create subproblems.
            node = nx.utils.arbitrary_element(graph)
            li, lc = len(indep), len(clique)

            # Push subproblems: node to indep set in first, to clique in second.
            non_nbrs = nx.non_neighbors(graph, node)
            if lbi < (lnn := len(non_nbrs)) + li + 1 or lbc < lnn + lc:
                non_nbr_graph = graph.subgraph(non_nbrs).copy()
                stack.append((non_nbr_graph, clique, indep | {node}))

            nbrs = set(nx.neighbors(graph, node)) - {node}
            if lbi < (ln := len(nbrs)) + li or lbc < ln + lc + 1:
                nbr_graph = graph.subgraph(nbrs).copy()
                stack.append((nbr_graph, clique | {node}, indep))

    return best_clique, best_indep
