__all__ = ["vertex_cover", "is_vertex_cover"]


import networkx as nx
from networkx.algorithms.vertex_covering.vertex_cover import vertex_cover
from networkx.utils.decorators import not_implemented_for


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
