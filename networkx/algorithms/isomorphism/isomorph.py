"""
Fast checking to see if graphs are not isomorphic.

This isn't a graph isomorphism checker.
"""
__author__ = """Pieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx
from networkx.exception import NetworkXException, NetworkXError

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
    d1=G1.degree(with_labels=True)
    t1=networkx.triangles(G1,with_labels=True)
    c1=networkx.number_of_cliques(G1,with_labels=True)
    props1=[ [d1[v], t1[v], c1[v]] for v in d1 ]
    props1.sort()
    
    d2=G2.degree(with_labels=True)
    t2=networkx.triangles(G2,with_labels=True)
    c2=networkx.number_of_cliques(G2,with_labels=True)
    props2=[ [d2[v], t2[v], c2[v]] for v in d2 ]
    props2.sort()

    if props1 != props2: 
#        print props1
#        print props2
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
    d1=G1.degree(with_labels=True)
    t1=networkx.triangles(G1,with_labels=True)
    props1=[ [d1[v], t1[v]] for v in d1 ]
    props1.sort()
    
    d2=G2.degree(with_labels=True)
    t2=networkx.triangles(G2,with_labels=True)
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
    d1=G1.degree()
    d1.sort()
    d2=G2.degree()
    d2.sort()

    if d1 != d2: return False

    # OK...
    return True

faster_graph_could_be_isomorphic=faster_could_be_isomorphic

def is_isomorphic(G1,G2,weighted=False,rtol=1e-6,atol=1e-9):
    """Returns True if the graphs G1 and G2 are isomorphic and False otherwise.

    Parameters
    ----------
    G1, G2: NetworkX graph instances
       The two graphs G1 and G2 must be the same type.
       
    weighted: bool, optional
       Optionally check isomorphism for weighted graphs.
       G1 and G2 must be valid weighted graphs.

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
    isomorphvf2()

    """
    gm=None
    if weighted==True:
#        assert(G1.weighted and G2.weighted)
        if not G1.is_directed() and not G1.is_multigraph():
            assert(not G2.is_directed() and not G2.is_multigraph())
            gm = networkx.WeightedGraphMatcher(G1,G2,rtol,atol)
        elif not G1.is_directed() and G1.is_multigraph():
            assert(not G2.is_directed() and G2.is_multigraph())
            gm = networkx.WeightedMultiGraphMatcher(G1,G2,rtol,atol)
        elif G1.is_directed() and not G1.is_multigraph():
            assert(G2.is_directed() and not G2.is_multigraph())
            gm = networkx.WeightedDiGraphMatcher(G1,G2,rtol,atol)
        else:
            assert(G2.is_directed() and G2.is_multigraph())
            gm = networkx.WeightedMultiDiGraphMatcher(G1,G2,rtol,atol)
    else:
        if G1.is_directed() and G2.is_directed():
            gm=  networkx.DiGraphMatcher(G1,G2)
        elif not (G1.is_directed() and G2.is_directed()):
            gm = networkx.GraphMatcher(G1,G2)
    if gm==None:
        # Graphs are of mixed type. We could just return False, 
        # but then there is the case of completely disconnected graphs...
        # which could be isomorphic.
        raise NetworkXError("Graphs G1 and G2 are not of the same type.")
    
    return gm.is_isomorphic()  

