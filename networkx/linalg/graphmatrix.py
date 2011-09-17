"""
Adjacency matrix and incidence matrix of graphs.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)'])

__all__ = ['incidence_matrix',
           'adj_matrix', 'adjacency_matrix',
           ]


def incidence_matrix(G, nodelist=None, edgelist=None, 
                     oriented=False, weight=None):
    """Return incidence matrix of G.

    The incidence matrix assigns each row to a node and each column to an edge.
    For a standard incidence matrix a 1 appears wherever a row's node is 
    incident on the column's edge.  For an oriented incidence matrix each
    edge is assigned an orientation (arbitrarily for undirected and aligning to
    direction for directed).  A -1 appears for the tail of an edge and 1 
    for the head of the edge.  The elements are zero otherwise.
    
    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional   (default= all nodes in G)
       The rows are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    edgelist : list, optional (default= all edges in G) 
       The columns are ordered according to the edges in edgelist.
       If edgelist is None, then the ordering is produced by G.edges().

    oriented: bool, optional (default=False)
       If True, matrix elements are +1 or -1 for the head or tail node 
       respectively of each edge.  If False, +1 occurs at both nodes.

    weight : string or None, optional (default=None)
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.  Edge weights, if used,
       should be positive so that the orientation can provide the sign.

    Returns
    -------
    A : NumPy matrix
      The incidence matrix of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges in edgelist should be 
    (u,v,key) 3-tuples.

    "Networks are the best discrete model for so many problems in 
    applied mathematics" [1]_.

    References
    ----------
    .. [1] Gil Strang, Network applications: A = incidence matrix,
       http://academicearth.org/lectures/network-applications-incidence-matrix
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
          "incidence_matrix() requires numpy: http://scipy.org/ ")
    if nodelist is None:
        nodelist = G.nodes()
    if edgelist is None:
        if G.is_multigraph():
            edgelist = G.edges(keys=True)
        else:
            edgelist = G.edges()
    A = np.zeros((len(nodelist),len(edgelist)))
    node_index = dict( (node,i) for i,node in enumerate(nodelist) )
    for ei,e in enumerate(edgelist):
        (u,v) = e[:2]
        if u == v: continue  # self loops give zero column
        try:
            ui = node_index[u]
            vi = node_index[v]
        except KeyError:
            raise NetworkXError('node %s or %s in edgelist '
                                'but not in nodelist"%(u,v)')
        if weight is None:
            wt = 1
        else:
            if G.is_multigraph():
                ekey = e[2]
                wt = G[u][v][ekey].get(weight,1)
            else:
                wt = G[u][v].get(weight,1)
        if oriented:
            A[ui,ei] = -wt
            A[vi,ei] = wt
        else:
            A[ui,ei] = wt
            A[vi,ei] = wt
    return np.asmatrix(A)

def adjacency_matrix(G, nodelist=None, weight='weight'):
    """Return adjacency matrix of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    A : numpy matrix
      Adjacency matrix representation of G.

    Notes
    -----
    If you want a pure Python adjacency matrix representation try
    networkx.convert.to_dict_of_dicts which will return a
    dictionary-of-dictionaries format that can be addressed as a
    sparse matrix.

    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    to_numpy_matrix
    to_dict_of_dicts
    """
    return nx.to_numpy_matrix(G,nodelist=nodelist,weight=weight)

adj_matrix=adjacency_matrix

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
