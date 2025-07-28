import networkx as nx
from networkx.algorithms.link_analysis.pagerank_alg import pagerank


def trustrank(G, alpha=0.85, seed_nodes=None, **kwargs):
    """
    Calculates the TrustRank of nodes in a graph.
    
    TrustRank is a link analysis algorithm that identifies important nodes
    starting from a small set of trusted "seed" nodes. It is a variant of the
    personalized PageRank algorithm.

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    alpha : float, optional
      Damping parameter for TrustRank, default=0.85.

    seed_nodes : iterable or dict
      An iterable of trusted seed nodes or a dictionary of trusted seed nodes
      with custom trust values. If a dictionary is provided, it represents the
      personalization vector used in the PageRank calculation, and the values
      will be normalized. If an iterable is provided, each node will be given
      an equal trust value.
    
    **kwargs
        Other keyword arguments are passed to the `networkx.pagerank` function.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with TrustRank as value.

    Raises
    ------
    NetworkXError
        If `seed_nodes` is an iterable and contains nodes not present in `G`.

    Examples
    --------
    >>> G = nx.DiGraph([(1, 2), (1, 3), (2, 4), (3, 4), (4, 1)])
    >>> seeds = {1}
    >>> ranks = nx.trustrank(G, seed_nodes=seeds)
        
    References
    ----------
    .. [1] Gyongyi, Zoltan; Garcia-Molina, Hector (2004).
       "Combating Web Spam with TrustRank"
       http://ilpubs.stanford.edu:8090/770/1/2004-52.pdf
    .. [2] Krishnan, Vijay; Raj, Rashmi
        "Web Spam Detection with Anti-Trust Rank"
        http://i.stanford.edu/~kvijay/krishnan-raj-airweb06.pdf
    """
    if seed_nodes is None:
        # If no seeds, it's just a regular pagerank
        personalization = None
    else:
        if isinstance(seed_nodes, dict):
        # Use user-provided weights as the personalization vector
            personalization = seed_nodes
        else:
            # Check that all seed nodes are in the graph
            seeds = set(seed_nodes)
            missing_nodes = [node for node in seeds if node not in G]
            if missing_nodes:
                raise nx.NetworkXError(
                    f"Seed nodes {missing_nodes} are not in the graph."
                )
            # Create a uniform personalization vector from the seed set
            personalization = {node: 1.0 / len(seeds) for node in seeds}

    return pagerank(G, alpha=alpha, personalization=personalization, **kwargs)
