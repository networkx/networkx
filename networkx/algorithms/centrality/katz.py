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

    Uses the power method to find the eigenvector for the 
    largest eigenvalue of the adjacency matrix of G.

    Parameters
    ----------
    G : graph
      A networkx graph 

    alpha : float

    beta : vector, optional 

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
    >>> eigenvalues,eigenvectors=np.linalg.eig(A)
    >>> largest_eigenvalue = np.array(eigenvalues).max().real
    >>> alpha = 1./(largest_eigenvalue+0.2)
    >>> centrality=nx.eigenvector_centrality(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    ------
    The Katz calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    For directed graphs this is "right" eigevector centrality.  For
    "left" eigenvector centrality, first reverse the graph with
    G.reverse().

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

    Parameters
    ----------
    G : graph
      A networkx graph

    alpha : float

    beta : NumPy Array, optional
        n by 1 NumPy vector Beta constant parameter of the Katz centrality method  

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> eigenvalues,eigenvectors=np.linalg.eig(A)
    >>> largest_eigenvalue = np.array(eigenvalues).max().real
    >>> alpha = 1./(largest_eigenvalue+0.2)
    >>> centrality=nx.katz_centrality_numpy(G, alpha)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    ------
    Katz centrality
    .. math::
        x_i = \alpha \sum_{i} A_{ij} x_j + \beta
    

    For directed graphs this is "right" eigevector centrality.  For
    "left" eigenvector centrality, first reverse the graph with
    G.reverse().

    References
    ++++++++++
    .. [New10] M. Newman, Networks: An Introduction. Oxford University Press, USA, 2010, p. 720.
    

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

if __name__ == '__main__':
    import numpy as np 

    # Generate a random Graph (random matrix)
    n = 200
    p = 0.01
    G = nx.fast_gnp_random_graph(n,p)
    A = nx.adj_matrix(G,nodelist=G.nodes())
    
    eigenvalues,eigenvectors=np.linalg.eig(A)
    #  largest eigenvalue
    largest = np.array(eigenvalues).max().real
    
    alpha = 1./(largest+0.2)
    centrality_numpy = katz_centrality_numpy(G, alpha)
    centrality  = katz_centrality(G,alpha)
    #print sum([abs(centrality[n] - centrality_numpy[n]) for n in centrality])

    #Test 
    G=nx.path_graph(3)
    alpha = 0.1
    centrality_numpy = katz_centrality_numpy(G, alpha)
    print centrality_numpy

    #Test
    alpha = 0.1 
    G=nx.DiGraph()
    edges=[(1,2),(1,3),(2,4),(3,2),(3,5),(4,2),(4,5),(4,6),(5,6),(5,7),(5,8),(6,8),(7,1),(7,5),(7,8),(8,6),(8,7)]
    G.add_edges_from(edges,weight=2.0)
    centrality_numpy = katz_centrality_numpy(G, alpha)
    print centrality_numpy

    #Test
    G=nx.path_graph(4)
    eigenvalues,eigenvectors=np.linalg.eig(A)
    largest_eigenvalue = np.array(eigenvalues).max().real
    alpha = 1./(largest_eigenvalue+0.2)
    centrality=nx.eigenvector_centrality(G)
    print(['%s %0.2f'%(node,centrality[node]) for node in centrality])