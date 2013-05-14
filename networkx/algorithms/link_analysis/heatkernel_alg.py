"""Heat Kernel analysis method of graph structure. """
#    Copyright (C) 2013 by
#    Jorge Catumba <jorgerev90@gmail.com>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/
import networkx as nx
from networkx.exception import NetworkXError
__author__ = """Jorge Catumba (jorgerev90@gmail.com)"""
__all__ = ['heatkernel']

def heatkernel(G, k=1):
    """Return the Heat Kernel indirect influences and indirect
     dependences of the nodes in the graph.

    Heat Kernel computes the indirect influences and dependencias
    via the exponential formula described in references.

    Parameters
    -----------
    G : graph
      A NetworkX [Di]Graph

    k : integer, optional
      Paramenter of the Heat Kernel method, default 1

    Returns
    -------
    indirect: dictionary
        Dictionary of Heat Kernel indirect dependencies and influences

    Examples
    --------
    >>> G=nx.DiGraph(nx.path_graph(4))
    >>> pr=nx.heatkernel(G)

    Notes
    -----
    This function uses the SciPy library to make the computations. A NetworkX DiGraph is prefered because on a regular Graph indirect dependences are equal to indirect dependeces.

    See Also
    --------
    micmac, pwp

    References
    ----------
    .. [1] F. Chung, 
    The heat kernel as the pagerank of a graph, Proc. Natl. Acad.
    Sci. 104 (50) 19735-19740.
    .. [2] R. Diaz,
       Indirect Influences, Advanced Studies in Contemporary Mathematics 23 (2013) 29 -41.
    """
    
    try:
        import scipy as sp
    except ImportError:
        raise ImportError(\
            "heatkernel() requires SciPy: http://scipy.org/")
            
    try:
        import scipy.linalg as lin
    except ImportError:
        raise ImportError(\
            "heatkernel() requires scipy.linalg: http://scipy.org")
            
    try:
        import scipy.linalg.matfuncs as matf
    except ImportError:
        raise ImportError(\
            "heatkernel() requires scipy.linalg.matfuncs: http://scipy.org")
            
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("heatkernel() not defined for graphs with multiedges.")

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G
    
    # Get the order of the Graph
    j = D.order()
    # Get the adjacency matrix of the graph
    A = nx.adjacency_matrix(D)
    # Transpose adjacency matrix
    A = sp.transpose(A)
    
    # Get the indirect influences matrix according to Heat Kernel
    I = matf.expm(k * (A - sp.eye(j, j)))
    
    # Get the indirect influences vector
    f = sp.sum(I, axis=0)
    f = f/sp.sum(f)
    
    # Get the indirect dependences vector
    d = sp.sum(I, axis=1)
    d = d/sp.sum(d)
    
    #create the dictionary with the result
    fdict = {i: number for number, i in zip(f, range(j))}
    ddict = {i: number for number, i in zip(d, range(j))}
    indirect = {'influences': fdict, 'dependences': ddict}
    return indirect

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
