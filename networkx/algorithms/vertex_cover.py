__all__ = ["vertex_cover", "is_vertex_cover"]


import networkx as nx
from networkx.algorithms.vertex_covering.lp_decomposition import find_lp_decomposition
from networkx.algorithms.vertex_covering.vertex_cover import (
    max_degree_branching,
    vc_above_lp_branching,
    vertex_cover_preprocessing,
)
from networkx.utils.decorators import not_implemented_for


@not_implemented_for("directed")
@nx._dispatchable
def vertex_cover(G, k):
    # find lp-opt value
    # compare 1.4656^k and 2.618^(k - lpOpt)

    g_new = G.copy()

    vc = set()
    g_new, k, vc, is_k_vc_possible = vertex_cover_preprocessing(g_new, k, vc)

    if not is_k_vc_possible:
        return False, set()

    lp_opt_value, *_ = find_lp_decomposition(g_new, k)

    if lp_opt_value > k:
        return False, set()

    vc_above_lp_opt_algo_check = 2.618 ** (k - lp_opt_value)
    max_deg_algo_check = 1.4656**k

    if vc_above_lp_opt_algo_check < max_deg_algo_check:
        return vc_above_lp_branching(g_new, k)
    else:
        return max_degree_branching(g_new, k)


@not_implemented_for("directed")
@nx._dispatchable
def is_vertex_cover(G, cover):
    """
    Decides whether a set of vertices is a valid vertex cover for the graph.

    Given a set of vertices, whether it is a vertex cover can be decided if
    we check that for all edges, atleast one of the end points is present
    in the set.

    Parameters
    ----------
    G : NetworkX graph
        An undirected bipartite graph.

    cover : set
        Set of vertices.

    Returns
    -------
    bool
        Whether the set of vertices is a valid vertex cover of the graph.

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)])
    >>> cover = {0, 1}
    >>> nx.is_vertex_cover(G, cover)
    True

    Notes
    -----
    A vertex cover of a graph is a set of vertices such that every edge is
    incident on atleast one vertex from the set

    """
    return all(u in cover or v in cover for (u, v) in G.edges)
