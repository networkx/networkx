import networkx as nx
from networkx.algorithms.clique import find_cliques

__all__ = ["is_split_graph", "is_complete_split_graph"]


def is_split_graph(G: nx.Graph) -> bool:
    """
    Returns True if G is a split graph.

    A graph is split if it is chordal and its complement is also chordal.

    Parameters
    ----------
    G : networkx.Graph
        The input undirected graph.

    Returns
    -------
    bool
        True if G is a split graph, False otherwise.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Split_graph
    """
    return nx.is_chordal(G) and nx.is_chordal(nx.complement(G))


def is_complete_split_graph(G: nx.Graph) -> bool:
    """
    Returns True if G is a complete split graph.

    A complete split graph has a vertex set partitioned into:
    - a clique C,
    - an independent set I,
    such that every vertex in I is adjacent to all vertices in C.

    Parameters
    ----------
    G : networkx.Graph
        The input undirected graph.

    Returns
    -------
    bool
        True if G is a complete split graph, False otherwise.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Split_graph
    """
    if G.number_of_nodes() == 0:
        return True

    max_clique = max(find_cliques(G), key=len)
    clique_set = set(max_clique)
    rest = set(G.nodes) - clique_set

    if any(G.has_edge(u, v) for u in rest for v in rest if u != v):
        return False

    for u in rest:
        if any(not G.has_edge(u, v) for v in clique_set):
            return False

    return True
