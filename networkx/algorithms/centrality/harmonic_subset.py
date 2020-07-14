from functools import partial
import networkx as nx

__all__ = ['harmonic_centrality_subset']


def harmonic_centrality_subset(G, nbunch_u=None, nbunch_v=None, distance=None):
    """Compute harmonic centrality for a set of nodes u with respect to a subset of nodes v.

    Harmonic centrality [1]_ of a node `u` is the sum of the reciprocal
    of the shortest path distances from all other nodes (adapted in this function to only 
    consider nodes in nbunch_v) to `u`

    .. math::

        C(u) = \sum_{v \neq u} \frac{1}{d(v, u)}

    where `d(v, u)` is the shortest-path distance between `v` and `u`.

    Harmonic_centrality_subset calculates the harmonic centrality for u in nbunch_u and v in nbunch_v.

    Notice that higher values indicate higher centrality.

    Parameters
    ----------
    G : NetworkX graph

    nbunch_u : container
      Container of nodes. If provided harmonic centrality will be computed only over the
      nodes in nbunch_u.

    nbunch_v : container
      Container of nodes. If provided, harmonic centrality will be computed only for paths
      starting at nodes v in nbunch_v.

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge weight in shortest
      path calculations.  If `None`, then each edge will have weight equal to 1.

    Returns
    -------
    harmonic_centrality : dict
        Keys: nodes, Values: harmonic centrality value

    References
    ----------
    .. [1] Boldi, Paolo, and Sebastiano Vigna. "Axioms for centrality."
           Internet Mathematics 10.3-4 (2014): 222-262.
    """

    if G.is_directed():
        G = G.reverse()
    spl = partial(nx.shortest_path_length, G, weight=distance)
    harmonic_centrality = dict()
    for u in G.nbunch_iter(nbunch_u):
        sum_of_inverse_spl = 0.0
        for v in G.nbunch_iter(nbunch_v):
            try:
                shortest_path_length_uv = spl(source=u, target=v)
            except nx.NetworkXNoPath:
                continue
            if shortest_path_length_uv > 0:
                sum_of_inverse_spl += 1/shortest_path_length_uv

        harmonic_centrality[u] = sum_of_inverse_spl

    return harmonic_centrality



