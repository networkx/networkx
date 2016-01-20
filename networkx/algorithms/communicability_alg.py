# -*- coding: utf-8 -*-
"""
Communicability.
"""
#    Copyright (C) 2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Previously coded as communicability centrality
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import *
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Franck Kalala (franckkalala@yahoo.fr'])
__all__ = ['communicability',
           'communicability_exp',
           ]

@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability_exp(G):
    r"""Return communicability between all pairs of nodes in G.

    Communicability between pair of node (u,v) of node in G is the sum of
    closed walks of different lengths starting at node u and ending at node v.

    Parameters
    ----------
    G: graph

    Returns
    -------
    comm: dictionary of dictionaries
        Dictionary of dictionaries keyed by nodes with communicability
        as the value.

    Raises
    ------
    NetworkXError
        If the graph is not undirected and simple.

    See Also
    --------
    communicability_centrality_exp:
       Communicability centrality for each node of G using matrix exponential.
    communicability_centrality:
       Communicability centrality for each node in G using spectral
       decomposition.
    communicability_exp:
       Communicability between all pairs of nodes in G  using spectral
       decomposition.

    Notes
    -----
    This algorithm uses matrix exponentiation of the adjacency matrix.

    Let G=(V,E) be a simple undirected graph.  Using the connection between
    the powers  of the adjacency matrix and the number of walks in the graph,
    the communicability between nodes u and v is [1]_,

    .. math::
        C(u,v) = (e^A)_{uv},

    where `A` is the adjacency matrix of G.

    References
    ----------
    .. [1] Ernesto Estrada, Naomichi Hatano,
       "Communicability in complex networks",
       Phys. Rev. E 77, 036111 (2008).
       http://arxiv.org/abs/0707.0756

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> c = nx.communicability_exp(G)
    """
    import scipy.linalg
    nodelist = list(G) # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    # communicability matrix
    expA = scipy.linalg.expm(A)
    mapping = dict(zip(nodelist,range(len(nodelist))))
    c = {}
    for u in G:
        c[u]={}
        for v in G:
            c[u][v] = float(expA[mapping[u],mapping[v]])
    return c

@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability_exp(G):
    r"""Return communicability between all pairs of nodes in G.

    Communicability between pair of node (u,v) of node in G is the sum of
    closed walks of different lengths starting at node u and ending at node v.

    Parameters
    ----------
    G: graph

    Returns
    -------
    comm: dictionary of dictionaries
        Dictionary of dictionaries keyed by nodes with communicability
        as the value.

    Raises
    ------
    NetworkXError
        If the graph is not undirected and simple.

    See Also
    --------
    communicability_centrality_exp:
       Communicability centrality for each node of G using matrix exponential.
    communicability_centrality:
       Communicability centrality for each node in G using spectral
       decomposition.
    communicability_exp:
       Communicability between all pairs of nodes in G  using spectral
       decomposition.

    Notes
    -----
    This algorithm uses matrix exponentiation of the adjacency matrix.

    Let G=(V,E) be a simple undirected graph.  Using the connection between
    the powers  of the adjacency matrix and the number of walks in the graph,
    the communicability between nodes u and v is [1]_,

    .. math::
        C(u,v) = (e^A)_{uv},

    where `A` is the adjacency matrix of G.

    References
    ----------
    .. [1] Ernesto Estrada, Naomichi Hatano,
       "Communicability in complex networks",
       Phys. Rev. E 77, 036111 (2008).
       http://arxiv.org/abs/0707.0756

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> c = nx.communicability_exp(G)
    """
    import scipy.linalg
    nodelist = list(G) # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    # communicability matrix
    expA = scipy.linalg.expm(A)
    mapping = dict(zip(nodelist,range(len(nodelist))))
    c = {}
    for u in G:
        c[u]={}
        for v in G:
            c[u][v] = float(expA[mapping[u],mapping[v]])
    return c

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
