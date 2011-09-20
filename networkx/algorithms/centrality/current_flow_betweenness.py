"""
Current-flow betweenness centrality measures.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['current_flow_betweenness_centrality',
           'edge_current_flow_betweenness_centrality']

import networkx as nx


def current_flow_betweenness_centrality(G, normalized=True, weight='weight',
                                        dtype=float):
    """Compute current-flow betweenness centrality for nodes.

    Current-flow betweenness centrality uses an electrical current
    model for information spreading in contrast to betweenness
    centrality which uses shortest paths.

    Current-flow betweenness centrality is also known as
    random-walk betweenness centrality [2]_.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional (default=True)
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.

    weight : string or None, optional (default='weight')
      Key for edge data used as the edge weight.
      If None, then use 1 as each edge weight.

    dtype: data type (float)
      Default data type for internal matrices.
      Set to np.float32 for lower memory consumption.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with betweenness centrality as the value.
        
    See Also
    --------
    betweenness_centrality
    edge_betweenness_centrality
    edge_current_flow_betweenness_centrality

    Notes
    -----
    The algorithm is from Brandes [1]_.

    If the edges have a 'weight' attribute they will be used as 
    weights in this algorithm.  Unspecified weights are set to 1.

    References
    ----------
    .. [1] Centrality Measures Based on Current Flow. 
       Ulrik Brandes and Daniel Fleischer,
       Proc. 22nd Symp. Theoretical Aspects of Computer Science (STACS '05). 
       LNCS 3404, pp. 533-544. Springer-Verlag, 2005. 
       http://www.inf.uni-konstanz.de/algo/publications/bf-cmbcf-05.pdf

    .. [2] A measure of betweenness centrality based on random walks,
       M. E. J. Newman, Social Networks 27, 39-54 (2005).
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError('current_flow_betweenness_centrality requires NumPy ',
                          'http://scipy.org/')
    if G.is_directed():
        raise nx.NetworkXError(\
            "current_flow_betweenness_centrality() not defined for digraphs.")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    m = G.number_of_edges()
    n = G.number_of_nodes()
    for Fe,(s,t) in flow_matrix_row(G,weight,dtype=dtype):
        # rank of F[ei,v] in row Fe sorted in non-increasing order
        pos=dict(zip(Fe.argsort()[::-1],range(1,n+1)))
        for i in range(n):
            betweenness[s]+=(i+1-pos[i])*Fe[i]
            betweenness[t]+=(n-i-pos[i])*Fe[i]
    if normalized:
        nb=(n-1.0)*(n-2.0) # normalization factor
    else:
        nb=2.0
    for i,v in enumerate(G): # map integers to nodes
        betweenness[v]=(betweenness[v]-i)*2.0/nb
    return betweenness


def edge_current_flow_betweenness_centrality(G, normalized=True,weight='weight',
                                             dtype=float):
    """Compute current-flow betweenness centrality for edges.

    Current-flow betweenness centrality uses an electrical current
    model for information spreading in contrast to betweenness
    centrality which uses shortest paths.

    Current-flow betweenness centrality is also known as
    random-walk betweenness centrality [2]_.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional (default=True)
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.

    weight : string or None, optional (default='weight')
      Key for edge data used as the edge weight.
      If None, then use 1 as each edge weight.

    dtype: data type (float)
      Default data type for internal matrices.
      Set to np.float32 for lower memory consumption.

    Returns
    -------
    nodes : dictionary
       Dictionary of edge tuples with betweenness centrality as the value.
        
    See Also
    --------
    betweenness_centrality
    edge_betweenness_centrality
    current_flow_betweenness_centrality

    Notes
    -----
    The algorithm is from Brandes [1]_.

    If the edges have a 'weight' attribute they will be used as 
    weights in this algorithm.  Unspecified weights are set to 1.

    References
    ----------
    .. [1] Centrality Measures Based on Current Flow. 
       Ulrik Brandes and Daniel Fleischer,
       Proc. 22nd Symp. Theoretical Aspects of Computer Science (STACS '05). 
       LNCS 3404, pp. 533-544. Springer-Verlag, 2005. 
       http://www.inf.uni-konstanz.de/algo/publications/bf-cmbcf-05.pdf

    .. [2] A measure of betweenness centrality based on random walks, 
       M. E. J. Newman, Social Networks 27, 39-54 (2005).
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError('current_flow_betweenness_centrality requires NumPy ',
                          'http://scipy.org/')
    if G.is_directed():
        raise nx.NetworkXError('current_flow_closeness_centrality ',
                               'not defined for digraphs.')
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    betweenness=(dict.fromkeys(G.edges(),0.0))
    m = G.number_of_edges()
    n = G.number_of_nodes()
    if normalized:
        nb=(n-1.0)*(n-2.0) # normalization factor
    else:
        nb=2.0
    for Fe,(e) in flow_matrix_row(G,weight,dtype=dtype):
        # rank of F[ei,v] in row Fe sorted in non-increasing order
        pos=dict(zip(Fe.argsort()[::-1],range(1,n+1)))
        for i in range(n):
            betweenness[e]+=(i+1-pos[i])*Fe[i]
            betweenness[e]+=(n-i-pos[i])*Fe[i]
        betweenness[e]/=nb
    return betweenness

def flow_matrix_row(G, weight='weight', dtype=float):
    """Current flow matrix."""
    import numpy as np
    L = nx.laplacian(G,weight=weight).astype(dtype)
    C = np.zeros(L.shape).astype(dtype)
    C[1:,1:] = np.linalg.inv(L[1:,1:])
    n = len(G)
    mapping=dict(zip(G,range(n)))  # map nodes to integers
    for (ei,(u,v,d)) in enumerate(G.edges_iter(data=True)): 
        B = np.zeros(n)
        c = d.get(weight,1.0)
        ui = mapping[u]
        vi = mapping[v]
        B[ui] = c
        B[vi] = -c
        row = np.dot(B,C)
        yield row,(u,v) # ei row of F with edge

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")

