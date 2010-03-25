#!/usr/bin/env python
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/. 
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

import networkx
from networkx.exception import NetworkXError
__all__ = ['pagerank','pagerank_numpy','pagerank_scipy','google_matrix']

def pagerank(G,alpha=0.85,max_iter=100,tol=1.0e-8,nstart=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes the largest eigenvector of the stochastic
    adjacency matrix of G.  
    

    Parameters
    -----------
    G : graph
      A networkx graph 

    alpha : float, optional
      Parameter for PageRank, default=0.85
       
    max_iter : interger, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of PageRank iteration for each node. 

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with value as PageRank 


    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.pagerank(G,alpha=0.9)

    Notes
    -----
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    The PageRank algorithm was designed for directed graphs but this
    algorithm does not check if the input graph is directed and will
    execute on undirected graphs.

    For an overview see:
    A. Langville and C. Meyer, "A survey of eigenvector methods of web
    information retrieval."  http://citeseer.ist.psu.edu/713792.html

    """
    import networkx
    if type(G) == networkx.MultiGraph or type(G) == networkx.MultiDiGraph:
        raise Exception("pagerank() not defined for graphs with multiedges.")

    # create a copy in (right) stochastic form        
    W=networkx.stochastic_graph(G)        

    # choose fixed starting vector if not given
    if nstart is None:
        x=dict.fromkeys(W,1.0/W.number_of_nodes())
    else:
        x=nstart
        # normalize starting vector to 1                
        s=1.0/sum(x.values())
        for k in x: x[k]*=s

    nnodes=W.number_of_nodes()
    # "dangling" nodes, no links out from them
    out_degree=W.out_degree(with_labels=True)
#    dangle=[n for n in W if sum(W[n].values())==0.0]  
    dangle=[n for n in W if out_degree[n]==0.0]  
    # pagerank power iteration: make up to max_iter iterations        
    for i in range(max_iter):
        xlast=x
        x=dict.fromkeys(xlast.keys(),0)
        danglesum=alpha/nnodes*sum(xlast[n] for n in dangle)
        teleportsum=(1.0-alpha)/nnodes*sum(xlast.values())
        for n in x:
            # this matrix multiply looks odd because it is
            # doing a left multiply x^T=xlast^T*W
            for nbr in W[n]:
                x[nbr]+=alpha*xlast[n]*W[n][nbr]['weight']
            x[n]+=danglesum+teleportsum
        # normalize vector to 1                
        s=1.0/sum(x.values())
        for n in x: x[n]*=s
        # check convergence, l1 norm            
        err=sum([abs(x[n]-xlast[n]) for n in x])
        if err < tol:
            return x

    raise NetworkXError("pagerank: power iteration failed to converge in %d iterations."%(i+1))



def google_matrix(G,alpha=0.85,nodelist=None):
    import numpy
    import networkx
    M=networkx.to_numpy_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    # add constant to dangling nodes' row
    dangling=numpy.where(M.sum(axis=1)==0)
    for d in dangling[0]:
        M[d]=1.0/n
    # normalize        
    M=M/M.sum(axis=1)
    # add "teleportation"
    P=alpha*M+(1-alpha)*numpy.ones((n,n))/n
    return P
    

def pagerank_numpy(G,alpha=0.85,max_iter=100,tol=1.0e-6,nodelist=None):
    """Return a NumPy array of the PageRank of G.
    """
    import numpy
    import networkx
    M=networkx.google_matrix(G,alpha,nodelist)   
    (n,m)=M.shape # should be square
    x=numpy.ones((n))/n
    for i in range(max_iter):
        xlast=x
        x=numpy.dot(x,M)
        # check convergence, l1 norm            
        err=numpy.abs(x-xlast).sum()
        if err < n*tol:
            return numpy.asarray(x).flatten()

    raise NetworkXError("pagerank: power iteration failed to converge in %d iterations."%(i+1))



def pagerank_scipy(G,alpha=0.85,max_iter=100,tol=1.0e-6,nodelist=None):
    """Return a SciPy sparse array of the PageRank of G.

    """
    import scipy.sparse
    import networkx
    M=networkx.to_scipy_sparse_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    S=scipy.array(M.sum(axis=1)).flatten()
    index=scipy.where(S<>0)[0]
    for i in index:
        M[i,:]*=1.0/S[i]
    x=scipy.ones((n))/n  # initial guess
    dangle=scipy.array(scipy.where(M.sum(axis=1)==0,1.0/n,0)).flatten()
    for i in range(max_iter):
        xlast=x
        x=alpha*(x*M+scipy.dot(dangle,xlast))+(1-alpha)*xlast.sum()/n
        # check convergence, l1 norm            
        err=scipy.absolute(x-xlast).sum()
        if err < n*tol:
            return x
    raise NetworkXError("pagerank_scipy: power iteration failed to converge in %d iterations."%(i+1))

