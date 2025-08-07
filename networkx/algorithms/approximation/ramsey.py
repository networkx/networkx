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

    while stack:
        graph, clique, indep = stack.pop()

        if not graph:
            # Graph is empty, no more nodes to distribute.
            best_clique = max(best_clique, clique, key=len)
            best_indep = max(best_indep, indep, key=len)
        else:
            # Pick arbitrary node and create subproblems.
            node = nx.utils.arbitrary_element(graph)

            # Push subproblems: node to indep set in first, to clique in second.
            non_nbrs = nx.non_neighbors(graph, node)
            if len(best_indep) <= len(non_nbrs) + len(indep):
                non_nbr_graph = graph.subgraph(non_nbrs).copy()
                stack.append((non_nbr_graph, clique, indep | {node}))

            nbrs = set(nx.neighbors(graph, node)) - {node}
            if len(best_clique) <= len(nbrs) + len(clique):
                nbr_graph = graph.subgraph(nbrs).copy()
                stack.append((nbr_graph, clique | {node}, indep))

    return best_clique, best_indep
