"""
******
Layout
******

Node positioning algorithms for graph drawing.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['circular_layout',
           'random_layout',
           'shell_layout',
           'spring_layout',
           'spectral_layout',
           'fruchterman_reingold_layout']

import networkx as nx


def random_layout(G,dim=2):
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "random_layout() requires numpy: http://scipy.org/ "
    n=len(G)
    pos=np.asarray(np.random.random((n,dim)),dtype=np.float32)
    return dict(zip(G,pos))


def circular_layout(G, dim=2, scale=1):
    # dim=2 only
    """Position nodes on a circle.

    Parameters
    ----------
    G : NetworkX graph 

    dim : int 
       Dimension of layout, currently only dim=2 is supported

    scale : float
        Scale factor for positions 

    Returns
    -------
    dict : 
       A dictionary of positions keyed by node

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> pos=nx.circular_layout(G)
    
    Notes
    ------
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "circular_layout() requires numpy: http://scipy.org/ "
    t=np.arange(0,2.0*np.pi,2.0*np.pi/len(G),dtype=np.float32)
    pos=np.transpose(np.array([np.cos(t),np.sin(t)]))
    pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos))

def shell_layout(G,nlist=None,dim=2,scale=1):
    """Position nodes in concentric circles.

    Parameters
    ----------
    G : NetworkX graph 

    nlist : list of lists
       List of node lists for each shell.

    dim : int 
       Dimension of layout, currently only dim=2 is supported

    scale : float
        Scale factor for positions 

    Returns
    -------
    dict : 
       A dictionary of positions keyed by node

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> shells=[[0],[1,2,3]]
    >>> pos=nx.shell_layout(G,shells)
    
    Notes
    ------
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "shell_layout() requires numpy: http://scipy.org/ "
    if nlist==None:
        nlist=[G.nodes()] # draw the whole graph in one shell

    nshells=len(nlist)
    if len(nlist[0])==1:
        radius=0.0 # single node at center
    else:
        radius=1.0 # else start at r=1

    npos={}        
    for nodes in nlist:
        t=np.arange(0,2.0*np.pi,2.0*np.pi/len(nodes),dtype=np.float32)
        pos=np.transpose(np.array([radius*np.cos(t),radius*np.sin(t)]))
        npos.update(dict(zip(nodes,pos)))
        radius+=1.0

    # FIXME: rescale        
    return npos        


def fruchterman_reingold_layout(G,dim=2,
                                pos=None,
                                fixed=None,
                                iterations=50,
                                weighted=True,scale=1):
    """Position nodes using Fruchterman-Reingold force-directed algorithm. 

    Parameters
    ----------
    G : NetworkX graph 

    dim : int 
       Dimension of layout

    pos : dict
       Initial positions for nodes as a dictionary with node as keys
       and values as a list or tuple.  

    fixed : list
      Nodes to keep fixed at initial position.


    iterations : int
       Number of iterations of spring-force relaxation 

    weighted : boolean
        If True, use edge weights in layout 

    scale : float
        Scale factor for positions 

    Returns
    -------
    dict : 
       A dictionary of positions keyed by node

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> pos=nx.spring_layout(G)

    # The same using longer function name
    >>> pos=nx.fruchterman_reingold_layout(G)
    
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "fruchterman_reingold_layout() requires numpy: http://scipy.org/ "
    if fixed is not None:
        nfixed=dict(zip(G,range(len(G))))
        fixed=np.asarray([nfixed[v] for v in fixed])

    if pos is not None:
        pos_arr=np.asarray(np.random.random((len(G),dim)))
        for n,i in zip(G,range(len(G))):
            if n in pos:
                pos_arr[i]=np.asarray(pos[n])
    else:
        pos_arr=None


    try:
        # Sparse matrix 
        if len(G) < 500:  # sparse solver for large graphs
            raise ValueError
        A=nx.to_scipy_sparse_matrix(G)
        pos=_sparse_fruchterman_reingold(A,
                                         pos=pos_arr,
                                         fixed=fixed,
                                         dim=dim,
                                         iterations=iterations,
                                         weighted=weighted)
    except:
        A=nx.to_numpy_matrix(G)
        pos=_fruchterman_reingold(A,
                                  pos=pos_arr,
                                  fixed=fixed,
                                  dim=dim,
                                  iterations=iterations,
                                  weighted=weighted)
    if fixed is None:
        pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos))





spring_layout=fruchterman_reingold_layout


def _fruchterman_reingold(A,dim=2,
                          pos=None,
                          fixed=None,
                          iterations=50,
                          weighted=True):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold  
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "_fruchterman_reingold() requires numpy: http://scipy.org/ "

    try:
        nnodes,_=A.shape
    except AttributeError:
        raise nx.NetworkXError(
            "fruchterman_reingold() takes an adjacency matrix as input")
    
    A=np.asarray(A) # make sure we have an array instead of a matrix
    if not weighted: # use 0/1 adjacency instead of weights
        A=np.where(A==0,A,A/A)

    if pos==None:
        # random initial positions
        pos=np.asarray(np.random.random((nnodes,dim)),dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos=pos.astype(A.dtype)

    # optimal distance between nodes
    k=np.sqrt(1.0/nnodes) 
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    t=0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt=t/float(iterations+1) 
    delta = np.zeros((pos.shape[0],pos.shape[0],pos.shape[1]),dtype=A.dtype)
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(iterations):
        # matrix of difference between points
        for i in xrange(pos.shape[1]):
            delta[:,:,i]= pos[:,i,None]-pos[:,i]
        # distance between points
        distance=np.sqrt((delta**2).sum(axis=-1))
        # enforce minimum distance of 0.01
        distance=np.where(distance<0.01,0.01,distance)
        # displacement "force"
        displacement=np.transpose(np.transpose(delta)*\
                                  (k*k/distance**2-A*distance/k))\
                                  .sum(axis=1)
        # update positions            
        length=np.sqrt((displacement**2).sum(axis=1))
        length=np.where(length<0.01,0.1,length)
        delta_pos=np.transpose(np.transpose(displacement)*t/length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed]=0.0
        pos+=delta_pos
        # cool temperature
        t-=dt

    return pos


def _sparse_fruchterman_reingold(A,dim=2,
                                 pos=None,
                                 fixed=None,
                                 iterations=50,
                                 weighted=True):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold  
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    # Sparse version
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "_sparse_fruchterman_reingold() requires numpy: http://scipy.org/ "
    try:
        nnodes,_=A.shape
    except AttributeError:
        raise nx.NetworkXError(
            "fruchterman_reingold() takes an adjacency matrix as input")
    
    try:
        from scipy.sparse import spdiags,coo_matrix
    except ImportError:
        raise ImportError, \
          "_sparse_fruchterman_reingold() scipy numpy: http://scipy.org/ "
    
    # make sure we have a LIst of Lists representation
    try:
        A=A.tolil() 
    except:
        A=(coo_matrix(A)).tolil()

    if not weighted: # use 0/1 adjacency instead of weights
        A=np.where(A==0,A,A/A)

    if pos==None:
        # random initial positions
        pos=np.asarray(np.random.random((nnodes,dim)),dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos=pos.astype(A.dtype)

    # no fixed nodes
    if fixed==None:
        fixed=[]

    # optimal distance between nodes
    k=np.sqrt(1.0/nnodes) 
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    t=0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt=t/float(iterations+1) 

    displacement=np.zeros((dim,nnodes))
    for iteration in range(iterations):
        displacement*=0
        # loop over rows
        for i in range(A.shape[0]):
            if i in fixed:
                continue
            # difference between this row's node position and all others
            delta=(pos[i]-pos).T
            # distance between points
            distance=np.sqrt((delta**2).sum(axis=0))
            # enforce minimum distance of 0.01
            distance=np.where(distance<0.01,0.01,distance)
            # the adjacency matrix row
            Ai=np.asarray(A.getrowview(i).toarray())
            # displacement "force"
            displacement[:,i]+=\
                (delta*(k*k/distance**2-Ai*distance/k)).sum(axis=1)
        # update positions            
        length=np.sqrt((displacement**2).sum(axis=0))
        length=np.where(length<0.01,0.1,length) 
        pos+=(displacement*t/length).T
        # cool temperature
        t-=dt

    return pos


def spectral_layout(G,dim=2,weighted=True,scale=1):
    """Position nodes using the eigenvectors of the graph Laplacian. 

    Parameters
    ----------
    G : NetworkX graph 

    dim : int 
       Dimension of layout

    weighted : boolean
        If True, use edge weights in layout 

    scale : float
        Scale factor for positions 

    Returns
    -------
    dict : 
       A dictionary of positions keyed by node

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> pos=nx.spectral_layout(G)

    Notes
    -----
    Directed graphs will be considered as unidrected graphs when
    positioning the nodes.

    For larger graphs (>500 nodes) this will use the SciPy sparse
    eigenvalue solver (ARPACK).
    """
    # handle some special cases that break the eigensolvers
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "spectral_layout() requires numpy: http://scipy.org/ "
    if len(G)<=2:
        if len(G)==0:
            pos=np.array([])
        elif len(G)==1:
            pos=np.array([[1,1]])
        else:
            pos=np.array([[0,0.5],[1,0.5]])
        return dict(zip(G,pos))
    try:
        # Sparse matrix 
        if len(G)< 500:  # dense solver is faster for small graphs
            raise ValueError
        A=nx.to_scipy_sparse_matrix(G)
        # Symmetrize directed graphs
        if G.is_directed():
            A=A+np.transpose(A)
        pos=_sparse_spectral(A,dim=dim,weighted=weighted)
    except (ImportError,ValueError):
        # Dense matrix
        A=nx.to_numpy_matrix(G)
        # Symmetrize directed graphs
        if G.is_directed():
            A=A+np.transpose(A)
        pos=_spectral(A,dim=dim,weighted=weighted)

    pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos))


def _spectral(A,dim=2,weighted=True):
    # Input adjacency matrix A
    # Uses dense eigenvalue solver from numpy
    try:
        import numpy as np
    except ImportError:
        raise ImportError, \
          "spectral_layout() requires numpy: http://scipy.org/ "
    try:
        nnodes,_=A.shape
    except AttributeError:
        raise nx.NetworkXError(\
            "spectral() takes an adjacency matrix as input")
    
    # form Laplacian matrix
    # make sure we have an array instead of a matrix
    A=np.asarray(A) 
    I=np.identity(nnodes,dtype=A.dtype)
    D=I*np.sum(A,axis=1) # diagonal of degrees
    L=D-A 

    eigenvalues,eigenvectors=np.linalg.eig(L)
    # sort and keep smallest nonzero 
    index=np.argsort(eigenvalues)[1:dim+1] # 0 index is zero eigenvalue
    return np.real(eigenvectors[:,index])

def _sparse_spectral(A,dim=2,weighted=True):
    # Input adjacency matrix A
    # Uses sparse eigenvalue solver from scipy
    # Could use multilevel methods here, see Koren "On spectral graph drawing" 
    
    try:
        from scipy.sparse import spdiags
        from scipy.sparse.linalg import eigen_symmetric
    except ImportError:
        raise ImportError, \
          "_sparse_spectral() scipy numpy: http://scipy.org/ "
    try:
        nnodes,_=A.shape
    except AttributeError:
        raise nx.NetworkXError(\
            "sparse_spectral() takes an adjacency matrix as input")
    
    # form Laplacian matrix
    data=np.asarray(A.sum(axis=1).T)
    D=spdiags(data,0,nnodes,nnodes)
    L=D-A
    # number of Lanczos vectors for ARPACK solver, what is the right scaling?
    ncv=int(np.sqrt(nnodes)) 
    # return smalest dim+1 eigenvalues and eigenvectors
    eigenvalues,eigenvectors=eigen_symmetric(L,dim+1,which='SM',ncv=ncv)
    index=np.argsort(eigenvalues)[1:dim+1] # 0 index is zero eigenvalue
    return np.real(eigenvectors[:,index])


def _rescale_layout(pos,scale=1):
    # rescale to (0,pscale) in all axes

    # shift origin to (0,0)
    lim=0 # max coordinate for all axes
    for i in xrange(pos.shape[1]):
        pos[:,i]-=pos[:,i].min()
        lim=max(pos[:,i].max(),lim)
    # rescale to (0,scale) in all directions, preserves aspect
    for i in xrange(pos.shape[1]):
        pos[:,i]*=scale/lim
    return pos


