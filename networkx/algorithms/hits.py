#!/usr/bin/env python
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/ 
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
import networkx
from networkx.exception import NetworkXError
__all__ = ['hits','hits_numpy','hits_scipy','authority_matrix','hub_matrix']

def hits(G,max_iter=100,tol=1.0e-8,nstart=None):
    """Return HITS hubs and authorities values for nodes.

    Parameters
    -----------
    G : graph
      A networkx graph 
       
    max_iter : interger, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of each node for power method iteration.

    Returns
    -------
    (hubs,authorities) : two-tuple of dictionaries
       Two dictionaries keyed by node containing the hub and authority
       values.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> h,a=nx.hits(G)

    Notes
    -----
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    The HITS algorithm was designed for directed graphs but this
    algorithm does not check if the input graph is directed and will
    execute on undirected graphs.

    For an overview see:
    A. Langville and C. Meyer, "A survey of eigenvector methods of web
    information retrieval."  http://citeseer.ist.psu.edu/713792.html

    """
    import networkx
    if type(G) == networkx.MultiGraph or type(G) == networkx.MultiDiGraph:
        raise Exception("hits() not defined for graphs with multiedges.")

#    if not G.weighted:
#        raise Exception("hits(): input graph must be weighted")

    # choose fixed starting vector if not given
    if nstart is None:
        h=dict.fromkeys(G,1.0/G.number_of_nodes())
    else:
        h=nstart
        # normalize starting vector 
        s=1.0/sum(h.values())
        for k in x: h[k]*=s
    nnodes=G.number_of_nodes()
    # power iteration: make up to max_iter iterations        
    for i in range(max_iter):
        hlast=h
        h=dict.fromkeys(hlast.keys(),0)
        a=dict.fromkeys(hlast.keys(),0)
        # this "matrix multiply" looks odd because it is
        # doing a left multiply a^T=hlast^T*G 
        for n in h:
            for nbr in G[n]:
                a[nbr]+=hlast[n]*G[n][nbr].get('weight',1)
        # now multiply h=Ga
        for n in h:
            for nbr in G[n]:
                h[n]+=a[nbr]*G[n][nbr].get('weight',1)
        # normalize vector 
        s=1.0/sum(h.values())
        for n in h: h[n]*=s
        # normalize vector 
        s=1.0/sum(a.values())
        for n in a: a[n]*=s
        # check convergence, l1 norm            
        err=sum([abs(h[n]-hlast[n]) for n in h])
        if err < tol:
            return h,a

    raise NetworkXError("HITS: power iteration failed to converge in %d iterations."%(i+1))


def authority_matrix(G,nodelist=None):
    """Return the HITS authority matrix."""
    import networkx
    M=networkx.to_numpy_matrix(G,nodelist=nodelist)
    return M.T*M

def hub_matrix(G,nodelist=None):
    """Return the HITS hub matrix."""
    import networkx
    M=networkx.to_numpy_matrix(G,nodelist=nodelist)
    return M*M.T


def hits_numpy(G,max_iter=100,tol=1.0e-6,nodelist=None):
    """Return a NumPy array of the hubs and authorities."""
    import numpy
    import networkx
    M=networkx.to_numpy_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    A=M.T*M # authority matrix
    x=numpy.ones((n,1))/n
    # power iteration on authority matrix
    for i in range(max_iter):
        xlast=x
        x=numpy.dot(A,x)
        x=x/x.sum()
        # check convergence, l1 norm            
        err=numpy.abs(x-xlast).sum()
        if err < n*tol:
            a=numpy.asarray(x).flatten()
            # h=M*a
            h=numpy.asarray(numpy.dot(M,a)).flatten()
            h/=h.sum()
            return h,a

    raise NetworkXError("page_rank: power iteration failed to converge in %d iterations."%(i+1))


def hits_scipy(G,max_iter=100,tol=1.0e-6,nodelist=None):
    """Return a SciPy sparse array of the hubs and authorities."""
    import numpy
    import scipy.sparse
    import networkx
    M=networkx.to_scipy_sparse_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    A=M.T*M # authority matrix
    x=scipy.ones((n,1))/n  # initial guess
    # power iteration on authority matrix
    for i in range(max_iter):
        xlast=x
        x=A*x
        x=x/x.sum()
        # check convergence, l1 norm            
        err=scipy.absolute(x-xlast).sum()
        if err < n*tol:
            a=numpy.asarray(x).flatten()
            # h=M*a
            h=numpy.asarray(M*a).flatten()
            h/=h.sum()
            return h,a

    raise NetworkXError("page_rank: power iteration failed to converge in %d iterations."%(i+1))

