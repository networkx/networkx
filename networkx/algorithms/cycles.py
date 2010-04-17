"""
========================
Cycle finding algorithms
========================
"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx

__all__ = ['cycle_basis']

def cycle_basis(G,root=None):
    """ Returns a list of cycles which form a basis for cycles of G.

    A basis for cycles of a network is a minimal collection of 
    cycles such that any cycle in the network can be written 
    as a sum of cycles in the basis.  Here summation of cycles 
    is defined as "exclusive or" of the edges. Cycle bases are 
    useful, e.g. when deriving equations for electric circuits 
    using Kirchhoff's Laws.

    Parameters
    ----------
    G : NetworkX Graph
    root : node of G, optional (default=arbitrary choice from G)

    Returns
    -------
    A list of cycle lists.  Each cycle list is a list of nodes
    which forms a cycle (loop) in G.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_cycle([0,1,2,3])
    >>> G.add_cycle([0,3,4,5])
    >>> print nx.cycle_basis(G,0)
    [[3, 4, 5, 0], [1, 2, 3, 0]]

    Notes
    -----
    This algorithm is adapted from algorithm CACM 491 published:
    Paton, K. An algorithm for finding a fundamental set of 
    cycles of a graph. Comm. ACM 12, 9 (Sept 1969), 514-518.

    """
    if G.is_multigraph() or G.is_directed():
        raise Exception("cycle_basis() not implemented for directed or multiedge graphs.")

    gnodes=set(G.nodes())
    cycles=[]
    while gnodes:  # loop over connected components
        if root is None:
            root=gnodes.pop()
        stack=[root]
        pred={root:root} 
        used={root:set()}
        while stack:  # walk the spanning tree finding cycles
            z=stack.pop()  # use last-in so cycles easier to find
            zused=used[z]
            for nbr in G[z]:
                if nbr not in used:   # new node 
                    pred[nbr]=z
                    stack.append(nbr)
                    used[nbr]=set([z])
                elif nbr is z:        # self loops
                    cycles.append([z]) 
                elif nbr not in zused:# found a cycle
                    pn=used[nbr]
                    cycle=[nbr,z]
                    p=pred[z]
                    while p not in pn:
                        cycle.append(p)
                        p=pred[p]
                    cycle.append(p)
                    cycles.append(cycle)
                    used[nbr].add(z)
        gnodes-=set(pred)
        root=None
    return cycles

