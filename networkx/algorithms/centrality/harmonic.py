#    Copyright (C) 2015 by
#    Alessandro Luongo
#    BSD license.
#
# Authors:
#    Alessandro Luongo <alessandro.luongo@studenti.unimi.it>
#
"""Functions for computing the harmonic centrality of a graph."""
from collections import Counter
from functools import partial

import networkx as nx

__all__ = ['harmonic_centrality']


def harmonic_centrality(G, u=None, distance=None, normalized=False, reverse=False):
    r"""Compute harmonic centrality for nodes.

    Harmonic centrality [1]_ of a node `u` is the sum of the reciprocal
    of the shortest path distances from all other nodes to `u`

    .. math::

        C(u) = \sum_{v \neq u} \frac{1}{d(v, u)}

    where `d(v, u)` is the shortest-path distance between `v` and `u`.

    Notice that higher values indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph
    
    u : node, optional
      Return only the value for node u

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations.  If `None`, then each edge will have distance equal to 1.
      
    normalized : bool, optional (default=False)
      If True normalize by the number of nodes in the graph.

    reverse : bool, optional (default=False)
      If True and G is a digraph, reverse the edges of G, using successors
      instead of predecessors.

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
    if distance is not None:
        # use Dijkstra's algorithm with specified attribute as edge weight 
        path_length = partial(nx.single_source_dijkstra_path_length, 
                              weight=distance, reverse=not(reverse))
    else: # handle either directed or undirected
        if G.is_directed() and not reverse:
            path_length = nx.single_target_shortest_path_length
        else:
            path_length = nx.single_source_shortest_path_length

    if u is None:
        nodes = G.nodes()
    else:
        nodes = [u]

    if normalized:
        normalize_denominator = float( len(G) - 1 )
    else:
        normalize_denominator = 1

    harmonic_centrality = {}
    for n in nodes:
        counters = Counter(dict(path_length(G, n)).values())
        if len(counters) > 1:
            harmonic_centrality[n] = sum([count / float(distance) for distance, count in counters.most_common() if distance != 0]) / normalize_denominator
        else:
            harmonic_centrality[n] = 0.0
    if u is not None:
        return harmonic_centrality[u]
    else:
        return harmonic_centrality
