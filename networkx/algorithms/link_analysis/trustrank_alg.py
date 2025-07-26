from networkx.algorithms.link_analysis.pagerank_alg import pagerank
import networkx as nx

def trustrank(G, alpha=0.85, seed_nodes=None):
    """
    Calculates the TrustRank of nodes in a graph.

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    alpha : float, optional
      Damping parameter for TrustRank, default=0.85.

    seed_nodes : list or set, optional
      A set of nodes to be considered the trusted seeds.
      If None, this is equivalent to standard PageRank.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with TrustRank as value.
    """
    if seed_nodes is None:
        # If no seeds, it's just a regular pagerank
        personalization = None
    else:
        # Check that all seed nodes are in the graph
        missing = set(seed_nodes) - set(G)
        if missing:
            raise nx.NetworkXError(f"Seed nodes {missing} are not in the graph")
        # Create the personalization vector for the seed set
        personalization = {node: 1.0 / len(seed_nodes) for node in seed_nodes}

    # Call the existing pagerank function with the personalization
    return pagerank(G, alpha=alpha, personalization=personalization)