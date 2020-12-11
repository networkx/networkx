"""Functions for computing the harmonic centrality of a graph."""
from functools import partial

import networkx as nx

__all__ = ["harmonic_centrality"]


def harmonic_centrality(G, nbunch=None, nbunch_v=None, distance=None):
    r"""Compute harmonic centrality for nodes.

    Harmonic centrality [1]_ of a node `u` is the sum of the reciprocal
    of the shortest path distances from all other nodes to `u`

    .. math::

        C(u) = \sum_{v \neq u} \frac{1}{d(v, u)}

    where `d(v, u)` is the shortest-path distance between `v` and `u`.

    If nbunch_v is given as an arguemnt, the harmonic centrality for u in
    nbunch is calculated considering only nodes v in nbunch_v.

    Notice that higher values indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    nbunch : container
      Container of nodes. If provided harmonic centrality will be computed
      only over the nodes in nbunch.

    nbunch_v : container
      Container of nodes. If provided, harmonic centrality will be computed
      only with respect to nodes in nbunch_v.

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations.  If `None`, then each edge will have distance equal to 1.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with harmonic centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality, closeness_centrality

    Notes
    -----
    If the 'distance' keyword is set to an edge attribute key then the
    shortest-path length will be computed using Dijkstra's algorithm with
    that edge attribute as the edge weight.

    References
    ----------
    .. [1] Boldi, Paolo, and Sebastiano Vigna. "Axioms for centrality."
           Internet Mathematics 10.3-4 (2014): 222-262.
    """

    if G.is_directed():
        g = G.reverse(copy=False)
    else:
        g = G

    spl = partial(nx.shortest_path_length, g, weight=distance)

    if nbunch_v is None:
        # original implementation of harmonic centrality
        centrality = {
            u: sum(1 / d if d > 0 else 0 for v, d in spl(source=u).items())
            for u in g.nbunch_iter(nbunch)
        }

        return centrality

    else:
        # only consider paths between nodes in nbunch and nbunch_v
        centrality = dict()
        for u in g.nbunch_iter(nbunch):
            sum_of_inverse_spl = 0.0
            for v in g.nbunch_iter(nbunch_v):
                try:
                    shortest_path_length_uv = spl(source=u, target=v)
                except nx.NetworkXNoPath:
                    continue
                if shortest_path_length_uv > 0:
                    sum_of_inverse_spl += 1 / shortest_path_length_uv
            centrality[u] = sum_of_inverse_spl
        return centrality
