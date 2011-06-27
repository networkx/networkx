"""
Graph isomorphism functions.

"""
__author__ = """Pieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx
from networkx.exception import NetworkXError

__all__ = ['could_be_isomorphic',
           'fast_could_be_isomorphic',
           'faster_could_be_isomorphic',
           'is_isomorphic']

def could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.
       
    Notes
    -----
    Checks for matching degree, triangle, and number of cliques sequences.
    """
  
    # Check global properties
    if G1.order() != G2.order(): return False
    
    # Check local properties
    d1=G1.degree()
    t1=nx.triangles(G1)
    c1=nx.number_of_cliques(G1)
    props1=[ [d1[v], t1[v], c1[v]] for v in d1 ]
    props1.sort()
    
    d2=G2.degree()
    t2=nx.triangles(G2)
    c2=nx.number_of_cliques(G2)
    props2=[ [d2[v], t2[v], c2[v]] for v in d2 ]
    props2.sort()

    if props1 != props2: 
        return False

    # OK...
    return True

graph_could_be_isomorphic=could_be_isomorphic

def fast_could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.
       
    Notes
    -----
    Checks for matching degree and triangle sequences.
    """
  
    # Check global properties
    if G1.order() != G2.order(): return False
    
    # Check local properties
    d1=G1.degree()
    t1=nx.triangles(G1)
    props1=[ [d1[v], t1[v]] for v in d1 ]
    props1.sort()
    
    d2=G2.degree()
    t2=nx.triangles(G2)
    props2=[ [d2[v], t2[v]] for v in d2 ]
    props2.sort()

    if props1 != props2: return False

    # OK...
    return True

fast_graph_could_be_isomorphic=fast_could_be_isomorphic

def faster_could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.
       
    Notes
    -----
    Checks for matching degree sequences.
    """
  
    # Check global properties
    if G1.order() != G2.order(): return False
    
    # Check local properties
    d1=list(G1.degree().values())
    d1.sort()
    d2=list(G2.degree().values())
    d2.sort()

    if d1 != d2: return False

    # OK...
    return True

faster_graph_could_be_isomorphic=faster_could_be_isomorphic

def is_isomorphic(G1, G2, node_match=None, weight=None, default=1, 
                          rtol=1.0000000000000001e-05, atol=1e-08):
    """Returns True if the graphs G1 and G2 are isomorphic and False otherwise.

    Parameters
    ----------
    G1, G2: NetworkX graph instances
        The two graphs G1 and G2 must be the same type.
       
    node_match : callable
        A function that returns True iff node `n1` in `G1` and `n2` in `G2`
        should be considered equal during the isomorphism test. The 
        function will be called like:
        
           node_match(G1.node[n1], G2.node[n2])
           
        That is, the function will receive the node attribute dictionaries
        of the nodes under consideration. If `None`, then no attributes are
        considered when testing for an isomorphism.
           
    weight : string or None, optional (default=None)
        The edge attribute that holds the numerical value used as a weight.
        If None, then don't check for weighted graphs.
        Otherwise, G1 and G2 must be valid weighted graphs.

    default : float, optional
        The default weight to use when an edge has no weight.

    rtol: float, optional
        The relative error tolerance when checking weighted edges

    atol: float, optional
        The absolute error tolerance when checking weighted edges
    
    Notes
    -----
    Uses the vf2 algorithm.
    Works for Graph, DiGraph, MultiGraph, and MultiDiGraph

    See Also
    --------
    :mod:`isomorphvf2`

    """
    if weight is None and node_match is None:
        if G1.is_directed() and G2.is_directed():
            gm = nx.DiGraphMatcher(G1,G2)
        elif (not G1.is_directed()) and (not G2.is_directed()):
            gm = nx.GraphMatcher(G1,G2)            
        else:
           raise NetworkXError("Graphs G1 and G2 are not of the same type.")        
    else:
        if not G1.is_directed() and not G1.is_multigraph():
            assert(not G2.is_directed() and not G2.is_multigraph())
            GM = nx.WeightedGraphMatcher
        elif not G1.is_directed() and G1.is_multigraph():
            assert(not G2.is_directed() and G2.is_multigraph())
            GM = nx.WeightedMultiGraphMatcher
        elif G1.is_directed() and not G1.is_multigraph():
            assert(G2.is_directed() and not G2.is_multigraph())
            GM = nx.WeightedDiGraphMatcher
        else:
            assert(G2.is_directed() and G2.is_multigraph())
            GM = nx.WeightedMultiDiGraphMatcher
            
        gm = GM(G1, G2, node_match=node_match, weight=weight, default=default, 
                        rtol=rtol, atol=atol)
    print gm
    return gm.is_isomorphic()

