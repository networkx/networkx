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
from networkx.utils import *
from collections import defaultdict 

__all__ = ['cycle_basis','simple_cycles']

__author__ = "\n".join(['Jon Olav Vik <jonovik@gmail.com>', 
                        'Aric Hagberg <hagberg@lanl.gov>'])

@not_implemented_for('directed')
@not_implemented_for('multigraph')
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
    root : node, optional 
       Specify starting node for basis.

    Returns
    -------
    A list of cycle lists.  Each cycle list is a list of nodes
    which forms a cycle (loop) in G.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_cycle([0,1,2,3])
    >>> G.add_cycle([0,3,4,5])
    >>> print(nx.cycle_basis(G,0))
    [[3, 4, 5, 0], [1, 2, 3, 0]]

    Notes
    -----
    This is adapted from algorithm CACM 491 [1]_. 

    References
    ----------
    .. [1] Paton, K. An algorithm for finding a fundamental set of 
       cycles of a graph. Comm. ACM 12, 9 (Sept 1969), 514-518.

    See Also
    --------
    simple_cycles
    """
    # if G.is_directed():
    #     e='cycle_basis() not implemented for directed graphs'
    #     raise Exception(e)
    # if G.is_multigraph():
    #     e='cycle_basis() not implemented for multigraphs'
    #     raise Exception(e)

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


@not_implemented_for('undirected')
def simple_cycles(G):
    """Find simple cycles (elementary circuits) of a directed graph.
    
    An simple cycle, or elementary circuit, is a closed path where no 
    node appears twice, except that the first and last node are the same. 
    Two elementary circuits are distinct if they are not cyclic permutations 
    of each other.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    A list of circuits, where each circuit is a list of nodes, with the first 
    and last node being the same.
    
    Example:
    >>> G = nx.DiGraph([(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)])
    >>> nx.simple_cycles(G)
    [[0, 0], [0, 1, 2, 0], [0, 2, 0], [1, 2, 1], [2, 2]]
    
    See Also
    --------
    cycle_basis (for undirected graphs)
    
    Notes
    -----
    The implementation follows pp. 79-80 in [1]_.

    The time complexity is O((n+e)(c+1)) for n nodes, e edges and c
    elementary circuits.

    References
    ----------
    .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975. 
       http://dx.doi.org/10.1137/0204007

    See Also
    --------
    cycle_basis
    """
    # Jon Olav Vik, 2010-08-09
    def _unblock(thisnode):
        """Recursively unblock and remove nodes from B[thisnode]."""
        if blocked[thisnode]:
            blocked[thisnode] = False
            while B[thisnode]:
                _unblock(B[thisnode].pop())
    
    def circuit(thisnode, startnode, component):
        closed = False # set to True if elementary path is closed
        path.append(thisnode)
        blocked[thisnode] = True
        for nextnode in component[thisnode]: # direct successors of thisnode
            if nextnode == startnode:
                result.append(path + [startnode])
                closed = True
            elif not blocked[nextnode]:
                if circuit(nextnode, startnode, component):
                    closed = True
        if closed:
            _unblock(thisnode)
        else:
            for nextnode in component[thisnode]:
                if thisnode not in B[nextnode]: # TODO: use set for speedup?
                    B[nextnode].append(thisnode)
        path.pop() # remove thisnode from path
        return closed
    
#    if not G.is_directed():
#        raise nx.NetworkXError(\
#            "simple_cycles() not implemented for undirected graphs.")
    path = [] # stack of nodes in current path
    blocked = defaultdict(bool) # vertex: blocked from search?
    B = defaultdict(list) # graph portions that yield no elementary circuit
    result = [] # list to accumulate the circuits found
    # Johnson's algorithm requires some ordering of the nodes.
    # They might not be sortable so we assign an arbitrary ordering.
    ordering=dict(zip(G,range(len(G))))
    for s in ordering:
        # Build the subgraph induced by s and following nodes in the ordering
        subgraph = G.subgraph(node for node in G 
                              if ordering[node] >= ordering[s])
        # Find the strongly connected component in the subgraph 
        # that contains the least node according to the ordering
        strongcomp = nx.strongly_connected_components(subgraph)
        mincomp=min(strongcomp, 
                    key=lambda nodes: min(ordering[n] for n in nodes))
        component = G.subgraph(mincomp)
        if component:
            # smallest node in the component according to the ordering
            startnode = min(component,key=ordering.__getitem__) 
            for node in component:
                blocked[node] = False
                B[node][:] = []
            dummy=circuit(startnode, startnode, component)

    return result
