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
    r"""Compute the largest clique and largest independent set in `G`.

    This can be used to estimate bounds for the 2-color
    Ramsey number ``R(2; s, t)`` for `G`.

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
    stack = [(G.copy(), set(), set())]
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

            nbrs = set(nx.all_neighbors(graph, node)) - {node}
            nbr_graph = graph.subgraph(nbrs).copy()

            nnbrs = nx.non_neighbors(graph, node)
            nnbr_graph = graph.subgraph(nnbrs).copy()

            # Push subproblems: node to clique in first, independent set in second.
            stack.append((nnbr_graph, clique, indep | {node}))
            stack.append((nbr_graph, clique | {node}, indep))

    return best_clique, best_indep
