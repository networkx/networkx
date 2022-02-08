"""
Bridging centrality measure.
"""

import networkx as nx
from networkx.algorithms.centrality.betweenness import betweenness_centrality
from networkx.utils import not_implemented_for

__all__ = ["bridging_centrality"]


@not_implemented_for("multigraph")
def bridging_centrality(G, k=None, normalized=True, weight=None, endpoints=False, seed=None):

    r"""Compute the bridging centrality for all nodes in the graph G.

    A bridging node is a node lying between modules, i.e., a
    node connecting densely connected components in a graph.
    The bridging nodes in a graph are identified by their high value of 
    bridging centrality. The bridging centrality of a node is the product 
    of the betweenness centrality (CB) and the bridging coefficient (BC), 
    which respectively measure the global and local features of a node.

    .. math::

       C_{R}(v)   = CB(v) \cdot BC(v)
    
    where CB(v) = \sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}
    and BC(v) = \frac{d^{-1}(v)}{\sum_{i \in N(v)} \frac{1}{d(i)}}
    Here, d(v) is the degree of v and N(v) is the set of neighbors of v.

    For more information on betweenness centrality, see centrality\betweenness.py
    
     Parameters
    ----------
    G : graph
      A NetworkX graph.
    k : int, optional (default=None)
      If k is not None use k node samples to estimate betweenness.
      The value of k <= n where n is the number of nodes in the graph.
      Higher values give better approximation.
    normalized : bool, optional
      If True the betweenness values are normalized by `2/((n-1)(n-2))`
      for graphs, and `1/((n-1)(n-2))` for directed graphs where `n`
      is the number of nodes in G.
    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.
      Weights are used to calculate weighted shortest paths, so they are
      interpreted as distances.
    endpoints : bool, optional
      If True include the endpoints in the shortest path counts.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
        Note that this is only used if k is not None.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with bridging centrality as the value.

    Raises
    ------
    NetworkXPointlessConcept
      If the graph `G` is the null graph.

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    This algorithm was introduced in [1].
    It relates the betweenness centrality of a node, a global feature,
    to its bridging coefficient, a local feature. It is used primarily
    to identify bridging nodes, which connect densely connected components
    of a graph. 

    This implementation uses the betweenness_centrality method. This method
    comes with a number of subtleties, more on this can be found in the
    documentation of that method

    References
    ----------
    .. [1] Ramanathan, M., Zhang, A., Cho, Y., & Hwang, W. (2006). 
        Bridging Centrality: Identifying Bridging Nodes in Scale-free Networks.

    """
    if len(G) == 0:
      raise nx.NetworkXPointlessConcept(
          "cannot compute centrality for the null graph"
      )
    
    bc = betweenness_centrality(G, k, normalized, weight, endpoints, seed)
    bridge_centrality = {}

    degrees = G.degree(weight=weight)

    for n in G.nodes():
        deg_n = degrees[n]
        neighbors = G.neighbors(n)
        sum_neighbor_deg = sum(degrees[neighbor] for neighbor in neighbors)

        bridge_coef = sum_neighbor_deg / deg_n
        bridge_centrality[n] = bc[n] * bridge_coef

    return bridge_centrality   