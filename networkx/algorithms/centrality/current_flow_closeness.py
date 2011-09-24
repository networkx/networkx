"""
Current-flow closeness centrality measures.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg <aric.hagberg@gmail.com>"""

__all__ = ['current_flow_closeness_centrality','information_centrality']

import networkx as nx
from networkx.algorithms.centrality.flow_matrix import *
    

def current_flow_closeness_centrality(G, normalized=True, weight='weight', 
                                      dtype=float, solver='lu'):
    """Compute current-flow closeness centrality for nodes.

    A variant of closeness centrality based on effective
    resistance between nodes in a network.  This metric
    is also known as information centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph 

    normalized : bool, optional
      If True the values are normalized by 1/(n-1) where n is the 
      number of nodes in G.

    dtype: data type (float)
      Default data type for internal matrices.
      Set to np.float32 for lower memory consumption.

    solver: string (default='lu')
       Type of linear solver to use for computing the flow matrix.
       Options are "full" (uses most memory), "lu" (recommended), and 
       "cg" (uses least memory).

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
    from networkx.utils import reverse_cuthill_mckee_ordering 
    try:
        import numpy as np
    except ImportError:
        raise ImportError('current_flow_closeness_centrality requires NumPy ',
                          'http://scipy.org/')
    try:
        import scipy 
    except ImportError:
        raise ImportError('current_flow_closeness_centrality requires SciPy ',
                          'http://scipy.org/')
    if G.is_directed():
        raise nx.NetworkXError('current_flow_closeness_centrality ',
                               'not defined for digraphs.')
    if G.is_directed():
        raise nx.NetworkXError(\
            "current_flow_closeness_centrality() not defined for digraphs.")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    solvername={"full" :FullInverseLaplacian,
                "lu": SuperLUInverseLaplacian,
                "cg": CGInverseLaplacian}
    n = G.number_of_nodes()
    ordering = list(reverse_cuthill_mckee_ordering(G))
    # make a copy with integer labels according to rcm ordering
    # this could be done without a copy if we really wanted to
    H = nx.relabel_nodes(G,dict(zip(ordering,range(n))))
    betweenness = dict.fromkeys(H,0.0) # b[v]=0 for v in H
    n = G.number_of_nodes()
    L = laplacian_sparse_matrix(H, nodelist=range(n), weight=weight, 
                                dtype=dtype, format='csc')
    C2 = solvername[solver](L, width=1, dtype=dtype) # initialize solver
    for v in H:
        col=C2.get_row(v)
        for w in H:
            betweenness[v]+=col[v]-2*col[w]
            betweenness[w]+=col[v]

    if normalized:
        nb=len(betweenness)-1.0
    else:
        nb=1.0
    for v in H:
        betweenness[v]=nb/(betweenness[v])
    return dict((ordering[k],v) for k,v in betweenness.items())

information_centrality=current_flow_closeness_centrality

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")

