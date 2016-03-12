# coding=utf8
"""
Eigenvector centrality.
"""
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (aric.hagberg@gmail.com)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Sasha Gutfraind (ag362@cornell.edu)'])
__all__ = ['eigenvector_centrality',
           'eigenvector_centrality_numpy']

def eigenvector_centrality(G, max_iter=100, tol=1.0e-6, nstart=None,
                           weight='weight'):
    """Compute the eigenvector centrality for the graph G.

    Eigenvector centrality computes the centrality for a node based on the
    centrality of its neighbors. The eigenvector centrality for node `i` is

    .. math::

        \mathbf{Ax} = \lambda \mathbf{x}

    where `A` is the adjacency matrix of the graph G with eigenvalue `\lambda`.
    By virtue of the Perron–Frobenius theorem, there is a unique and positive
    solution if `\lambda` is the largest eigenvalue associated with the
    eigenvector of the adjacency matrix `A` ([2]_).

    Parameters
    ----------
    G : graph
      A networkx graph

    max_iter : integer, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of eigenvector iteration for each node.

    weight : None or string, optional
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> centrality = nx.eigenvector_centrality(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    See Also
    --------
    eigenvector_centrality_numpy
    pagerank
    hits

    Notes
    -----
    The measure was introduced by [1]_ and is discussed in [2]_.

    Eigenvector convergence: The power iteration method is used to compute
    the eigenvector and convergence is not guaranteed. Our method stops after
    `max_iter` iterations or when the vector change is below an error
    tolerance of ``number_of_nodes(G)*tol``. We actually use (A+I) rather
    than the adjacency matrix A because it shifts the spectrum to enable
    discerning the correct eigenvector even for networks with multiple
    dominant eigenvalues.

    For directed graphs this is "left" eigenvector centrality which corresponds
    to the in-edges in the graph. For out-edges eigenvector centrality
    first reverse the graph with ``G.reverse()``.

    References
    ----------
    .. [1] Phillip Bonacich:
       Power and Centrality: A Family of Measures.
       American Journal of Sociology 92(5):1170–1182, 1986
       http://www.leonidzhukov.net/hse/2014/socialnetworks/papers/Bonacich-Centrality.pdf
    .. [2] Mark E. J. Newman:
       Networks: An Introduction.
       Oxford University Press, USA, 2010, pp. 169.

    """
    from math import sqrt
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXException("Not defined for multigraphs.")

    if len(G) == 0:
        raise nx.NetworkXException("Empty graph.")

    if nstart is None:
        # choose starting vector with entries of 1/len(G)
        x = dict([(n,1.0/len(G)) for n in G])
    else:
        x = nstart
    # normalize starting vector
    s = 1.0/sum(x.values())
    for k in x:
        x[k] *= s
    nnodes = G.number_of_nodes()
    # make up to max_iter iterations
    for i in range(max_iter):
        xlast = x
        x = xlast.copy() # Start with xlast times I to iterate with (A+I)
        # do the multiplication y^T = x^T A (left eigenvector)
        for n in x:
            for nbr in G[n]:
                x[nbr] += xlast[n] * G[n][nbr].get(weight, 1)
        # normalize vector
        try:
            s = 1.0/sqrt(sum(v**2 for v in x.values()))
        # this should never be zero?
        except ZeroDivisionError:
            s = 1.0
        for n in x:
            x[n] *= s
        # check convergence
        err = sum([abs(x[n]-xlast[n]) for n in x])
        if err < nnodes*tol:
            return x

    raise nx.NetworkXError("""eigenvector_centrality():
power iteration failed to converge in %d iterations."%(i+1))""")


def eigenvector_centrality_numpy(G, weight='weight'):
    """Compute the eigenvector centrality for the graph G.

    Eigenvector centrality computes the centrality for a node based on the
    centrality of its neighbors. The eigenvector centrality for node `i` is

    .. math::

        \mathbf{Ax} = \lambda \mathbf{x}

    where `A` is the adjacency matrix of the graph G with eigenvalue `\lambda`.
    By virtue of the Perron–Frobenius theorem, there is a unique and positive
    solution if `\lambda` is the largest eigenvalue associated with the
    eigenvector of the adjacency matrix `A` ([2]_).

    Parameters
    ----------
    G : graph
      A networkx graph

    weight : None or string, optional
      The name of the edge attribute used as weight.
      If None, all edge weights are considered equal.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> centrality = nx.eigenvector_centrality_numpy(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    See Also
    --------
    eigenvector_centrality
    pagerank
    hits

    Notes
    -----
    The measure was introduced by [1]_.

    This algorithm uses the SciPy sparse eigenvalue solver (ARPACK) to
    find the largest eigenvalue/eigenvector pair.

    For directed graphs this is "left" eigenvector centrality which corresponds
    to the in-edges in the graph. For out-edges eigenvector centrality
    first reverse the graph with G.reverse().

    References
    ----------
    .. [1] Phillip Bonacich:
       Power and Centrality: A Family of Measures.
       American Journal of Sociology 92(5):1170–1182, 1986
       http://www.leonidzhukov.net/hse/2014/socialnetworks/papers/Bonacich-Centrality.pdf
    .. [2] Mark E. J. Newman:
       Networks: An Introduction.
       Oxford University Press, USA, 2010, pp. 169.
    """
    import scipy as sp
    from scipy.sparse import linalg
    if len(G) == 0:
        raise nx.NetworkXException('Empty graph.')
    M = nx.to_scipy_sparse_matrix(G, nodelist=list(G), weight=weight,
                                  dtype=float)
    eigenvalue, eigenvector = linalg.eigs(M.T, k=1, which='LR')
    largest = eigenvector.flatten().real
    norm = sp.sign(largest.sum())*sp.linalg.norm(largest)
    centrality = dict(zip(G,map(float,largest/norm)))
    return centrality


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
