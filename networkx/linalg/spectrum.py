"""
Laplacian, adjacency matrix, and spectrum of graphs.

"""
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx

__all__ = ['adj_matrix', 'laplacian', 'generalized_laplacian',
           'laplacian_spectrum', 'adjacency_spectrum','normalized_laplacian']


def adj_matrix(G,nodelist=None):
    """Return adjacency matrix of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

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

    See Also
    --------
    to_numpy_matrix
    to_dict_of_dicts
    """
    return nx.to_numpy_matrix(G,nodelist=nodelist)


def laplacian(G,nodelist=None):
    """Return the Laplacian matrix of G.

    The graph Laplacian is the matrix L = D - A, where
    A is the adjacency matrix and D is the diagonal matrix of node degrees.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    Returns
    -------
    L : NumPy matrix
      Laplacian of G.

    See Also
    --------
    normalized_laplacian
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "laplacian() requires numpy: http://scipy.org/ "
    # this isn't the most efficient way to do this...
    n=G.order()
    I=np.identity(n)
    A=np.asarray(nx.to_numpy_matrix(G,nodelist=nodelist))
    D=I*np.sum(A,axis=1)
    L=D-A
    return L


def normalized_laplacian(G,nodelist=None):
    """Return the normalized Laplacian matrix of G.

    The normalized graph Laplacian is the matrix NL=D^(-1/2) L D^(-1/2)
    L is the graph Laplacian and D is the diagonal matrix of node degrees.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    nodelist : list, optional       
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    Returns
    -------
    L : NumPy matrix
      Normalized Laplacian of G.

    See Also
    --------
    laplacian

    References
    ----------
    .. [1] Fan Chung-Graham, Spectral Graph Theory, 
       CBMS Regional Conference Series in Mathematics, Number 92, 1997.
    """
    # FIXME: this isn't the most efficient way to do this...
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "normalized_laplacian() requires numpy: http://scipy.org/ "
    A=np.asarray(nx.to_numpy_matrix(G,nodelist=nodelist))
    d=np.sum(A,axis=1)
    I=np.identity(len(d))
    L=I*d-A
    osd=np.zeros(len(d))
    for i in range(len(d)):
        if d[i]>0: osd[i]=np.sqrt(1.0/d[i])
    T=I*osd
    L=np.dot(T,np.dot(L,T))
    return L

def laplacian_spectrum(G):
    """Return eigenvalues of the Laplacian of G

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    See Also
    --------
    laplacian
    """

    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "laplacian_spectrum() requires NumPy: http://scipy.org/ "
    return np.linalg.eigvals(laplacian(G))

def adjacency_spectrum(G):
    """Return eigenvalues of the adjacency matrix of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    See Also
    --------
    adj_matrix
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "adjacency_spectrum() requires NumPy: http://scipy.org/ "
    return np.linalg.eigvals(adj_matrix(G))


combinatorial_laplacian=laplacian
generalized_laplacian=normalized_laplacian
