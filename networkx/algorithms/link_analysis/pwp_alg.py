"""PWP analysis method of graph structure. """
#    Copyright (C) 2013 by
#    Jorge Catumba <jorgerev90@gmail.com>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/
import networkx as nx
from networkx.exception import NetworkXError
__author__ = """Jorge Catumba (jorgerev90@gmail.com)"""
__all__ = ['pwp']

def pwp(G, k=1):
    """Return the PWP indirect influences and indirect dependences
    of the nodes in the graph.

    PWP computes the indirect influences and dependences via the
    exponential formula described in references.

    Parameters
    -----------
    G : graph
      A NetworkX [Di]Graph

    k : integer, optional
      Paramenter of the PWP method, default 1

    Returns
    -------
    indirect : dictionary
       Dictionary of PWP indirect dependences and influences.
       
    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.pwp(G)

    Notes
    -----
    This function uses the SciPy library to make the computations. A NetworkX DiGraph is prefered because on a regular Graph indirect dependences are equal to indirect dependeces.

    See Also
    --------
    micmac, heatkernel

    References
    ----------
    .. [1] R. Diaz,
       Indirect Influences, Advanced Studies in Contemporary Mathematics 23 (2013) 29-41.
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
            
    try:
        import scipy.linalg.matfuncs as matf
    except ImportError:
        raise ImportError(\
            "pwp() requires scipy.linalg.matfuncs: http://scipy.org")
            
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
    I = (matf.expm(k * A) - sp.eye(j, j)) / (sp.expm1(k))
    
    # Get the indirect influences vector
    f = sp.sum(I, axis=0)
    f = f/sp.sum(f)
    
    # Get the indirect dependences vector
    d = sp.sum(I, axis=1)
    d = d/sp.sum(d)
  
    # Create dictionary with the result
    fdict = {i: number for number, i in zip(f, nx.nodes_iter(D))}
    ddict = {i: number for number, i in zip(d, nx.nodes_iter(D))}
    indirect = {'influences': fdict, 'dependences': ddict}
    return indirect

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
