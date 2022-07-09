import networkx as nx

__all__ = ["decay_centrality"]


def decay_centrality(G, u=None, delta=0.5, mode="all", weight=None):
    r"""
    Compute the decay centrality for nodes.
    Decay centrality [1]_ of a node `u` is the decay parameter raised to power
    sum of shortest distance between `u`and `n-1` reachable nodes. This
    particular algorithm allows to manipulate the emphasis of reachable nodes
    with respect to distance between the nodes.

    .. math::
        DC(u) = {\sum_{v=1}^{n - 1}} \delta ^{d(v, u)},
        0 < \delta < 1
    where `d(v, u)` is the shortest-path distance between `v` and `u`,
    `delta` is the decay parameter with value between 0 and 1,
    and `n` is the number of nodes that can reach `u`.

    Notice that when `delta` approaches 0, the decay centrality approaches
    degree and decay centrality becomes propostional to the degree centrality.

    When `delta` approaches 1, the decay centrality approaches size of
    component i.e the number of reachable nodes.

    Parameters
    ----------
    G : graph
      A NetworkX graph
    u : node, optional
      Return only the value for node u
    delta : decay parameter, optional (default=0.5)
      Use the specified decay parameter. It must be between 0 and 1.
    mode : string, optional (default='all')
      Ignored for undirected graphs.
      Compute the decay centrality for nodes as if graph is undirected if mode
      is 'all', or the decay centrality for incoming edges path if mode is 'in'
      or the decay centrality for outgoing edges path if mode is 'out'.
    weight : string or function, optional (default = None)
      If None, every edge has weight/distance/cost 1.If a string, use this edge
      attribute as the edge weight.Any edge attribute not present defaults
      to 1. If this is a function, the weight of an edge is the value returned
      by the function. The function must accept exactly three positional
      arguments:
      1. the two endpoints of an edge
      2. the dictionary of edge attributes for that edge.
      The function must return a number.
    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with decay centrality as the value.
    Raises
    ------
    ValueError:
        if delta is not between 0 and 1
    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> decay_centrality(G, delta=0.5)
    {0: 0.875, 1: 1.25, 2: 1.25, 3: 0.875}

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality, incremental_closeness_centrality, closeness_centrality
    References
    ----------
    .. [1] Bloch, Francis and Jackson, Matthew O. and Tebaldi, Pietro:
          Centrality Measures in Networks
          https://doi.org/10.48550/arxiv.1608.05845,
       [2] pg 64 of Jackson, Matthew O.,
          Social and Economic Networks, 2008,
          Princeton University Press.
    """
    if delta >= 1 or delta <= 0:
        raise ValueError("delta must be between 0 and 1")

    decay_centrality = {}

    if mode == "all" and G.is_directed():
        G = G.to_undirected()

    if mode == "in" and G.is_directed():
        path_length = lambda x: nx.shortest_path_length(G, target=x, weight=weight)
    else:
        path_length = lambda x: nx.shortest_path_length(G, source=x, weight=weight)

    if u is None:
        nodes = G.nodes
    else:
        nodes = [u]

    for n in nodes:

        geodisc_distance_for_n = path_length(n)

        decay_centrality[n] = 0

        for v in geodisc_distance_for_n:
            if v == n or geodisc_distance_for_n[v] == 0:
                continue
            decay_centrality[n] += delta ** (geodisc_distance_for_n[v])

    if u is not None:
        return decay_centrality[u]

    return decay_centrality
