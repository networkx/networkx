"""
Incremental closeness centrality measure.
"""

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils.decorators import not_implemented_for

__author__ = 'Michael Lauria <michael.david.lauria@gmail.com>'
__all__ = ['incremental_closeness_centrality']


@not_implemented_for('directed')
def incremental_closeness_centrality(G,
                                     edge,
                                     prev_cc=None,
                                     insertion=True,
                                     normalized=True):
    """
    Compute closeness centrality for nodes using level-based work filtering
    as described in Incremental Algorithms for Closeness Centrality by Sariyuce,
    A.E. ; Kaya, K. ; Saule, E. ; Catalyiirek, U.V.

    Closeness centrality [1]_ of a node `u` is the reciprocal of the
    sum of the shortest path distances from `u` to all `n-1` other nodes.
    Since the sum of distances depends on the number of nodes in the
    graph, closeness is normalized by the sum of minimum possible
    distances `n-1`.

    .. math::

        C(u) = \frac{n - 1}{\sum_{v=1}^{n-1} d(v, u)},

    where `d(v, u)` is the shortest-path distance between `v` and `u`,
    and `n` is the number of nodes in the graph.

    Notice that higher values of closeness indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph
    edge: tuple
      The modified edge (u, v) in the graph.
    prev_cc: list
      The previous closeness centrality for all nodes in the graph.
    insertion: bool, optional
      If True (default) the edge was inserted, otherwise it was deleted from the graph.
    normalized : bool, optional
      If True (default) normalize by the number of nodes in the connected
      part of the graph.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with closeness centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality

    Notes
    -----
    The closeness centrality is normalized to `(n-1)/(|G|-1)` where
    `n` is the number of nodes in the connected part of graph
    containing the node.  If the graph is not completely connected,
    this algorithm computes the closeness centrality for each
    connected part separately.

    This algorithm is applicable to undirected graphs without edge weights.

    References
    ----------
    .. [1] Freeman, L.C., 1979. Centrality in networks: I.
       Conceptual clarification.  Social Networks 1, 215--239.
       http://www.soc.ucsb.edu/faculty/friedkin/Syllabi/Soc146/Freeman78.PDF
       [2]Sariyuce, A.E. ; Kaya, K. ; Saule, E. ; Catalyiirek, U.V. Incremental
       Algorithms for Closeness Centrality
       http://sariyuce.com/papers/bigdata13.pdf
    """

    if prev_cc is not None:
        shared_items = set(prev_cc.keys()) & set(G.nodes())
        count_shared = len(shared_items)
        if len(prev_cc) != count_shared or len(G.nodes()) != count_shared:
            raise NetworkXError(
                "Previous closeness centrality list does not correspond to given\
        graph.")

    # Just aliases G
    G_prime = G

    # Unpack edge
    (u, v) = edge
    path_length = nx.single_source_shortest_path_length

    if insertion:
        # Do this first because G and G_prime refer to the same thing
        du = path_length(G, u)
        dv = path_length(G, v)

        G_prime.add_edge(u, v)
    else:
        G_prime.remove_edge(u, v)

        # For edge removal, we want to know about distances after the edge is gone
        du = path_length(G_prime, u)
        dv = path_length(G_prime, v)

    if prev_cc is None:
        return nx.closeness_centrality(G_prime)

    nodes = G_prime.nodes()
    closeness_centrality = {}
    for n in nodes:
        n_from_u = du.get(n)
        n_from_v = dv.get(n)
        if (n_from_u is not None and n_from_v is not None
                and abs(n_from_u - n_from_v) <= 1):
            closeness_centrality[n] = prev_cc[n]
        else:
            sp = path_length(G_prime, n)
            totsp = sum(sp.values())
            if totsp > 0.0 and len(G_prime) > 1:
                closeness_centrality[n] = (len(sp) - 1.0) / totsp
                # normalize to number of nodes-1 in connected part
                if normalized:
                    s = (len(sp) - 1.0) / (len(G_prime) - 1)
                    closeness_centrality[n] *= s
            else:
                closeness_centrality[n] = 0.0

    # Leave the graph as we found it
    if insertion:
        G_prime.remove_edge(u, v)
    else:
        G_prime.add_edge(u, v)

    return closeness_centrality
