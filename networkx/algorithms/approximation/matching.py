"""
**************
Graph Matching
**************

Given a graph G = (V,E), a matching M in G is a set of pairwise non-adjacent
edges; that is, no two edges share a common vertex.

`Wikipedia: Matching <https://en.wikipedia.org/wiki/Matching_(graph_theory)>`_
"""
import networkx as nx

__all__ = ["min_maximal_matching"]


def min_maximal_matching(G):
    r"""Returns the minimum maximal matching of G. That is, out of all maximal
    matchings of the graph G, the smallest is returned.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    Returns
    -------
    min_maximal_matching : set
      Returns a set of edges such that no two edges share a common endpoint
      and every edge not in the set shares some common endpoint in the set.
      Cardinality will be 2*OPT in the worst case.

    Examples
    --------
    >>> from networkx.algorithms.approximation.matching import min_maximal_matching
    >>> G = nx.Graph()
    >>> edges = [(0, 1),(0, 3),(1, 2),(1, 3),(1, 4)]
    >>> nx.add_edges_from(edges)
    >>> min_maximal_matching(G)
    {(0, 1)}

    Notes
    -----
    The algorithm computes an approximate solution fo the minimum maximal
    cardinality matching problem. The solution is no more than 2 * OPT in size.
    Runtime is $O(|E|)$.

    References
    ----------
    .. [1] Vazirani, Vijay Approximation Algorithms (2001)
    """
    return nx.maximal_matching(G)
