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


@nx._dispatchable
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
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])
    >>> nx.approximation.min_maximal_matching(G)
    {(1, 2), (3, 5)}

    Notes
    -----
    The algorithm computes an approximate solution for the minimum maximal
    cardinality matching problem. The solution is no more than 2 * OPT in size.
    Runtime is $O(|E|)$.

    References
    ----------
    .. [1] Vazirani, Vijay Approximation Algorithms (2001)
    """
    return nx.maximal_matching(G)
