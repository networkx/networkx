from __future__ import division
import networkx as nx


def _average_shortest_path_length_weakly_connected(G, weight=None):
    r"""Return the average shortest path length for a directed graph.

    Unlike average_shortest_path_length, which normalizes the
    sum of the total path lengths by the maximum possible number of paths
    `n(n-1)`, this function normalizes only by the number of actual paths that
    a particular node has to other nodes in the graph.  For a weakly connected
    graph, this number can be significantly smaller.

    Parameters
    ----------
    G : NetworkX graph

    weight : None or string, optional (default = None)
       If None, every edge has weight/distance/cost 1.
       If a string, use this edge attribute as the edge weight.
       Any edge attribute not present defaults to 1.

    Raises
    ------
    NetworkXError:
       if the graph is not at least weakly connected.

    For strongly connected graphs, this function and
    average_shortest_path_length will give slightly different answer
    because only paths to other nodes are considered here.
    """
    if G.is_directed():
        if not nx.is_weakly_connected(G):
            raise nx.NetworkXError("Graph is not connected.")
    else:
        if not nx.is_connected(G):
            raise nx.NetworkXError("Graph is not connected.")

    all_pairs = nx.all_pairs_dijkstra_path_length(G, weight=weight)
    avg = []
    for node_1 in all_pairs.iterkeys():
        node_1_avg = []
        for node_2 in all_pairs[node_1].iterkeys():
            if node_1 == node_2:
                continue
            node_1_avg.append(all_pairs[node_1][node_2])
        avg.extend(node_1_avg)
    avg_path_len = sum(avg) / len(avg)
    return avg_path_len


def small_world(G, n_iter=1000, use_transitivity=False,
                null_graph_generator=nx.gnm_random_graph):
    r"""Calculates the small world coefficient for the network G.

    The small world coefficient is defined as:

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

    use_transitivity : bool, optional (default = False)
      if True, will use transitivity to calculate small worldness, if False
      will use average clustering coefficient instead.  Read [1]_ for an
      in-depth discussion of the difference between the two measures.

    null_graph_generator : function, optional (default = nx.gnm_random_graph)
      a function which generates a random graph, using the number of nodes
      and the number of edges of G as an input. We assume the function signature
      of the generator function is:
        null_G = null_graph_generator(n, m, directed) where n is the number of
     nodes in G, m is the number of edges, and directed is a boolean variable
     depending on whether or not G was directed.

    ...
    Notes
    -----
    This implementation is based on algorithm 11 in [1]_. The authors propose
    two different methods of calculating small worldness, one based on
    transitivity, and one based on clustering coefficient.  For most networks,
    the two measures give similar results, although this is not always the case.

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
        clustering_fcn = nx.linalg.la_clustering

    distance_fcn = _average_shortest_path_length_weakly_connected

    rand_cc = []
    rand_shortest_path = []
    for I in range(n_iter):
        random_G = null_graph_generator(n, m, directed=directed)
        if directed:
            if not nx.is_weakly_connected(random_G):
                random_G = nx.weakly_connected_component_subgraphs(random_G)[0]
                # The generated random graph might not have all the connected
                # nodes - in which case use the largest component.
        else:
            if not nx.is_connected(random_G):
                random_G = nx.connected_component_subgraphs(random_G)[0]

        rand_cc.append(clustering_fcn(random_G))
        rand_shortest_path.append(distance_fcn(random_G))

    mean_shortest_path = sum(rand_shortest_path) / float(n_iter)
    mean_cc = sum(rand_cc) / float(n_iter)

    G_shortest_path = distance_fcn(G)
    path_len_ratio = float(G_shortest_path) / mean_shortest_path

    G_cc = clustering_fcn(G)
    cc_ratio = float(G_cc) / mean_cc
    small_worldness = cc_ratio / path_len_ratio

    #rand_sw = []
    #for cc, sp in zip(rand_cc, rand_shortest_path):
    #    rand_sw.append((cc/mean_cc) / (sp/mean_shortest_path))
    #sw_prob = stats.norm.pdf(small_worldness, loc=np.mean(rand_sw),
    #    scale=np.std(rand_sw))

    return small_worldness
