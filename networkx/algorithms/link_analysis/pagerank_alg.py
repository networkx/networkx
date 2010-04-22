"""
PageRank analysis of graph structure.
"""
#!/usr/bin/env python
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/. 
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

import networkx as nx
from networkx.exception import NetworkXError
__all__ = ['pagerank','pagerank_numpy','pagerank_scipy','google_matrix']

def pagerank(G,alpha=0.85,max_iter=100,tol=1.0e-8,nstart=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.
    
    Parameters
    -----------
    G : graph
      A NetworkX graph 

    alpha : float, optional
      Damping parameter for PageRank, default=0.85
       
    max_iter : integer, optional
      Maximum number of iterations in power method eigenvalue solver.

    tol : float, optional
      Error tolerance used to check convergence in power method solver.

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
    execute on undirected graphs by converting each oriented edge in the
    directed graph to two edges.
    
    References
    ----------
    .. [1] A. Langville and C. Meyer, 
       "A survey of eigenvector methods of web information retrieval."  
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry, 
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("pagerank() not defined for graphs with multiedges.")

    if not G.is_directed():
        D=G.to_directed()
    else:
        D=G

    # create a copy in (right) stochastic form        
    W=nx.stochastic_graph(D)

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
    out_degree=W.out_degree()
    dangle=[n for n in W if out_degree[n]==0.0]  
    i=0
    while True: # power iteration: make up to max_iter iterations
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
            break
        if i>max_iter:
            raise NetworkXError(\
        "pagerank: power iteration failed to converge in %d iterations."%(i+1))
        i+=1
    return x


def google_matrix(G,alpha=0.85,nodelist=None):
    """Return the Google matrix of the graph.

    Parameters
    -----------
    G : graph
      A NetworkX graph 

    alpha : float
      The damping factor

    nodelist : list, optional       
      The rows and columns are ordered according to the nodes in nodelist.
      If nodelist is None, then the ordering is produced by G.nodes().

    Returns
    -------
    A : NumPy matrix
       Google matrix of the graph
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
            "google_matrix() requires NumPy: http://scipy.org/")
    M=nx.to_numpy_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    # add constant to dangling nodes' row
    dangling=np.where(M.sum(axis=1)==0)
    for d in dangling[0]:
        M[d]=1.0/n
    # normalize        
    M=M/M.sum(axis=1)
    # add "teleportation"
    P=alpha*M+(1-alpha)*np.ones((n,n))/n
    return P
    


def pagerank_numpy(G,alpha=0.85):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.
    
    Parameters
    -----------
    G : graph
      A NetworkX graph 

    alpha : float, optional
      Damping parameter for PageRank, default=0.85
       
    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with value as PageRank 

    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.pagerank_numpy(G,alpha=0.9)

    Notes
    -----
    The eigenvector calculation uses NumPy's interface to the LAPACK
    eigenvalue solvers.  

    This implementation works with Multi(Di)Graphs.
    
    References
    ----------
    .. [1] A. Langville and C. Meyer, 
       "A survey of eigenvector methods of web information retrieval."  
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry, 
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
            "pagerank_numpy() requires NumPy: http://scipy.org/")

    M=google_matrix(G,alpha,nodelist=G.nodes())
    # use numpy LAPACK solver
    eigenvalues,eigenvectors=np.linalg.eig(M.T)
    ind=eigenvalues.argsort()[::-1]
    # eigenvector of largest eigenvalue at ind[0], normalized
    largest=np.array(eigenvectors[:,ind[0]]).flatten()
    norm=largest.sum()
    centrality=dict(zip(G.nodes(),largest/norm))
    return centrality


def pagerank_scipy(G,alpha=0.85,max_iter=100,tol=1.0e-6,nodelist=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.
    
    Parameters
    -----------
    G : graph
      A NetworkX graph 

    alpha : float, optional
      Damping parameter for PageRank, default=0.85
       
    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with value as PageRank 

    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.pagerank_numpy(G,alpha=0.9)

    Notes
    -----
    The eigenvector calculation uses power iteration with a SciPy
    sparse matrix representation.
    
    References
    ----------
    .. [1] A. Langville and C. Meyer, 
       "A survey of eigenvector methods of web information retrieval."  
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry, 
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    try:
        import scipy.sparse
    except ImportError:
        raise ImportError(\
            "pagerank_scipy() requires SciPy: http://scipy.org/")
    if nodelist is None:
        nodelist=G.nodes()
    M=nx.to_scipy_sparse_matrix(G,nodelist=nodelist)
    (n,m)=M.shape # should be square
    S=scipy.array(M.sum(axis=1)).flatten()
    index=scipy.where(S<>0)[0]
    for i in index:
        M[i,:]*=1.0/S[i]
    x=scipy.ones((n))/n  # initial guess
    dangle=scipy.array(scipy.where(M.sum(axis=1)==0,1.0/n,0)).flatten()
    i=0
    while True: # power iteration: make up to max_iter iterations
        xlast=x
        x=alpha*(x*M+scipy.dot(dangle,xlast))+(1-alpha)*xlast.sum()/n
        # check convergence, l1 norm            
        err=scipy.absolute(x-xlast).sum()
        if err < n*tol:
            break
        if i>max_iter:
            raise NetworkXError(\
        "pagerank: power iteration failed to converge in %d iterations."%(i+1))
        i+=1
    centrality=dict(zip(G.nodes(),x))
    return centrality
