import networkx as nx
import numpy as np

__author__ = ['Federico Vaggi (federico.vaggi@fmach.it)']

__all__ = ['small_world']

def small_world(G, n_iter = 1000, use_transitivity = False):
    r"""Calculates the small world coefficient for the network G.  The small
    world coefficient is defined as:

    .. math::

       S^{\vartriangle}(g) =\frac{\gamma^{\vartriangle}_g}{\lambda_g}

    Where `\gamma^{\vartriangle}_g` is the ratio between the transitivity of
    network `g` and the average transitivity of n_iter random networks with the
    same amount of nodes and edges, and `\lambda_g` is the ratio between the
    average shortest path length of network `g` and the average of the
    average shortest path length of n_iter random networks.
    
    If G is directed, the random networks generated (as well as the 
    clustering coefficient/transitivity) will also be directed.

    Parameters
    ----------
    G : graph
      A NetworkX graph 

    n_iter : int, optional (default=1000)
      n_iter is the number of random networks used to calculate the average
      shortest path length and the average transitivity (or clustering
      coefficient) for a network with the same number of edges and nodes as G.

    use_transitivity : bool, option (default = False)
      if True, will use transitivity to calculate small worldness, if False
      will use average clustering coefficient instead.  Read [1]_ for an
      in-depth discussion of the difference between the two measures.
      
    Returns
    -------
    small_worldness : float
       The small world ratio for the network.
       
    rand_sw : list
        A list containing n_iter elements, with each element representing the
        small world value for each random network.  Can be used to calculate
        more advanced statistics for small worldness.
        
    Notes
    -----
    This implementation is based on algorithm 11 in [1]_. The authors propose
    two different methods of calculating small worldness, one based on
    transitivity, and one based on average_clustering.  For most networks, the
    two measures give similar results, although this is not always the case.

    See also
    --------
    average_clustering
    transitivity
    average_shortest_path_length

    References
    ----------
    .. [1] Humphries MD, Gurney K (2008)
    Network ‘Small-World-Ness’: A Quantitative Method for Determining Canonical
    Network Equivalence.
    PLoS ONE 3(4): e0002051. doi:10.1371/journal.pone.0002051
    """

    n = len(G)
    m = len(G.edges())
    directed = nx.is_directed(G)
    
    if use_transitivity:
        clustering_fcn = nx.transitivity
    else:
        clustering_fcn = nx.linalg.linalg_average_clustering
        
    if directed:
        distance_fcn = nx.average_distance_weakly_connected
        connected_fcn = nx.is_weakly_connected
        components_fcn = nx.weakly_connected_component_subgraphs
    else:
        distance_fcn = nx.average_shortest_path_length
        connected_fcn = nx.is_connected
        components_fcn = nx.connected_component_subgraphs
    # When we generate random subgraphs, sometimes they will have unconnected
    # components.  In that case, we work with the largest connected component.

    rand_cc = []
    rand_shortest_path = []
    for I in range(n_iter):
        random_G = nx.gnm_random_graph(n, m, directed = directed)
        if not connected_fcn(random_G):
            random_G = components_fcn(random_G)[0]
            # The generated random graph might not have all the connected
            # nodes - in which case use the largest component.
                
        rand_cc.append(clustering_fcn(random_G))
        rand_shortest_path.append(distance_fcn(random_G))
        
    mean_shortest_path = float(np.mean(rand_shortest_path))
    G_shortest_path = distance_fcn(G)
    path_len_ratio = float(G_shortest_path) /mean_shortest_path
    mean_cc = float(np.mean(rand_cc))
    G_cc = clustering_fcn(G)
    cc_ratio = float(G_cc) / mean_cc
    small_worldness = cc_ratio / path_len_ratio
    
    rand_sw = []
    for cc, sp in zip(rand_cc, rand_shortest_path):
        rand_sw.append((cc/mean_cc) / (sp/mean_shortest_path))
    
    return (small_worldness, rand_sw)
