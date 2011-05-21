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


def adj_matrix(G,nodelist=None,weight='weight'):
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


def laplacian(G,nodelist=None,weight='weight'):
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

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    L : NumPy array
      Laplacian of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    to_numpy_matrix
    normalized_laplacian
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
          "laplacian() requires numpy: http://scipy.org/ ")
    # this isn't the most efficient way to do this...
    if G.is_multigraph():
        A=np.asarray(nx.to_numpy_matrix(G,nodelist=nodelist,weight=weight))
        I=np.identity(A.shape[0])
        D=I*np.sum(A,axis=1)
        L=D-A
        return L
    # Graph or DiGraph, this is faster than above 
    if nodelist is None:
        nodelist=G.nodes()
    n=len(nodelist)
    index=dict( (n,i) for i,n in enumerate(nodelist) )
    L = np.zeros((n,n))
    for ui,u in enumerate(nodelist):
        totalwt=0.0
        for v,d in G[u].items():
            try:
                vi=index[v]
            except KeyError:
                continue
            wt=d.get(weight,1)
            L[ui,vi]= -wt
            totalwt+=wt
        L[ui,ui]= totalwt
    return L


def normalized_laplacian(G,nodelist=None,weight='weight'):
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

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    L : NumPy array
      Normalized Laplacian of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

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
        raise ImportError(
          "normalized_laplacian() requires numpy: http://scipy.org/ ")
    if G.is_multigraph():
        A=np.asarray(nx.to_numpy_matrix(G,nodelist=nodelist,weight=weight))
        d=np.sum(A,axis=1)
        n=A.shape[0]
        I=np.identity(n)
        L=I*d-A
        osd=np.zeros(n)
        for i in range(n):
            if d[i]>0: osd[i]=np.sqrt(1.0/d[i])
        T=I*osd
        L=np.dot(T,np.dot(L,T))
        return L
    # Graph or DiGraph, this is faster than above 
    if nodelist is None:
        nodelist = G.nodes()
    n=len(nodelist)
    L = np.zeros((n,n))
    deg = np.zeros((n,n))
    index=dict( (n,i) for i,n in enumerate(nodelist) )
    for ui,u in enumerate(nodelist):
        totalwt=0.0
        for v,data in G[u].items():
            try:
                vi=index[v]
            except KeyError:
                continue
            wt=data.get(weight,1)
            L[ui,vi]= -wt
            totalwt+=wt
        L[ui,ui]= totalwt
        if totalwt>0.0:
            deg[ui,ui]= np.sqrt(1.0/totalwt)
    L=np.dot(deg,np.dot(L,deg))
    return L

def laplacian_spectrum(G,weight='weight'):
    """Return eigenvalues of the Laplacian of G

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    laplacian
    """

    try:
        import numpy as np
    except ImportError:
        raise ImportError(
          "laplacian_spectrum() requires NumPy: http://scipy.org/ ")
    return np.linalg.eigvals(laplacian(G,weight=weight))

def adjacency_spectrum(G,weight='weight'):
    """Return eigenvalues of the adjacency matrix of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    adj_matrix
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
          "adjacency_spectrum() requires NumPy: http://scipy.org/ ")
    return np.linalg.eigvals(adj_matrix(G,weight=weight))


combinatorial_laplacian=laplacian
generalized_laplacian=normalized_laplacian


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
