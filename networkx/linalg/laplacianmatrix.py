"""
Laplacian matrix of graphs.
"""
#    Copyright (C) 2004-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import require, not_implemented_for

__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)'])

__all__ = ['laplacian', 'generalized_laplacian','normalized_laplacian',
           'laplacian_matrix', 'generalized_laplacian','normalized_laplacian',
           'directed_laplacian',
           ]


def laplacian_matrix(G, nodelist=None, weight='weight'):
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

def normalized_laplacian_matrix(G, nodelist=None, weight='weight'):
    r"""Return the normalized Laplacian matrix of G.

    The normalized graph Laplacian is the matrix

    .. math::

        NL = D^{-1/2} L D^{-1/2}

    where `L` is the graph Laplacian and `D` is the diagonal matrix of
    node degrees.

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

    If the Graph contains selfloops, D is defined as diag(sum(A,1)), where A is
    the adjencency matrix [2]_.

    See Also
    --------
    laplacian

    References
    ----------
    .. [1] Fan Chung-Graham, Spectral Graph Theory,
       CBMS Regional Conference Series in Mathematics, Number 92, 1997.
    .. [2] Steve Butler, Interlacing For Weighted Graphs Using The Normalized
       Laplacian, Electronic Journal of Linear Algebra, Volume 16, pp. 90-98,
       March 2007.
    """
    # FIXME: this isn't the most efficient way to do this...
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
          "normalized_laplacian() requires numpy: http://scipy.org/ ")
    if G.is_multigraph():

        L = laplacian(G, nodelist=nodelist, weight=weight)
        D = np.diag(L)
    elif G.number_of_selfloops() == 0:
        L = laplacian(G, nodelist=nodelist, weight=weight)
        D = np.diag(L)
    else:
        A = np.array(nx.adj_matrix(G))
        D = np.sum(A, 1)
        L = np.diag(D) - A

    # Handle div by 0. It happens if there are unconnected nodes
    with np.errstate(divide='ignore'):
        Disqrt = np.diag(1 / np.sqrt(D))
    Disqrt[np.isinf(Disqrt)] = 0
    Ln = np.dot(Disqrt, np.dot(L,Disqrt))
    return Ln

###############################################################################
# Code based on
# https://bitbucket.org/bedwards/networkx-community/src/370bd69fc02f/networkx/algorithms/community/

@require('numpy')
@not_implemented_for('undirected')
@not_implemented_for('multigraph')
def directed_laplacian(G, nodelist=None, weight='weight', walk_type=None, alpha=0.95):
    r"""Return the directed Laplacian matrix of G.

    The graph directed Laplacian is the matrix

    .. math::

        L = I - (\Phi^{1/2} P \Phi^{-1/2} + \Phi^{-1/2} P^T \Phi^{1/2} ) / 2

    where `I` is the identity matrix, `P` is the transition matrix of the
    graph, and `Phi` a matrix with the Perron vector of `P` in the diagonal and
    zeros elsewhere.

    Depending on the value of `walk_type`, `P` can be the transition matrix
    induced by a random walk, a lazy random walk, or a random walk with
    teleportation (pagerank).

    Parameters
    ----------
    G : DiGraph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    walk_type : string or None, optional (default=None)
       If `None`, P is selected depending on the properties of the
       graph. Otherwise is one of 'random', 'lazy', or 'pagerank'

    alpha : real
       (1 - alpha) is the teleportation probability used with pagerank

    Returns
    -------
    L : NumPy array
      Normalized Laplacian of G.

    Raises
    ------
    NetworkXError
        If NumPy cannot be imported
    NetworkXNotImplemnted
        If G is not a DiGraph

    Notes
    -----
    Only implemented for DiGraphs

    See Also
    --------
    laplacian

    References
    ----------
    .. [1] Fan Chung (2005). Laplacians and the Cheeger inequality for directed
    graphs. Annals of Combinatorics, 9(1), 2005
    """
    import numpy as np

    if walk_type is None:
        if nx.is_strongly_connected(G):
            if nx.is_aperiodic(G):
                walk_type = "random"
            else:
                walk_type = "lazy"
        else:
            walk_type = "pagerank"

    M = nx.to_numpy_matrix(G, nodelist=nodelist, weight=weight)
    n, m = M.shape
    if walk_type in ["random", "lazy"]:
        DI = np.diagflat(1.0 / np.sum(M, axis=1))
        if walk_type == "random":
            P =  DI * M
        else:
            I = np.identity(n)
            P = (I + DI * M) / 2.0
    elif walk_type == "pagerank":
        if not (0 < alpha < 1):
            raise nx.NetworkXError('alpha must be between 0 and 1')
        # add constant to dangling nodes' row
        dangling = np.where(M.sum(axis=1) == 0)
        for d in dangling[0]:
            M[d] = 1.0 / n
        # normalize
        M = M / M.sum(axis=1)
        P = alpha * M + (1 - alpha) / n
    else:
        raise nx.NetworkXError("walk_type must be random, lazy, or pagerank")

    evals, evecs = np.linalg.eig(P.T)
    index = evals.argsort()[-1] # index of largest eval,evec
    # eigenvector of largest eigenvalue at ind[-1]
    v = np.array(evecs[:,index]).flatten().real
    p =  v / v.sum()
    sp = np.sqrt(p)
    Q = np.diag(sp) * P * np.diag(1.0/sp)
    I = np.identity(len(G))

    return I  - (Q + Q.T) /2.0

combinatorial_laplacian=laplacian_matrix
generalized_laplacian=normalized_laplacian_matrix
normalized_laplacian=normalized_laplacian_matrix
laplacian=laplacian_matrix

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
