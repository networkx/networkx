"""
Fast checking to see if graphs are not isomorphic.

This isn't a graph isomorphism checker.
"""
__author__ = """Pieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx
from networkx.exception import NetworkXException, NetworkXError

def graph_could_be_isomorphic(G1,G2):
    """
    Returns False if graphs G1 and G2 are definitely not isomorphic.
    True does NOT garantee isomorphism.
  
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

def fast_graph_could_be_isomorphic(G1,G2):
    """
    Returns False if graphs G1 and G2 are definitely not isomorphic.
    True does NOT garantee isomorphism.
  
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

def faster_graph_could_be_isomorphic(G1,G2):
    """
    Returns False if graphs G1 and G2 are definitely not isomorphic.
    True does NOT garantee isomorphism.
  
    Checks for matching degree sequences in G1 and G2.
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

def is_isomorphic(G1,G2):
    """Returns True if the graphs G1 and G2 are isomorphic and False otherwise.

    Uses the vf2 algorithm - see networkx.isomorphvf2
        
    """
    if G1.directed and G2.directed:
        return networkx.DiGraphMatcher(G1,G2).is_isomorphic()
    elif not (G1.directed and G2.directed):
        return networkx.GraphMatcher(G1,G2).is_isomorphic()
    else:
            # Graphs are of mixed type. We could just return False, 
            # but then there is the case of completely disconnected graphs...
            # which could be isomorphic.
        raise NetworkXError, "Both graphs were not directed or both graphs were not undirected."
    

