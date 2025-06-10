"""Function for computing a linear geometric centrality of a graph."""

from functools import partial

import networkx as nx

__all__ = ["linear_geometric_centrality"]


@nx._dispatchable(edge_attrs="distance")
def linear_geometric_centrality(G, f, *, nbunch=None, sources=None, weight=None):
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
    the same node-order as _negative eccentricity_, defined by

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

    f : function or string
      A function providing a float value for every distance.
      As a string can be:
        - "harmonic" (for the function x &rarr; 1/x),
        - "indegree" (for the function x &rarr; 1 if x==1 else 0),
        - "negecc" (for the function x &arr; -x).

    nbunch : container (default: all nodes in G)
      Container of nodes for which linear geometric centrality values are calculated.

    sources : container (default: all nodes in G)
      Container of nodes `v` over which distances are computed.
      Nodes not in `G` are silently ignored.

    weight : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge length in shortest
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
    If the 'weight' keyword is set to an edge attribute key then the
    shortest-path length will be computed using Dijkstra's algorithm with
    that edge attribute as the edge length.

    References
    ----------
    .. [1] Boldi, Paolo, Furia, Flavio and Prezioso, Chiara. "Linear Geometric Centralities."
           In International Workshop on Modelling and Mining Networks (pp. 1-16). Springer, Cham. 2025.
    .. [2] Skibski, Oskar and Sosnowska, Jadwiga. "Axioms for distance-based centralities."
           In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 32, No. 1), 2018.
    """

    def harmonic_f(x):
        return 1 / x

    def indegree_f(x):
        if x == 1:
            return 1
        return 0

    def negecc_f(x):
        return -x

    nbunch = set(G.nbunch_iter(nbunch) if nbunch is not None else G.nodes)
    sources = set(G.nbunch_iter(sources) if sources is not None else G.nodes)

    centrality = dict.fromkeys(nbunch, 0)

    if isinstance(f, str):
        if f == "harmonic":
            f = harmonic_f
        elif f == "indegree":
            f = indegree_f
        elif f == "negecc":
            f = negecc_f
        else:
            raise TypeError(f"Expected str or function, got {type(x).__name__}")

    transposed = False
    if (
        len(nbunch) < len(sources)
    ):  # Optimize: if there are fewer nodes for which we want to compute centrality than
        # sources, just reverse the computation
        transposed = True
        nbunch, sources = sources, nbunch
        if nx.is_directed(G):
            G = nx.reverse(G, copy=False)

    spl = partial(nx.shortest_path_length, G, weight=weight)
    for v in sources:
        dist = spl(v)
        for u in nbunch & dist.keys():
            d = dist[u]
            if d == 0:  # handle u == v and edges with 0 weight
                continue
            centrality[v if transposed else u] += f(d)

    return centrality
