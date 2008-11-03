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
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__=['edge_boundary','node_boundary']

def edge_boundary(G, nbunch1, nbunch2=None):
    """Return list of edges from G: (n1,n2) with n1 in nbunch1 and n2 in
    nbunch2.  If nbunch2 is omitted or nbunch2=None, then nbunch2
    is all nodes not in nbunch1.

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
    """Return list of all nodes on external boundary of nbunch1 that are
    in nbunch2.  If nbunch2 is omitted or nbunch2=None, then nbunch2
    is all nodes not in nbunch1.

    Note that by definition the node_boundary is external to nbunch1.
    
    Nodes in nbunch1 and nbunch2 that are not in the graph are ignored.

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

