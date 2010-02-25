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
import networkx

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
    [[0, 3, 4, 5], [0, 1, 2, 3]]

    Notes
    -----
    This algorithm is adapted from algorithm CACM 491 published:
    Paton, K. An algorithm for finding a fundamental set of 
    cycles of a graph. Comm. ACM 12, 9 (Sept 1969), 514-518.

    """
    if root is None:
        root=G.nodes_iter().next()
    ST=networkx.Graph({root:G[root]}) # spanning tree
    cycles=[]
    stack=list(ST)
    pred=dict.fromkeys(stack,[]) # all nodes have pred that is root
    
    while stack:
        z=stack.pop()
        for nbr in G[z]:
            if nbr in ST: 
                if nbr not in ST[z]:
                    cycle=pred[z]
                    cycle.reverse()
                    cycle=[root]+pred[nbr]+[nbr,z]+cycle
                    cycles.append(cycle)
                    ST.add_edge(z,nbr)
            else:
                ST.add_edge(z,nbr)
                pred[nbr]=pred[z]+[z]
                stack.append(nbr)
    return cycles

