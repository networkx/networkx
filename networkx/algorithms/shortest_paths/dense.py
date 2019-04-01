# -*- coding: utf-8 -*-
"""Floyd-Warshall algorithm for shortest paths.
"""
#    Copyright (C) 2004-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg <aric.hagberg@gmail.com>
#          Miguel Sozinho Ramalho <m.ramalho@fe.up.pt>
import networkx as nx

__all__ = ['floyd_warshall',
           'floyd_warshall_predecessor_and_distance',
           'reconstruct_path',
           'floyd_warshall_numpy']


def floyd_warshall_numpy(G, nodelist=None, weight='weight'):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered by the nodes in nodelist.
       If nodelist is None then the ordering is produced by G.nodes().

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    distance : NumPy matrix
        A matrix of shortest path distances between nodes.
        If there is no path between to nodes the corresponding matrix entry
        will be Inf.

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths in
    dense graphs or graphs with negative weights when Dijkstra's
    algorithm fails.  This algorithm can still fail if there are
    negative cycles.  It has running time $O(n^3)$ with running space of $O(n^2)$.
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            "to_numpy_matrix() requires numpy: http://scipy.org/ ")

    # To handle cases when an edge has weight=0, we must make sure that
    # nonedges are not given the value 0 as well.
    A = nx.to_numpy_matrix(G, nodelist=nodelist, multigraph_weight=min,
                           weight=weight, nonedge=np.inf)
    n, m = A.shape
    I = np.identity(n)
    A[I == 1] = 0  # diagonal elements should be zero
    for i in range(n):
        A = np.minimum(A, A[i, :] + A[:, i])
    return A


def floyd_warshall_predecessor_and_distance(G, weight='weight'):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    predecessor,distance : dictionaries
       Dictionaries, keyed by source and target, of predecessors and distances
       in the shortest path.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from([('s', 'u', 10), ('s', 'x', 5),
    ...     ('u', 'v', 1), ('u', 'x', 2), ('v', 'y', 1), ('x', 'u', 3),
    ...     ('x', 'v', 5), ('x', 'y', 2), ('y', 's', 7), ('y', 'v', 6)])
    >>> predecessors, _ = nx.floyd_warshall_predecessor_and_distance(G)
    >>> print(nx.reconstruct_path('s', 'v', predecessors))
    ['s', 'x', 'u', 'v']

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time $O(n^3)$ with running space of $O(n^2)$.

    See Also
    --------
    floyd_warshall
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    from collections import defaultdict
    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: float('inf')))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v
    for w in G:
        for u in G:
            for v in G:
                if dist[u][v] > dist[u][w] + dist[w][v]:
                    dist[u][v] = dist[u][w] + dist[w][v]
                    pred[u][v] = pred[w][v]
    return dict(pred), dict(dist)


def reconstruct_path(source, target, predecessors):
    """Reconstruct a path from source to target using the predecessors
    dict as returned by floyd_warshall_predecessor_and_distance

    Parameters
    ----------
    source : node
       Starting node for path

    target : node
       Ending node for path

    predecessors: dictionary
       Dictionary, keyed by source and target, of predecessors in the
       shortest path, as returned by floyd_warshall_predecessor_and_distance

    Returns
    -------
    path : list
       A list of nodes containing the shortest path from source to target

       If source and target are the same, an empty list is returned

    Notes
    ------
    This function is meant to give more applicability to the
    floyd_warshall_predecessor_and_distance function

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    """
    if source == target:
        return []
    prev = predecessors[source]
    curr = prev[target]
    path = [target, curr]
    while curr != source:
        curr = prev[curr]
        path.append(curr)
    return list(reversed(path))


def floyd_warshall(G, weight='weight'):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.


    Returns
    -------
    distance : dict
       A dictionary,  keyed by source and target, of shortest paths distances
       between nodes.

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time $O(n^3)$ with running space of $O(n^2)$.

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    # could make this its own function to reduce memory costs
    return floyd_warshall_predecessor_and_distance(G, weight=weight)[1]

# fixture for nose tests


def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
