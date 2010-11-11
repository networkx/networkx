# -*- coding: utf-8 -*-
"""
Floyd-Warshall algorithmf or shortest paths.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['floyd_warshall',
           'floyd_warshall_predecessor_and_distance',
           'floyd_warshall_numpy']

import networkx as nx


def floyd_warshall_numpy(G,nodelist=None):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph
    
    nodelist : list, optional       
       The rows and columns are ordered by the nodes in nodelist.
       If`nodelist is None then the ordering is produced by G.nodes().

    Returns
    -------
    distance : NumPy matrix
        A matrix of shortest path distances between nodes.
        If there is no path between to nodes the corresponding matrix entry
        will be Inf.

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths 
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time O(n^3) with running space is O(n^2).
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
          "to_numpy_matrix() requires numpy: http://scipy.org/ ")
    A=nx.to_numpy_matrix(G,nodelist=nodelist,multigraph_weight=min)
    n,m = A.shape
    I=np.identity(n)
    A[A==0]=np.inf # set zero entries to inf
    A[I==1]=0 # except diagonal which should be zero
    for i in range(n):
        r = A[i,:]
        A = np.minimum(A, r + r.T)
    return A

def floyd_warshall_predecessor_and_distance(G):
    """Find all-pairs shortest path lengths using Floyd's algorithm.
    
    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    predecessor,distance : dictionaries
       Dictionaries, keyed by source and target, of predecessors and distances 
       in the shortest path.

    Notes
    ------
    Floyd's algorithm is appropriate for finding shortest paths 
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time O(n^3) with running space is O(n^2).

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
    dist=defaultdict(lambda : defaultdict(lambda: float('inf')))
    pred=defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected= not G.is_directed()
    for u,v,d in G.edges(data=True):
        weight = d.get('weight',1.0)
        dist[u][v] = min(weight,dist[u][v])
        pred[u][v] = u
        dist[u][u] = 0
        if undirected:
            dist[v][u] = min(weight,dist[v][u])
            pred[v][u] = v
    for w in G:
        for u in G:
            for v in G:
                if dist[u][v] > dist[u][w] + dist[w][v]:
                    dist[u][v] = dist[u][w] + dist[w][v]
                    pred[u][v] = pred[w][v]
    return dict(pred),dict(dist)


def floyd_warshall(G):
    """Find all-pairs shortest path lengths using Floyd's algorithm.
    
    Parameters
    ----------
    G : NetworkX graph

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
    It has running time O(n^3) with running space is O(n^2).

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    # could make this it's own function to reduce memory costs
    return floyd_warshall_predecessor_and_distance(G)[1]

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
