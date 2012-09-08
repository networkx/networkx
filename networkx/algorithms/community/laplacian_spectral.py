import bisect
import random
import networkx as nx

from functools import partial
from operator import itemgetter
from networkx.utils.decorators import requires


#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])


def spectral_bisection(G, weight='weight'):
    """Bisect the graph using the Laplacian eigenvectors.

    This method calculates the eigenvector v associated with the second
    largest eigenvalue of the Laplacian. The partition is defined by the
    nodes which are associated with either positive or negative values in v.

    Parameters
    ----------
    G : NetworkX Graph or MultiGraph
    weight : dict key
       Edge data key to use as weight.  If None the partition will use
       unweighted edges.

    Returns
    --------
    bisection : list of sets
      List with two sets of nodes

    Raises
    ------
    ImportError
      If NumPy is not available
    
    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> nx.spectral_partition(G)
    [set([9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]),
     set([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21])]

    Notes
    -----
    This algorithm splits the eigenvector at the value 0.

    References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', pages 364-370
       Oxford University Press 2011.
    """
    if not nx.is_connected(G):
        raise NetworkXError('graph is not connected')

    v2 = laplacian_eigenvector(G, weight=weight)
    cut_value = 0
    return [set([n for n,v in v2 if v < cut_value]),
            set([n for n,v in v2 if v >= cut_value])]
    

def directed_laplacian(G, nodelist=None, weight='weight', walk='simple'):
    L=sparse_directed_laplacian(G, nodelist=nodelist, weight=weight, walk=walk)
    return L.todense()

def simple_directed_laplacian(G, nodelist=None, weight='weight'):
    # G strongly connected, aperiodic
    import numpy as np
    from scipy.sparse import spdiags
    from scipy.sparse.linalg import eigsh
    n = len(G)
    A = nx.to_scipy_sparse_matrix(G,nodelist=nodelist,weight=weight)
    data = np.asarray(A.sum(axis=1).T)
    D_inv = spdiags(1.0/data,0,n,n)
    P = D_inv*A
    Pi = spdiags(eigsh(P,1,which='LM')[1].T,0,n,n)
    return identity(n) - (Pi*P + P.T*Pi)/2.0


def lazy_directed_laplacian(G, nodelist=None, weight='weight'):
    # G strongly connected, not aperiodic
    import numpy as np
    from scipy.sparse import spdiags,identity
    from scipy.sparse.linalg import eigsh
    n = len(G)
    A = nx.to_scipy_sparse_matrix(G,nodelist=nodelist,weight=weight)
    data = np.asarray(A.sum(axis=1).T)
    D_inv = spdiags(1.0/data,0,n,n)
    P = (identity(n) + D_inv*A)/2.0
    Pi = spdiags(eigsh(P,1,which='LM')[1].T,0,n,n)
    return identity(n) - (Pi*P + P.T*Pi)/2.0

def pagerank_directed_laplacian(G, nodelist=None, weight='weight',alpha=0.99):
    # G not strongly connected, not aperiodic
    import numpy as np
    n = len(G)
    A = nx.to_scipy_sparse_matrix(G,nodelist=nodelist,weight=weight)
    data = np.asarray(A.sum(axis=1).T)
    D_inv = np.diagflat(1.0/data)
    P = alpha*(D_inv*A) + (1-alpha)/n
    eigenvalues,eigenvectors = np.linalg.eig(P)
    index = np.argsort(eigenvalues)[0]
    Pi = np.diagflat(eigenvectors[:,index])
    return np.identity(n)-(Pi*P + P.T*Pi)/2.0

    
