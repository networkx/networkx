"""MICMAC analysis method of graph structure. """
#    Copyright (C) 2013 by
#    Jorge Catumba <jorgerev90@gmail.com>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/
import networkx as nx
__author__ = """Jorge Catumba (jorgerev90@gmail.com)"""
__all__ = ['micmac']

def micmac(G, k=4):
    """Return the MICMAC indirect influences and indirect dependences
    of the nodes in the graph.

    MICMAC computes the paths graph of size k in the graph G.

    Parameters
    -----------
    G : graph
      A NetworkX graph

    k : integer, optional
      Paramenter of the MICMAC method, default=4

    Returns
    -------
    indirect : dictionary
       Dictionary of MICMAC indirect dependences and influences

    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.micmac(G,k=3)

    Notes
    -----
    This function uses SciPy and NumPy libraries to make the computations.
    A NetworkX DiGraph is prefered because on an undirected Graph
    indirect dependences are equal to indirect dependeces.

    See Also
    --------
    pwp, heatkernel

    References
    ----------
    .. [1] R. Diaz,
       Indirect Influences, 
       Advanced Studies in Contemporary Mathematics 23 (2013) 29-41. 
       http://arxiv.org/abs/0906.1610
    .. [2] M. Godet,
       De l'Anticipation a l'Action, Dunod, Paris 1992.
    """
    
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
            "micmac() requires SciPy: http://scipy.org/")
            
    try:
        import numpy.linalg as lin
    except ImportError:
        raise ImportError(\
            "micmac() requires numpy.linalg: http://docs.scipy.org/doc/numpy/reference/routines.linalg.html")
            
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("micmac() not defined for Multi[Di]Graphs.")

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G
    
    # Get order of Graph
    j = D.order()
    # Get the adjacency matrix of the graph
    A = nx.adjacency_matrix(D)
    # transpose the adjacency matrix
    A = np.transpose(A)
    
    # get the k-th power of A
    I = lin.matrix_power(A, k)
    
    # get the indirect influences vector
    f = np.sum(I, axis=0)
    f = f/np.sum(f)
    
    # get the indirect dependences vector
    d = np.sum(I, axis=1)
    d = d/np.sum(d)
    
    #create the dictionary with the result
    fdict = dict( zip(D, f.tolist()[0]) )
    ddict = dict( zip(D, d.transpose().tolist()[0]) )
    x = {'influences': fdict, 'dependences': ddict}
    return x

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("numPy not available")
    try:
        import numpy.linalg
    except:
        raise SkipTest("NumPy.linalg not available")
