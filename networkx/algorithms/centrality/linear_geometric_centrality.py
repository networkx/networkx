"""Function for computing a linear geometric centrality of a graph."""

from functools import partial

import networkx as nx

__all__ = ["linear_geometric_centrality"]


@nx._dispatchable(edge_attrs="distance")
def linear_geometric_centrality(G, f, nbunch=None, distance=None, sources=None):
    r"""Compute a linear geometric centrality for nodes.

    Linear geometric centrality [1]_ of a node `u` is the sum of some function `f(-)`
    applied to the shortest path distances from all other nodes to `u`.
    .. math::

        C(u) = \sum_{v \neq u} f(d(v, u))

    where `d(v, u)` is the shortest-path distance between `v` and `u`.
    The function `f(-)` determines how the distances impact on centrality: it is typically a
    monotonically non-increasing function,

    Other known centralities can be defined as special cases of linear geometric centrality,
    for suitable choices of `f(-)`. For instance,

    .. math::

        f(x) = 1 / x

    yields the harmonic centrality; instead,

    .. math::

        f(x) =  \begin{cases}
                1 & \text{if } x == 1\\
                0 & \text{otherwise}
                \end{cases}

    yields in-degree centrality.

    Even closeness centrality, albeit not being a linear geometric centrality itself, gives
    the same node-order as:

    .. math::

        f(x) = -x

    In [2]_ and elsewhere, this class is called decay centrality, but only for the special
    case in which `f(-)` is an exponentially-decaying function. Here, we are not making
    any assumption on how f behaves.

    If `sources` is given as an argument, the returned linear geometric centrality
    values are calculated only for nodes belonging to `sources`.

    Notice that higher values indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    f : function
      A function providing a float value for every distance.

    nbunch : container (default: all nodes in G)
      Container of nodes for which linear geometric centrality values are calculated.

    sources : container (default: all nodes in G)
      Container of nodes `v` over which distances are computed.
      Nodes not in `G` are silently ignored.

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations.  If `None`, then each edge will have distance equal to 1.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with linear geometric centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality, closeness_centrality, harmonic_centrality

    Notes
    -----
    If the 'distance' keyword is set to an edge attribute key then the
    shortest-path length will be computed using Dijkstra's algorithm with
    that edge attribute as the edge weight.

    References
    ----------
    .. [1] Boldi, Paolo, Furia, Flavio and Prezioso, Chiara. "Linear Geometric Centralities."
           In International Workshop on Modelling and Mining Networks (pp. 1-16). Springer, Cham. 2025.
    .. [2] Skibski, Oskar and Sosnowska, Jadwiga. "Axioms for distance-based centralities."
           In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 32, No. 1), 2018.
    """

    nbunch = set(G.nbunch_iter(nbunch) if nbunch is not None else G.nodes)
    sources = set(G.nbunch_iter(sources) if sources is not None else G.nodes)

    centrality = dict.fromkeys(nbunch, 0)

    transposed = False
    if len(nbunch) < len(sources):
        transposed = True
        nbunch, sources = sources, nbunch
        if nx.is_directed(G):
            G = nx.reverse(G, copy=False)

    spl = partial(nx.shortest_path_length, G, weight=distance)
    for v in sources:
        dist = spl(v)
        for u in nbunch.intersection(dist):
            d = dist[u]
            if d == 0:  # handle u == v and edges with 0 weight
                continue
            centrality[v if transposed else u] += f(d)

    return centrality
