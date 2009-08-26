"""
Routines to find the boundary of a set of nodes.

Edge boundaries are edges that have only one end
in the set of nodes.  

Node boundaries are nodes outside the set of nodes
that have an edge to a node in the set.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__=['edge_boundary','node_boundary']

def edge_boundary(G, nbunch1, nbunch2=None):
    """Return the edge boundary. 

    Edge boundaries are edges that have only one end
    in the given set of nodes.  

    Parameters
    -----------
    G : graph
      A networkx graph 

    nbunch1 : list, container
       Interior node set 

    nbunch2 : list, container
       Exterior node set.  If None then it is set to all of the
       nodes in G not in nbunch1.

    Returns
    -------
    elist : list
       List of edges

    Notes
    ------
    Nodes in nbunch1 and nbunch2 that are not in G are ignored.

    nbunch1 and nbunch2 are usually meant to be disjoint, 
    but in the interest of speed and generality, that is 
    not required here.

    """
    if nbunch2 is None:     # Then nbunch2 is complement of nbunch1
        nset1=set((n for n in nbunch1 if n in G))
        return [(n1,n2) for n1 in nset1 for n2 in G[n1] \
                if n2 not in nset1]

    nset2=set(nbunch2)
    return [(n1,n2) for n1 in nbunch1 if n1 in G for n2 in G[n1] \
            if n2 in nset2]

def node_boundary(G, nbunch1, nbunch2=None):
    """Return the node boundary. 

    The node boundary is all nodes in the edge boundary of a given
    set of nodes that are in the set.

    Parameters
    -----------
    G : graph
      A networkx graph 

    nbunch1 : list, container
       Interior node set 

    nbunch2 : list, container
       Exterior node set.  If None then it is set to all of the
       nodes in G not in nbunch1.

    Returns
    -------
    nlist : list
       List of nodes.

    Notes
    ------
    Nodes in nbunch1 and nbunch2 that are not in G are ignored.

    nbunch1 and nbunch2 are usually meant to be disjoint, 
    but in the interest of speed and generality, that is 
    not required here.

    """
    nset1=set(n for n in nbunch1 if n in G)
    bdy=set()
    for n1 in nset1:
        bdy.update(G[n1])
    bdy -= nset1
    if nbunch2 is not None: # else nbunch2 is complement of nbunch1
        bdy &= set(nbunch2)
    return list(bdy)

