"""
Current-flow betweenness centrality measures for subsets of nodes.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['current_flow_betweenness_centrality_subset',
           'edge_current_flow_betweenness_centrality_subset']

import networkx as nx

def current_flow_betweenness_centrality_subset(G,sources,targets,
                                               normalized=True,
                                               weight='weight'):
    """Compute current-flow betweenness centrality for subsets nodes.

    Current-flow betweenness centrality uses an electrical current
    model for information spreading in contrast to betweenness
    centrality which uses shortest paths.

    Current-flow betweenness centrality is also known as
    random-walk betweenness centrality [2]_.

    Parameters
    ----------
    G : graph
      A networkx graph 

    sources: list of nodes
      Nodes to use as sources for current

    targets: list of nodes
      Nodes to use as sinks for current

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.

    weight : string or None, optional (default='weight')
      Key for edge data used as the edge weight.
      If None, then use 1 as each edge weight.

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
        raise ImportError(
            """current_flow_betweenness_centrality_subset() requires NumPy 
http://scipy.org/""")

    if G.is_directed():
        raise nx.NetworkXError(\
            "current_flow_betweenness_centrality_subset() not defined for digraphs.")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    F=_compute_F(G,weight) # Current-flow matrix
    m,n=F.shape # m edges and n nodes
    mapping=dict(zip(G,range(n)))  # map nodes to integers
    for (ei,e) in enumerate(G.edges_iter()): 
        u,v=e
        # ei is index of edge
        Fe=F[ei,:] # ei row of F
        for s in sources:
            i=mapping[s]
            for t in targets:
                j=mapping[t]
                betweenness[u]+=0.5*np.abs(Fe[i]-Fe[j]) 
                betweenness[v]+=0.5*np.abs(Fe[i]-Fe[j]) 
    if normalized:
        nb=(n-1.0)*(n-2.0) # normalization factor
    else:
        nb=2.0
    for v in G:
        betweenness[v]=betweenness[v]/nb+1.0/(2-n)
    return betweenness


def edge_current_flow_betweenness_centrality_subset(G,sources,targets,
                                               normalized=True,
                                               weight='weight'):
    """Compute edge current-flow betweenness centrality for subsets
    of nodes.

    Current-flow betweenness centrality uses an electrical current
    model for information spreading in contrast to betweenness
    centrality which uses shortest paths.

    Current-flow betweenness centrality is also known as
    random-walk betweenness centrality [2]_.

    Parameters
    ----------
    G : graph
      A networkx graph 

    sources: list of nodes
      Nodes to use as sources for current

    targets: list of nodes
      Nodes to use as sinks for current

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.

    weight : string or None, optional (default='weight')
      Key for edge data used as the edge weight.
      If None, then use 1 as each edge weight.

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
        raise ImportError(
            """current_flow_betweenness_centrality_subset() requires NumPy 
http://scipy.org/""")

    if G.is_directed():
        raise nx.NetworkXError(\
            "edge_current_flow_closeness_centrality_subset() not defined for digraphs.")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    betweenness=(dict.fromkeys(G.edges(),0.0)) 
    F=_compute_F(G,weight) # Current-flow matrix
    m,n=F.shape # m edges and n nodes
    if normalized:
        nb=(n-1.0)*(n-2.0) # normalization factor
    else:
        nb=2.0
    mapping=dict(zip(G,range(n)))  # map nodes to integers
    for (ei,e) in enumerate(G.edges_iter()): 
        # ei is index of edge
        Fe=F[ei,:] # ei row of F
        for s in sources:
            i=mapping[s]
            for t in targets:
                j=mapping[t]
                betweenness[e]+=0.5*np.abs(Fe[i]-Fe[j])
        betweenness[e]/=nb
    return betweenness



def _compute_C(G,weight='weight'):
    """Inverse of Laplacian."""
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            """current_flow_betweenness_centrality_subset() requires NumPy 
http://scipy.org/""")

    L=nx.laplacian(G,weight=weight) # use ordering of G.nodes() 
    # remove first row and column
    LR=L[1:,1:]
    LRinv=np.linalg.inv(LR)
    C=np.zeros(L.shape)
    C[1:,1:]=LRinv
    return C

def _compute_F(G,weight='weight'):
    """Current flow matrix."""
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            """current_flow_betweenness_centrality_subset() requires NumPy 
http://scipy.org/""")
    C=np.asmatrix(_compute_C(G,weight))
    n=G.number_of_nodes()
    m=G.number_of_edges()
    B=np.zeros((n,m))
    # use G.nodes() and G.edges() ordering of edges for B  
    mapping=dict(zip(G,range(n)))  # map nodes to integers
    for (ei,(v,w,d)) in enumerate(G.edges_iter(data=True)): 
        c=d.get(weight,1.0)
        vi=mapping[v]
        wi=mapping[w]
        B[vi,ei]=c
        B[wi,ei]=-c
    return np.asarray(B.T*C)


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
