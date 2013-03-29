import numpy as np
import networkx as nx

__author__ = ['Federico Vaggi (federico.vaggi@fmach.it)']

__all__ = ['linalg_clustering']

def linalg_clustering(G, weight = 'weight'):
    r""""    For unweighted graphs the clustering of each node `u`
    is the fraction of possible triangles that exist,
    For each node find the fraction of possible triangles that exist,
    
    .. math::
    
      c_u = \frac{2 T(u)}{deg(u)(deg(u)-1)},
    
    where `T(u)` is the number of triangles through node `u` and
    `deg(u)` is the degree of `u`.
    
    For directed graphs, the maximum number of triangles is:
    
    .. math::
    
      c_u = \frac{2 T(u)}{deg(u)(deg(u)-1)-deg_{double}(u)},
    
    where `T(u)` is the number of triangles through node `u`,
    `deg(u)` is the degree of `u`, and `deg_{double}(u)` is
    the number of mutual edges that `u` has with other nodes.
    
    For weighted graphs the clustering is defined
    as the geometric average of the subgraph edge weights [1]_,
    
    .. math::
    
       c_u = \frac{1}{deg(u)(deg(u)-1))}
            \sum_{uv} (\hat{w}_{uv} \hat{w}_{uw} \hat{w}_{vw})^{1/3}.
      
    The edge weights `\hat{w}_{uv}` are normalized by the maximum weight in the
    network `\hat{w}_{uv} = w_{uv}/\max(w)`.
    
    
    The value of `c_u` is assigned to 0 if `deg(u) < 2`.
    
    Parameters
    ----------
    G : graph
    
    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.
    
    Returns
    -------
    out : dictionary
       Clustering coefficient for all nodes    """
    
    W = np.abs(nx.adjacency_matrix(G, weight = weight))
    W = W / np.max(W)
    A = np.array(W != 0, dtype = int)
    
    d_out = np.sum(A, axis = 1).flatten()
    d_in = np.sum(A, axis = 0).flatten()
    d_tot = np.array(d_out + d_in, dtype = float)
    d_double = np.diag(np.dot(A,A))
    
    C = np.power(W, (1/3.0)) + np.power(W.T, (1/3.0))
    C = np.diagonal(np.dot(C,C).dot(C))
    # Actual number of triangles present
    max_triangles = 2*(d_tot*(d_tot-1)-2*d_double)
    # Maximum number of triangles, the -2*d_double factor
    # accounts for the presence of double edges.
    C /= max_triangles
    C[max_triangles == 0] = 0
    # If there are 0 possible triangles, then C is 0.
    C = dict(zip(G.nodes(),C))
    # Return as a dict to follow networkx API standards.
    return C