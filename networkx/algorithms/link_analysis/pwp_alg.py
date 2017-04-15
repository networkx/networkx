"""PWP analysis method of graph structure. """
#    Copyright (C) 2013 by
#    Jorge Catumba <jorgerev90@gmail.com>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/
import networkx as nx
__author__ = """Jorge Catumba (jorgerev90@gmail.com)"""
__all__ = ['pwp']

def pwp(G, k=1):
    """Return the PWP indirect influences and indirect dependences
    of the nodes in the graph.

    When two nodes on a DiGraph are connected with a directed
    edge we say that the source exerts a direct influence over the
    target and the target perceives a direct dependency from the source.
    The amount of such influences or dependences is given by the
    weight of the edge between them.

    PWP computes the indirect influences and dependences for all nodes
    in a DiGraph  via the exponential formula described in references.
    We call indirect influences and indirect dependences to the output of
    PWP and its related methods: Heat Kernel, MICMAC and PageRank.

    Parameters
    -----------
    G : graph
      A NetworkX [Di]Graph

    k : integer, optional
      Paramenter of the PWP method, default 1. Comes from the formula:
      (e^{k*adj(G)} - I)/(e^k - 1), where adj(G) represents the
      adjacency matrix of G and I is the identity matrix.

    Returns
    -------
    influences : dictionary
       Dictionary of PWP indirect influences.
    dependences : dictionary
       Dictionary of PWP indirect dependences.
       
    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> influences,dependences = nx.pwp(G)

    Notes
    -----
    This function uses the SciPy library to make the computations.
    A NetworkX DiGraph is preferred because on an undirected Graph
    indirect dependences are equal to indirect influences. Every
    NetworkX Graph will be converted to a NetworkX DiGraph.

    The name PWP comes from "nearly Poisson Weighted Path" and was
    proposed by Rafael Díaz. We always refer to this method as PWP
    never as its justification.

    See Also
    --------
    micmac, heatkernel

    References
    ----------
    .. [1] R. Diaz,
       Indirect Influences, 
       Advanced Studies in Contemporary Mathematics 23 (2013) 29-41.
       http://arxiv.org/abs/0906.1610
    """
    
    try:
        import scipy as sp
    except ImportError:
        raise ImportError(\
            "pwp() requires SciPy: http://scipy.org/")
            
    try:
        import scipy.linalg as lin
    except ImportError:
        raise ImportError(\
            "pwp() requires scipy.linalg: http://scipy.org")
            
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("pwp() not defined for graphs with multiedges.")

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G
    
    # Get order of Graph
    j = D.order()
    # Get the adjacency matrix of the graph
    A = nx.adjacency_matrix(D)
    # Transpose adjacency matrix
    A = sp.transpose(A)
    
    # Get the k-th power of A
    I = (lin.expm(k * A) - sp.eye(j, j)) / (sp.expm1(k))
    
    # Get the indirect influences vector
    f = sp.sum(I, axis=0)
    f = f/sp.sum(f)
    
    # Get the indirect dependences vector
    d = sp.sum(I, axis=1)
    d = d/sp.sum(d)
  
    # Create dictionary with the result
    influences = dict( zip(D, f) )
    dependences = dict( zip(D, d) )
    return influences,dependences

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
