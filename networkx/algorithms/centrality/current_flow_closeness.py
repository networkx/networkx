"""
Current-flow closeness centrality measures.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['current_flow_closeness_centrality','information_centrality']

import networkx as nx

def current_flow_closeness_centrality(G,normalized=True):
    """Compute current-flow closeness centrality for nodes.

    A variant of closeness centrality based on effective
    resistance between nodes in a network.  This metric
    is also known as information centrality.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the values are normalized by 1/(n-1) where n is the 
      number of nodes in G.
       
    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with current flow closeness centrality as the value.
        
    See Also
    --------
    closeness_centrality

    Notes
    -----
    The algorithm is from Brandes [1]_.

    See also [2]_ for the original definition of information centrality.

    References
    ----------
    .. [1] Ulrik Brandes and Daniel Fleischer,
       Centrality Measures Based on Current Flow. 
       Proc. 22nd Symp. Theoretical Aspects of Computer Science (STACS '05). 
       LNCS 3404, pp. 533-544. Springer-Verlag, 2005. 
       http://www.inf.uni-konstanz.de/algo/publications/bf-cmbcf-05.pdf

    .. [2] Stephenson, K. and Zelen, M.
       Rethinking centrality: Methods and examples.
       Social Networks. Volume 11, Issue 1, March 1989, pp. 1-37
       http://dx.doi.org/10.1016/0378-8733(89)90016-6
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("flow_closeness_centrality() requires NumPy: http://scipy.org/ ")
    

    if G.is_directed():
        raise nx.NetworkXError(\
            "current_flow_closeness_centrality() not defined for digraphs.")

    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")

    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    n=len(G)
    mapping=dict(zip(G,list(range(n))))  # map nodes to integers
    C=_compute_C(G)
    for v in G:
        vi=mapping[v]
        for w in G:
            wi=mapping[w]
            betweenness[v]+=C[vi,vi]-2*C[wi,vi]
            betweenness[w]+=C[vi,vi]
                
    if normalized:
        nb=len(betweenness)-1.0
    else:
        nb=1.0
    for v in G:
        betweenness[v]=nb/(betweenness[v])
    return betweenness            


def _compute_C(G):
    """Compute inverse of Laplacian."""
    try:
        import numpy as np
    except ImportError:
        raise ImportError("flow_closeness_centrality() requires NumPy: http://scipy.org/ ")
    L=nx.laplacian(G) # use ordering of G.nodes()
    # remove first row and column
    LR=L[1:,1:]
    LRinv=np.linalg.inv(LR)
    C=np.zeros(L.shape)
    C[1:,1:]=LRinv
    return C

information_centrality=current_flow_closeness_centrality

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")

