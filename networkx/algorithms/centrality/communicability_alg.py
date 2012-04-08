"""
Communicability and centrality measures.
"""
#    Copyright (C) 2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import *
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Franck Kalala (franckkalala@yahoo.fr'])
__all__ = ['communicability_centrality_exp',
           'communicability_centrality',
           'communicability_betweenness_centrality',
           'communicability',
           'communicability_exp',
           'estrada_index',
           ]

@require('scipy')
@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability_centrality_exp(G):
    r"""Return the communicability centrality for each node of G

    Communicability centrality, also called subgraph centrality, of a node `n`
    is the sum of closed walks of all lengths starting and ending at node `n`.

    Parameters
    ----------
    G: graph

    Returns
    -------
    nodes:dictionary
        Dictionary of nodes with communicability centrality as the value.

    Raises
    ------
    NetworkXError
        If the graph is not undirected and simple.

    See Also
    --------
    communicability:
        Communicability between all pairs of nodes in G.
    communicability_centrality:
        Communicability centrality for each node of G.

    Notes
    -----
    This version of the algorithm exponentiates the adjacency matrix.
    The communicability centrality of a node `u` in G can be found using
    the matrix exponential of the adjacency matrix of G  [1]_ [2]_,

    .. math::

        SC(u)=(e^A)_{uu} .

    References
    ----------
    .. [1] Ernesto Estrada, Juan A. Rodriguez-Velazquez,
       "Subgraph centrality in complex networks",
       Physical Review E 71, 056103 (2005).
       http://arxiv.org/abs/cond-mat/0504730

    .. [2] Ernesto Estrada, Naomichi Hatano,
       "Communicability in complex networks",
       Phys. Rev. E 77, 036111 (2008).
       http://arxiv.org/abs/0707.0756

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> sc = nx.communicability_centrality_exp(G)
    """
    # alternative implementation that calculates the matrix exponential
    import scipy.linalg
    nodelist = G.nodes() # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    expA = scipy.linalg.expm(A)
    # convert diagonal to dictionary keyed by node
    sc = dict(zip(nodelist,map(float,expA.diagonal())))
    return sc

@require('numpy')
@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability_centrality(G):
    r"""Return communicability centrality for each node in G.

    Communicability centrality, also called subgraph centrality, of a node `n`
    is the sum of closed walks of all lengths starting and ending at node `n`.

    Parameters
    ----------
    G: graph

    Returns
    -------
    nodes: dictionary
       Dictionary of nodes with communicability centrality as the value.

    Raises
    ------
    NetworkXError
       If the graph is not undirected and simple.

    See Also
    --------
    communicability:
        Communicability between all pairs of nodes in G.
    communicability_centrality:
        Communicability centrality for each node of G.

    Notes
    -----
    This version of the algorithm computes eigenvalues and eigenvectors
    of the adjacency matrix.

    Communicability centrality of a node `u` in G can be found using
    a spectral decomposition of the adjacency matrix [1]_ [2]_,

    .. math::

       SC(u)=\sum_{j=1}^{N}(v_{j}^{u})^2 e^{\lambda_{j}},

    where `v_j` is an eigenvector of the adjacency matrix `A` of G
    corresponding corresponding to the eigenvalue `\lambda_j`.

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> sc = nx.communicability_centrality(G)

    References
    ----------
    .. [1] Ernesto Estrada, Juan A. Rodriguez-Velazquez,
       "Subgraph centrality in complex networks",
       Physical Review E 71, 056103 (2005).
       http://arxiv.org/abs/cond-mat/0504730
    .. [2] Ernesto Estrada, Naomichi Hatano,
       "Communicability in complex networks",
       Phys. Rev. E 77, 036111 (2008).
       http://arxiv.org/abs/0707.0756
    """
    import numpy
    import numpy.linalg
    nodelist = G.nodes() # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    w,v = numpy.linalg.eigh(A)
    vsquare = numpy.array(v)**2
    expw = numpy.exp(w)
    xg = numpy.dot(vsquare,expw)
    # convert vector dictionary keyed by node
    sc = dict(zip(nodelist,map(float,xg)))
    return sc

@require('scipy')
@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability_betweenness_centrality(G, normalized=True):
    r"""Return communicability betweenness for all pairs of nodes in G.

    Communicability betweenness measure makes use of the number of walks
    connecting every pair of nodes as the basis of a betweenness centrality
    measure.

    Parameters
    ----------
    G: graph

    Returns
    -------
    nodes:dictionary
        Dictionary of nodes with communicability betweenness as the value.

    Raises
    ------
    NetworkXError
        If the graph is not undirected and simple.

    See Also
    --------
    communicability:
       Communicability between all pairs of nodes in G.
    communicability_centrality:
       Communicability centrality for each node of G using matrix exponential.
    communicability_centrality_exp:
       Communicability centrality for each node in G using
       spectral decomposition.

    Notes
    -----
    Let `G=(V,E)` be a simple undirected graph with `n` nodes and `m` edges,
    and `A` denote the adjacency matrix of `G`.

    Let `G(r)=(V,E(r))` be the graph resulting from
    removing all edges connected to node `r` but not the node itself.

    The adjacency matrix for `G(r)` is `A+E(r)`,  where `E(r)` has nonzeros
    only in row and column `r`.

    The communicability betweenness of a node `r`  is [1]_

    .. math::
         \omega_{r} = \frac{1}{C}\sum_{p}\sum_{q}\frac{G_{prq}}{G_{pq}},
         p\neq q, q\neq r,

    where
    `G_{prq}=(e^{A}_{pq} - (e^{A+E(r)})_{pq}`  is the number of walks
    involving node r,
    `G_{pq}=(e^{A})_{pq}` is the number of closed walks starting
    at node `p` and ending at node `q`,
    and `C=(n-1)^{2}-(n-1)` is a normalization factor equal to the
    number of terms in the sum.

    The resulting `\omega_{r}` takes values between zero and one.
    The lower bound cannot be attained for a connected
    graph, and the upper bound is attained in the star graph.

    References
    ----------
    .. [1] Ernesto Estrada, Desmond J. Higham, Naomichi Hatano,
       "Communicability Betweenness in Complex Networks"
       Physica A 388 (2009) 764-774.
       http://arxiv.org/abs/0905.4102

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> cbc = nx.communicability_betweenness_centrality(G)
    """
    import scipy
    import scipy.linalg
    nodelist = G.nodes() # ordering of nodes in matrix
    n = len(nodelist)
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    expA = scipy.linalg.expm(A)
    mapping = dict(zip(nodelist,range(n)))
    sc = {}
    for v in G:
        # remove row and col of node v
        i = mapping[v]
        row = A[i,:].copy()
        col = A[:,i].copy()
        A[i,:] = 0
        A[:,i] = 0
        B = (expA - scipy.linalg.expm(A)) / expA
        # sum with row/col of node v and diag set to zero
        B[i,:] = 0
        B[:,i] = 0
        B -= scipy.diag(scipy.diag(B))
        sc[v] = float(B.sum())
        # put row and col back
        A[i,:] = row
        A[:,i] = col
    # rescaling
    sc = _rescale(sc,normalized=normalized)
    return sc

def _rescale(sc,normalized):
    # helper to rescale betweenness centrality
    if normalized is True:
        order=len(sc)
        if order <=2:
            scale=None
        else:
            scale=1.0/((order-1.0)**2-(order-1.0))
    if scale is not None:
        for v in sc:
            sc[v] *= scale
    return sc


@require('numpy','scipy')
@not_implemented_for('directed')
@not_implemented_for('multigraph')
def communicability(G):
    r"""Return communicability between all pairs of nodes in G.

    The communicability between pairs of nodes in G is the sum of
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
    communicability:
       Communicability between pairs of nodes in G.

    Notes
    -----
    This algorithm uses a spectral decomposition of the adjacency matrix.
    Let G=(V,E) be a simple undirected graph.  Using the connection between
    the powers  of the adjacency matrix and the number of walks in the graph,
    the communicability  between nodes `u` and `v` based on the graph spectrum
    is [1]_

    .. math::
        C(u,v)=\sum_{j=1}^{n}\phi_{j}(u)\phi_{j}(v)e^{\lambda_{j}},

    where `\phi_{j}(u)` is the `u\rm{th}` element of the `j\rm{th}` orthonormal
    eigenvector of the adjacency matrix associated with the eigenvalue
    `\lambda_{j}`.

    References
    ----------
    .. [1] Ernesto Estrada, Naomichi Hatano,
       "Communicability in complex networks",
       Phys. Rev. E 77, 036111 (2008).
       http://arxiv.org/abs/0707.0756

    Examples
    --------
    >>> G = nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> c = nx.communicability(G)
    """
    import numpy
    import scipy.linalg
    nodelist = G.nodes() # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    w,vec = numpy.linalg.eigh(A)
    expw = numpy.exp(w)
    mapping = dict(zip(nodelist,range(len(nodelist))))
    sc={}
    # computing communicabilities
    for u in G:
        sc[u]={}
        for v in G:
            s = 0
            p = mapping[u]
            q = mapping[v]
            for j in range(len(nodelist)):
                s += vec[:,j][p,0]*vec[:,j][q,0]*expw[j]
            sc[u][v] = float(s)
    return sc

@require('scipy')
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
    nodelist = G.nodes() # ordering of nodes in matrix
    A = nx.to_numpy_matrix(G,nodelist)
    # convert to 0-1 matrix
    A[A!=0.0] = 1
    # communicability matrix
    expA = scipy.linalg.expm(A)
    mapping = dict(zip(nodelist,range(len(nodelist))))
    sc = {}
    for u in G:
        sc[u]={}
        for v in G:
            sc[u][v] = float(expA[mapping[u],mapping[v]])
    return sc

@require('numpy')
def estrada_index(G):
    r"""Return the Estrada index of a the graph G.

    Parameters
    ----------
    G: graph

    Returns
    -------
    estrada index: float

    Raises
    ------
    NetworkXError
        If the graph is not undirected and simple.

    See also
    --------
    estrada_index_exp

    Notes
    -----
    Let `G=(V,E)` be a simple undirected graph with `n` nodes  and let
    `\lambda_{1}\leq\lambda_{2}\leq\cdots\lambda_{n}`
    be a non-increasing ordering of the eigenvalues of its adjacency
    matrix `A`.  The Estrada index is

    .. math::
        EE(G)=\sum_{j=1}^n e^{\lambda _j}.

    References
    ----------
    .. [1] E. Estrada,  Characterization of 3D molecular structure,
       Chem. Phys. Lett. 319, 713 (2000).

    Examples
    --------
    >>> G=nx.Graph([(0,1),(1,2),(1,5),(5,4),(2,4),(2,3),(4,3),(3,6)])
    >>> ei=nx.estrada_index(G)
    """
    return sum(communicability_centrality(G).values())

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
