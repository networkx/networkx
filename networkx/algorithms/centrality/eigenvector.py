"""
Eigenvector centrality.
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
                        'Sasha Gutfraind (ag362@cornell.edu)'])
__all__ = ['eigenvector_centrality',
           'eigenvector_centrality_numpy']

def eigenvector_centrality(G,max_iter=100,tol=1.0e-6,nstart=None):
    """Compute the eigenvector centrality for the graph G.

    Uses the power method to find the eigenvector for the 
    largest eigenvalue of the adjacency matrix of G.

    Parameters
    ----------
    G : graph
      A networkx graph 

    max_iter : interger, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of eigenvector iteration for each node. 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> centrality=nx.eigenvector_centrality(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    ------
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    For directed graphs this is "right" eigevector centrality.  For
    "left" eigenvector centrality, first reverse the graph with
    G.reverse().

    See Also
    --------
    eigenvector_centrality_numpy
    pagerank
    hits
    """
    from math import sqrt
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXException("Not defined for multigraphs.")

    if len(G)==0:
        raise nx.NetworkXException("Empty graph.")

    if nstart is None:
        # choose starting vector with entries of 1/len(G) 
        x=dict([(n,1.0/len(G)) for n in G])
    else:
        x=nstart
    # normalize starting vector
    s=1.0/sum(x.values())
    for k in x: x[k]*=s
    nnodes=G.number_of_nodes()
    # make up to max_iter iterations        
    for i in range(max_iter):
        xlast=x
        x=dict.fromkeys(xlast, 0)
        # do the multiplication y=Ax
        for n in x:
            for nbr in G[n]:
                x[n]+=xlast[nbr]*G[n][nbr].get('weight',1)
        # normalize vector
        try:
            s=1.0/sqrt(sum(v**2 for v in x.values()))
        # this should never be zero?
        except ZeroDivisionError:
            s=1.0
        for n in x: x[n]*=s
        # check convergence            
        err=sum([abs(x[n]-xlast[n]) for n in x])
        if err < nnodes*tol:
            return x

    raise nx.NetworkXError("""eigenvector_centrality(): 
power iteration failed to converge in %d iterations."%(i+1))""")


def eigenvector_centrality_numpy(G):
    """Compute the eigenvector centrality for the graph G.

    Parameters
    ----------
    G : graph
      A networkx graph 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with eigenvector centrality as the value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> centrality=nx.eigenvector_centrality_numpy(G)
    >>> print(['%s %0.2f'%(node,centrality[node]) for node in centrality])
    ['0 0.37', '1 0.60', '2 0.60', '3 0.37']

    Notes
    ------
    This algorithm uses the NumPy eigenvalue solver.

    For directed graphs this is "right" eigevector centrality.  For
    "left" eigenvector centrality, first reverse the graph with
    G.reverse().

    See Also
    --------
    eigenvector_centrality
    pagerank
    hits
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError('Requires NumPy: http://scipy.org/')

    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXException('Not defined for multigraphs.')

    if len(G)==0:
        raise nx.NetworkXException('Empty graph.')

    A=nx.adj_matrix(G,nodelist=G.nodes())
    eigenvalues,eigenvectors=np.linalg.eig(A)
    # eigenvalue indices in reverse sorted order
    ind=eigenvalues.argsort()[::-1]
    # eigenvector of largest eigenvalue at ind[0], normalized
    largest=np.array(eigenvectors[:,ind[0]]).flatten().real
    norm=np.sign(largest.sum())*np.linalg.norm(largest)
    centrality=dict(zip(G,map(float,largest/norm)))
    return centrality


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
        import numpy.linalg
    except:
        raise SkipTest("numpy not available")
