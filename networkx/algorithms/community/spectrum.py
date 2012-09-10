import networkx as nx
from collections import defaultdict
from itertools import repeat
from math import sqrt
from networkx.utils.decorators import require

def adjacency_matrix(G,weight=None):
    A = {}
    for u in G:
        A[u] = defaultdict(repeat(0).next)
        for v in G.neighbors_iter(u):
            A[u][v] = G[u][v].get(weight,1.0)
    return A

def laplacian(G,weight=None):
    L = {}
    for u in G:
        L[u] = defaultdict(repeat(0).next)
        L[u][u] = G.degree(u)
        for v in G.neighbors_iter(u):
            L[u][v] -= G[u][v].get(weight,1)
    return L

def normalized_laplacian(G,weight=None):
    L = {}
    degrees = G.degree(weight=weight)
    for u in G:
        L[u] = defaultdict(repeat(0).next)
        L[u][u] = 1.0
        for v in G.neighbors_iter(u):
            L[u][v] -= G[u][v].get(weight,1.0)/sqrt(degrees(u)*degrees(v))
    return L

def normalized_directed_laplacian(G,weight=None,walk_type=None,alpha=0.99):
    if not G.is_directed():
        nx.NetworkxError("Directed Laplacian only implemented for directed graphs")

    if walk_type is None:
        if nx.is_strongly_connected(G):
            if nx.is_aperiodic(G):
                walk_type = "random"
            else:
                walk_type = "lazy"
        else:
            walk_type = "pagerank"

    n = float(G.order())
    degrees = G.out_degree(weight=weight)

    if walk_type == "random":
        P = dict((u,defaultdict(repeat(0.0).next)) for u in G)
        pi = stationary_distribution(G,weight=weight)
        for u in G:
            for v in G[u]:
                P[u][v] = G[u][v].get(weight,1.0)/float(degrees[u])
    elif walk_type == "lazy":
        P = dict((u,defaultdict(repeat(0.0).next)) for u in G)
        pi = lazy_stationary_distribution(G,weight=weight)
        for u in G:
            P[u][u] = .5
            for v in G[u]:
                P[u][v] += G[u][v].get(weight,1.0)/float(degrees[u]*2)
    elif walk_type == "pagerank":
        P = dict((u,defaultdict(repeat((1.0-alpha)/n).next)) for u in G)
        pi = pagerank_stationary_distribution(G,weight=weight)
        for u in G:
            for v in G[u]:
                P[u][v] += alpha*G[u][v].get(weight,1.0)/float(degrees[u])
        L = dict((u,defaultdict()) for u in G)
        for u in G: # do this as a special case, cause this is actually a dense matrix
            L[u] = defaultdict()
            for v in G:
                L[u][v] = .5*(sqrt(pi[u])*P[u][v]*(1/sqrt(pi[v])) + (1/sqrt(pi[u]))*P[v][u]*sqrt(pi[v]))
            L[u][u] = 1.0 - L[u][u]
        return L
        
    else:
        raise nx.NetworkXError("walk_type must be random, lazy, or pagerank")


    L = dict((u,defaultdict(repeat(0.0).next)) for u in G)
    for u in G:
        L[u][u] = 1.0
        for v in G[u]:
            L[u][v] -= .5*(sqrt(pi[u])*P[u][v]*(1/sqrt(pi[v])) + (1/sqrt(pi[u]))*P[v][u]*sqrt(pi[v]))
            if not u in G[v]:
                L[v][u] = L[u][v]

    return L

def stationary_distribution(G,x_init=None,weight=None,tol=1.e-8,max_steps=1000):
    n = G.order()
    if x_init is None:
        ds = float(sum(G.in_degree(weight=weight).values()))
        x = dict((v,G.in_degree(v,weight=weight)/ds) for v in G)
    else:
        x_norm = sum(x_init[v] for v in x_init)
        x = dict((v,x_init[v]/x_norm) for v in x_init)

    degrees = G.out_degree(weight=weight)
    i = 0
    while True:
        x_new = {}
        err = 0.0
        for u in G:
            x_new[u] = sum(x[v]*G[v][u].get(weight,1.0)/degrees[v]
                           for v in G.predecessors_iter(u))
            err += abs(x[u] - x_new[u])
        x = x_new
        i += 1
        if err < tol*n:
            break
        if i > max_steps:
            raise nx.NetworkXError("Could not converge")
    return x

def lazy_stationary_distribution(G,x_init=None,weight=None,tol=1.e-8,max_steps=1000):
    n = G.order()
    if x_init is None:
        ds = float(sum(G.in_degree(weight=weight).values()))
        x = dict((v,G.in_degree(v,weight=weight)/ds) for v in G)
    else:
        x_norm = sum(x_init[v] for v in x_init)
        x = dict((v,x_init[v]/x_norm) for v in x_init)

    degrees = G.out_degree(weight=weight)
    i = 0
    while True:
        x_new = {}
        err = 0.0
        for u in G:
            x_new[u] = sum(x[v]*G[v][u].get(weight,1.0)/(degrees[v]*2.0)
                           for v in G.predecessors_iter(u))
            x_new[u] += x[u]/2.
            err += abs(x[u] - x_new[u])
        x = x_new
        i += 1
        if err < tol*n:
            break
        if i > max_steps:
            raise nx.NetworkXError("Could not converge")
    return x

def pagerank_stationary_distribution(G,alpha=.99,x_init=None,weight=None,tol=1.e-8,max_steps=1000):
    n = G.order()
    if x_init is None:
        ds = float(sum(G.in_degree(weight=weight).values()))
        x = dict((u,G.in_degree(u,weight=weight)/ds) for u in G)
    else:
        x_norm = sum(x_init[u] for u in x_init)
        x = dict((n,x_init[u]/x_norm) for u in x_init)

    degrees = G.out_degree(weight=weight)
    i = 0
    while True:
        x_new = {}
        err = 0.0
        for u in G:
            x_new[u] = sum(alpha*x[v]*G[v][u].get(weight,1.0)/degrees[v]
                           for v in G.predecessors_iter(u))
            x_new[u] += (1.0-alpha)
            err += abs(x[u] - x_new[u])
        x = x_new
        i += 1
        if err < tol*n:
            break
        if i > max_steps:
            raise nx.NetworkXError("Could not converge")
    return x

def adjacency_matrix_numpy(G,nodelist=None,weight='weight'):
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

@require('numpy')
def laplacian_numpy(G,nodelist=None,weight='weight'):
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
    import numpy as np

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

@require('numpy')
def normalized_laplacian_numpy(G,nodelist=None,weight='weight'):
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

    See Also
    --------
    laplacian

    References
    ----------
    .. [1] Fan Chung-Graham, Spectral Graph Theory, 
       CBMS Regional Conference Series in Mathematics, Number 92, 1997.
    """
    # FIXME: this isn't the most efficient way to do this...
    import numpy as np
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



def sparse_normalized_directed_laplacian(G, nodelist=None, weight='weight', walk='simple'):
    laplacian_type={'simple':simple_directed_laplacian,
                    'lazy':lazy_directed_laplacian,
                    'pagerank':pagerank_directed_laplacian}
    try:
        return laplacian_type[walk](G, nodelist=nodelist, weight='weight')
    except KeyError:
        raise nx.NetworkXError('walk must be simple|lazy|pagerank')

@require('numpy')
def laplacian_eigenvector(G, weight='weight'):
    import numpy as np
    if G.is_directed():
        raise nx.NetworkXError('laplacian_eigenvector() ',
                            'not implemented for directed graphs.')

         # test explicitly because we really only need numpy
    try: # use sparse solver if we have scipy
        from scipy.sparse import spdiags
        from scipy.sparse.linalg import eigsh
        sparse = True
    except ImportError: # fall back to numpy dense solver
        sparse = False

    n = len(G)
    if n < 200: # dense solver is faster for small graphs
        sparse = False

    # set up sparse or dense Laplacian and eigensolver
    if sparse:
        # number of Lanczos vectors for ARPACK solver is np.sqrt(n)
        # what is a good value?
        eigsolver = partial(eigsh,k=2,which='SM',ncv=int(np.sqrt(n)))
        if G.is_directed():
            laplacian = nx.sparse_directed_laplacian
        else:
            laplacian = nx.sparse_laplacian
    else:
        eigsolver = np.linalg.eig
        if G.is_directed():
            laplacian = directed_laplacian
        else:
            laplacian = nx.laplacian

    # create Laplacian and find eigenvalues
    L = laplacian(G,weight=weight)
    eigenvalues,eigenvectors = eigsolver(L)    
    # sort and keep smallest nonzero 
    index = np.argsort(eigenvalues)[1] # 0 index is zero eigenvalue
    v2 = zip(G,np.real(eigenvectors[:,index]))
    return v2

@require('scipy.sparse')
def sparse_laplacian(G,nodelist=None,weight='weight'):
    # form Laplacian matrix
    from scipy.sparse import spdiags
    A = nx.to_scipy_sparse_matrix(G, nodelist=nodelist, weight=weight)
    data = np.asarray(A.sum(axis=1).T)
    D = spdiags(data,0,n,n)
    return  D-A



