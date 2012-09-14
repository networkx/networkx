"""
Katz centrality.
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
                        'Sasha Gutfraind (ag362@cornell.edu)', 
                        'Vincent Gauthier (vgauthier@luxbulb.org)'])

__all__ = ['katz_centrality',
           'katz_centrality_numpy']

def katz_centrality(G,alpha, beta=None, max_iter=1000,tol=1.0e-6,nstart=None):
    """Compute the Katz centrality for the graph G.

    The Katz centrality is derived from the eigenvector centrality it uses the
    power method to find the eigenvector corresponding to the largest eigenvalue
    obtain from eigen decomposition of adjacency matrix of G. The constant alpha
    should be strictly inferior to the inverse of largest eigenvalue of the
    adjacency matrix for the algorithm to converge.

    Parameters
    ----------
    G : graph
      A networkx graph 

    alpha : float
      Attenuation factor

    beta : vector, optional
      n by 1 NumPy vector, weight attributed to the immediate neighborhood.

    max_iter : interger, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of Katz iteration for each node. 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with Katz centrality as the value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> A = nx.adj_matrix(G,nodelist=G.nodes())
    >>> eigenvalues,eigenvectors=np.linalg.eig(A)
    >>> largest_eigenvalue = np.array(eigenvalues).max().real
    >>> alpha = 1./(largest_eigenvalue+0.2)
    >>> centrality=nx.katz_centrality(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    -----
    The Katz calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    Notes
    ------
    Katz centrality overcome some limitations of the eigenvalue centrality and 
    it is defined as follows :  
    .. math::
        x_i = \alpha \sum_{i} A_{ij} x_j + \beta

    with 

    .. math::
        \alpha < \frac{1}{\lambda_max}

    Katz centrality computes the relative influence of a node within a network
    by measuring the number of the immediate neighbors (first degree nodes) and
    also all other nodes in the network that connect to the node under
    consideration through these immediate neighbors, extra weight could be
    provided to immediate neighbor through the parameter :math:`\beta`.
    Connections made with distant neighbors are, however, penalized by an
    attenuation factor :math:`\alpha. :math:`\alpha` should be stricly less than
    the inverse largest eigenvalue of the adjacency matrix in order for the Katz
    centrality to be computed correctly. More information are provided in
    [New10]_ .


    References
    ++++++++++
    .. [New10] M. Newman, Networks: An Introduction. Oxford University Press, 
    USA, 2010, p. 720.


    See Also
    --------
    katz_centrality_numpy
    eigenvector_centrality
    eigenvector_centrality_numpy
    pagerank
    hits
    """
    from math import sqrt
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXException("Not defined for multigraphs.")

    if len(G)==0:
        raise nx.NetworkXException("Empty graph.")

    nnodes=G.number_of_nodes()

    if beta is None:
        beta = [1]*nnodes

    if nstart is None:
        # choose starting vector with entries of 0 
        x=dict([(n,0) for n in G])
    else:
        x=nstart

    # make up to max_iter iterations        
    for i in range(max_iter):
        xlast=x
        x=dict.fromkeys(xlast, 0)
        # do the multiplication y = Alpha * Ax - Beta
        for n in x:
            for nbr in G[n]:
                x[n] += xlast[nbr] * G[n][nbr].get('weight',1)
            x[n] = alpha*x[n] + beta[n]

        # check convergence            
        err=sum([abs(x[n]-xlast[n]) for n in x])
        if err < nnodes*tol:
            # normalize vector
            try:
                s=1.0/sqrt(sum(v**2 for v in x.values()))
            # this should never be zero?
            except ZeroDivisionError:
                s=1.0
            for n in x: x[n]*=s
            return x

    raise nx.NetworkXError("""eigenvector_centrality(): 
power iteration failed to converge in %d iterations."%(i+1))""")


def katz_centrality_numpy(G, alpha, beta=None):
    """Compute the Katz centrality for the graph G.

    The constant alpha should be strictly inferior to the inverse of largest
    eigenvalue of the adjacency matrix for the algorithm to converge.

    Parameters
    ----------
    G : graph
      A networkx graph

    alpha : float
      Attenuation factor

    beta : NumPy Array, optional
        n by 1 NumPy vector, weight attributed to the immediate neighborhood. 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> A = nx.adj_matrix(G,nodelist=G.nodes())
    >>> eigenvalues,eigenvectors=np.linalg.eig(A)
    >>> largest_eigenvalue = np.array(eigenvalues).max().real
    >>> alpha = 1./(largest_eigenvalue+0.2)
    >>> centrality=nx.katz_centrality_numpy(G, alpha)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    ------
    Katz centrality overcome some limitations of the eigenvalue centrality and 
    it is defined as follows :  
    .. math::
        x_i = \alpha \sum_{i} A_{ij} x_j + \beta

    with 

    .. math::
        \alpha < \frac{1}{\lambda_max}

    Katz centrality computes the relative influence of a node within a network
    by measuring the number of the immediate neighbors (first degree nodes) and
    also all other nodes in the network that connect to the node under
    consideration through these immediate neighbors, extra weight could be
    provided to immediate neighbor through the parameter :math:`\beta`.
    Connections made with distant neighbors are, however, penalized by an
    attenuation factor :math:`\alpha. :math:`\alpha` should be stricly less than
    the inverse largest eigenvalue of the adjacency matrix in order for the Katz
    centrality to be computed correctly. More information are provided in
    [New10]_ .

    References
    ++++++++++
    .. [New10] M. Newman, Networks: An Introduction. Oxford University Press, 
    USA, 2010, p. 720.
    

    See Also
    --------
    katz_centrality
    eigenvector_centrality_numpy
    eigenvector_centrality
    pagerank
    hits
    """
    try:
        import numpy as np
        from numpy.matlib import ones 
    except ImportError:
        raise ImportError('Requires NumPy: http://scipy.org/')

    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXException('Not defined for multigraphs.')

    if len(G)==0:
        raise nx.NetworkXException('Empty graph.')

    A=nx.adj_matrix(G,nodelist=G.nodes())
    n = np.array(A).shape[0]
    if beta is None:
        beta = ones((n,1))

    centrality = np.linalg.pinv( np.matlib.eye(n,n) - (alpha * A) ) * beta
    norm = np.sign(sum(centrality)) * np.linalg.norm(centrality)
    centrality=dict(zip(G,map(float,centrality/norm)))
    return centrality


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
        import numpy.linalg
    except:
        raise SkipTest("numpy not available")