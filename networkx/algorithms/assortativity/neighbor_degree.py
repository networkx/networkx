import networkx as nx

__all__ = ["average_neighbor_degree"]


def average_neighbor_degree(G, source="out", target="out", nodes=None, weight=None):
    r"""Returns the average degree of the neighborhood of each node.

    In an undirected graph, the neighborhood of a node is the list of nodes which are connected to the given node with an edge.

    In a directed graph, the neighborhood of a node will depend on the argument passed to source parameter when calling the function:

        - if source is 'in', then the neighborhood of the node is the list of nodes which are predecessors of the given node,
        - if source is 'out', then the neighborhood of the node is the list of nodes which are successors of the given node,
        - if source is 'in+out', then the neighborhood of the node is the list of nodes which are either predecessors or successors of the given node.

    The average neighborhood degree of a node `i` is

    .. math::

        k_{nn,i} = \frac{1}{|N(i)|} \sum_{j \in N(i)} k_j

    where `N(i)` are the neighbors of node `i` and `k_j` is
    the degree of node `j` which belongs to `N(i)`. For weighted
    graphs, an analogous measure can be defined [1]_,

    .. math::

        k_{nn,i}^{w} = \frac{1}{s_i} \sum_{j \in N(i)} w_{ij} k_j

    where `s_i` is the weighted degree of node `i`, `w_{ij}`
    is the weight of the edge that links `i` and `j` and
    `N(i)` are the neighbors of node `i`.


    Parameters
    ----------
    G : NetworkX graph

    source : string ("in"|"out"|"in+out")
       Directed graphs only.
       Use "in"- or "out"-degree for source node.

    target : string ("in"|"out"|"in+out")
       Directed graphs only.
       Use "in"- or "out"-degree for target node.

    nodes : list or iterable, optional
        Compute neighbor degree for specified nodes.  The default is
        all nodes in the graph.

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.

    Returns
    -------
    d: dict
       A dictionary keyed by node with average neighbors degree value.

    Raises
    ------
    NetworkXError
        If either `source` or `target` are not one of 'in',
        'out', or 'in+out'.
        If either `source` or `target` is passed for an undirected graph.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> G.edges[0, 1]["weight"] = 5
    >>> G.edges[2, 3]["weight"] = 3

    >>> nx.average_neighbor_degree(G)
    {0: 2.0, 1: 1.5, 2: 1.5, 3: 2.0}
    >>> nx.average_neighbor_degree(G, weight="weight")
    {0: 2.0, 1: 1.1666666666666667, 2: 1.25, 3: 2.0}

    >>> G = nx.DiGraph()
    >>> nx.add_path(G, [0, 1, 2, 3])
    >>> nx.average_neighbor_degree(G, source="in", target="in")
    {0: 0.0, 1: 0.0, 2: 1.0, 3: 1.0}

    >>> nx.average_neighbor_degree(G, source="out", target="out")
    {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0}

    Notes
    -----
    For directed graphs you can also specify in-degree or out-degree
    by passing keyword arguments.

    See Also
    --------
    average_degree_connectivity

    References
    ----------
    .. [1] A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani,
       "The architecture of complex weighted networks".
       PNAS 101 (11): 3747–3752 (2004).
    """
    if G.is_directed():
        if source == "in":
            source_degree = G.in_degree
        elif source == "out":
            source_degree = G.out_degree
        elif source == "in+out":
            source_degree = G.degree
        else:
            raise nx.NetworkXError(
                f"source argument {source} must be 'in', 'out' or 'in+out'"
            )

        if target == "in":
            target_degree = G.in_degree
        elif target == "out":
            target_degree = G.out_degree
        elif target == "in+out":
            target_degree = G.degree
        else:
            raise nx.NetworkXError(
                f"target argument {target} must be 'in', 'out' or 'in+out'"
            )
    else:
        if source != "out" or target != "out":
            raise nx.NetworkXError(
                f"source and target arguments are only supported for directed graphs"
            )
        source_degree = G.degree
        target_degree = G.degree

    # precompute target degrees -- should *not* be weighted degree
    tgt_deg = dict(target_degree())

    # average degree of neighbors
    avg = {}

    # default to empty neighbors dicts
    # based on the arguments passed to the method we will populate them or leave them empty
    G_P = G_S = {n: {} for n in G}

    # if G is a directed graph
    if G.is_directed():
        # if source includes 'in' ("in" or "in+out" cases), G_P will be populated with predecessors
        if "in" in source:
            G_P = G.pred
        # if source includes 'out' ("out" or "in+out" cases), G_S will be populated with successors
        if "out" in source:
            G_S = G.succ
    else:
        # if G is an undirected graph, G_S will be populated with adjacency dict
        G_S = G.adj

    for n, deg in source_degree(nodes, weight=weight):
        # normalize but not by zero degree
        if deg == 0:
            avg[n] = 0.0
            continue

        # these will hold the predecessors and successors of node n
        P_n = G_P[n]
        S_n = G_S[n]

        # when calculating average neighbor degree, we consider both P_n (predessors of n) and S_n (successors of n).
        # note that one of these two dictionaries may be empty based on the arguments passed to the method.
        if weight is None:
            avg[n] = (
                sum(tgt_deg[nbr] for nbr in S_n) + (sum(tgt_deg[nbr] for nbr in P_n))
            ) / deg
        else:
            avg[n] = (
                sum(S_n[nbr].get(weight, 1) * tgt_deg[nbr] for nbr in S_n)
                + sum(P_n[nbr].get(weight, 1) * tgt_deg[nbr] for nbr in P_n)
            ) / deg
    return avg
