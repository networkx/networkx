"""
Local Community Detection Algorithms

Local Community Detection (LCD) aims to detected one or a few communities
sarting from certain source nodes in the network. This differs from Global
Communty Detection (GCD), which aims to partition an entire network into
communities.

LCD is often useful when either the complete graph is unknown or the graph
is large enough that GCD is infeasable

[1]_ Gives a good introduction and overview of LCD see this review here

References
----------
.. [1] Baltsou, Georgia, Konstantinos Christopoulos, and Konstantinos Tsichlas.
Local community detection: A survey. IEEE Access 10 (2022): 110701-110726.
https://doi.org/10.1109/ACCESS.2022.3213980

"""


def greedy_source_expansion(G, source, cutoff=None, weight=None):
    """Find the local community around a source node using the Greedy Source
    Expansion algorithm.

    The Greedy Source Expansion algorithm identifies a local community starting
    from a given source node and expands it based on the local modularity gain
    at each step. Following Clauset’s method [1]_, the algorithm adds neighboring
    nodes that maximize local modularity to the community iteratively, stopping
    when no additional nodes improve the modularity or when a predefined cutoff is
    reached.

    Local modularity measures the density of edges within a community relative
    to the total graph. By focusing on local modularity, the algorithm efficiently
    uncovers communities around a specific node without requiring global optimization
    over the entire graph.

    Local Modularity

    Local modularity measures how tightly connected a subset of nodes is compared to their
    external connections. For a community C, the local modularity is defined as the difference
    between the fraction of edges inside the community and the expected fraction of such
    edges if they were randomly distributed among all nodes in the graph.

    TODO: add the mathematical functions of local modularity and modularity difference

    Parameters
    ----------
    G : NetworkX graph
        The input graph, which can be directed or undirected.

    source : node
        The source node from which the community expansion begins.

    cutoff : int, optional (default=None)
        The maximum number of nodes to include in the community. If None, the algorithm
        expands until no further modularity gain can be made.

    weight : string or None, optional (default=None)
        The name of an edge attribute that holds the numerical value used as a weight.
        If None, each edge is treated as having a weight of 1.

    Returns
    ----------
    set
        A set of nodes representing the local community around the source node.

    Examples TODO: check example
    ----------
    >>> G = nx.karate_club_graph()
    >>> nx.community.local.greedy_source_expansion(G, source=0)
    {0, 1, 2, 3, 7, 13}

    Notes
    -----
    This algorithm is designed for detecting local communities around a specific node,
    which is useful for large networks where global community detection is computationally
    expensive. The method follows the local modularity optimization framework introduced by
    Clauset [1]_.

    The result of the algorithm may vary based on the structure of the graph, the choice
    of the source node, and the presence of ties between nodes during the greedy expansion process.

    References
    ----------
    .. [1] Clauset, Aaron. Finding local community structure in networks.
    Physical Review E—Statistical, Nonlinear, and Soft Matter Physics 72, no. 2 (2005): 026132.
    https://doi.org/10.1103/PhysRevE.72.026132

    """

    return {}
