import networkx as nx
import numpy as np
from scipy import stats

def small_world(G, n_iter = 1000, use_transitivity = False):
    r"""Calculates the small world coefficient for the network G.  The small world
    coefficient is defined as:

    .. math::

       S^{\vartriangle}(g) =\frac{\gamma^{\vartriangle}_g}{\lambda_g}

    Where `\gamma^{\vartriangle}_g` is the ratio between the transitivity of
    network `g` and the average transitivity of n_iter random networks with the
    same amount of nodes and edges, and `\lambda_g` is the ratio between the
    average shortest path length of network `g` and the average of the
    average shortest path length of n_iter random networks.

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
    ... 
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

    rand_cc = []
    rand_shortest_path = []
    for I in range(n_iter):
        random_G = nx.gnm_random_graph(n, m)
        if not nx.is_connected(random_G):
            random_G = nx.connected_component_subgraphs(random_G)[0]
            # The generated random graph might not have all the connected
            # nodes - in which case use the largest component.
        if not use_transitivity:   
            _cc = nx.average_clustering(random_G)
        else:
            _cc = nx.transitivity(random_G)
            
        _sp = nx.average_shortest_path_length(random_G)
        rand_cc.append(_cc)
        rand_shortest_path.append(_sp)
        
    mean_shortest_path = float(np.mean(rand_shortest_path))
    mean_cc = float(np.mean(rand_cc))
    
    rand_sw = []
    for _cc, _sp in zip(rand_cc, rand_shortest_path):
        rand_sw.append((_cc/mean_cc) / (_sp/mean_shortest_path))

    G_cc = nx.average_clustering(G)
    G_shortest_path = nx.average_shortest_path_length(G)
    
    path_len_ratio = float(G_shortest_path) /mean_shortest_path
    cc_ratio = float(G_cc) / mean_cc

    small_worldness = cc_ratio / path_len_ratio

    sw_prob = stats.norm.pdf(small_worldness, loc=np.mean(rand_sw), 
        scale=np.std(rand_sw))
    
    return (small_worldness, sw_prob, rand_sw, rand_shortest_path, rand_cc)