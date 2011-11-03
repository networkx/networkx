# -*- coding: utf-8 -*-
"""Generate graphs with given degree and triangle sequence.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import random
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Joel Miller (joel.c.miller.research@gmail.com)'])

__all__ = ['random_clustered_graph']


def random_clustered_graph(joint_degree_sequence, create_using=None, seed=None):
    """Generate a random graph with the given joint degree and triangle
    degree sequence.
	
    This uses a configuration model-like approach to generate a
    random pseudograph (graph with parallel edges and self loops) by
    randomly assigning edges to match the given indepdenent edge 
    and triangle degree sequence.

    Parameters 
    ---------- 
    joint_degree_sequence : list of integer pairs
        Each list entry corresponds to the independent edge degree and
        triangle degree of a node.
    create_using : graph, optional (default MultiGraph)
        Return graph of this type. The instance will be cleared.
    seed : hashable object, optional
        The seed for the random number generator.

    Returns
    -------
    G : MultiGraph
        A graph with the specified degree sequence. Nodes are labeled
        starting at 0 with an index corresponding to the position in
        deg_sequence.
	
    Raises
    ------
    NetworkXError
        If the independent edge degree sequence sum is not even
        or the triangle degree sequence sum is not divisible by 3.

    Notes
    -----
    As described by Miller [1]_ (see also Newman [2]_ for an equivalent
    description).
	
    A non-graphical degree sequence (not realizable by some simple
    graph) is allowed since this function returns graphs with self
    loops and parallel edges.  An exception is raised if the
    independent degree sequence does not have an even sum or the
    triangle degree sequence sum is not divisible by 3.
	
    This configuration model-like construction process can lead to
    duplicate edges and loops.  You can remove the self-loops and
    parallel edges (see below) which will likely result in a graph
    that doesn't have the exact degree sequence specified.  This
    "finite-size effect" decreases as the size of the graph increases.

    References
    ----------
    .. [1] J. C. Miller "Percolation and Epidemics on Random Clustered Graphs."
        Physical Review E, Rapid Communication (to appear).
    .. [2] M.E.J. Newman, "Random clustered networks".
        Physical Review Letters (to appear).
	       
    Examples
    --------
    >>> deg_tri=[[1,0],[1,0],[1,0],[2,0],[1,0],[2,1],[0,1],[0,1]]
    >>> G = nx.random_clustered_graph(deg_tri)

    To remove parallel edges:

    >>> G=nx.Graph(G)
	
    To remove self loops:

    >>> G.remove_edges_from(G.selfloop_edges())

    """
    if create_using is None:
        create_using = nx.MultiGraph()
    elif create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    if not seed is None:
        random.seed(seed)

    # In Python 3, zip() returns an iterator. Make this into a list.
    joint_degree_sequence = list(joint_degree_sequence)

    N = len(joint_degree_sequence)
    G = nx.empty_graph(N,create_using)

    ilist = []
    tlist = []
    for n in G:
        degrees = joint_degree_sequence[n]
        for icount in range(degrees[0]):
            ilist.append(n)
        for tcount in range(degrees[1]):
            tlist.append(n)

    if len(ilist)%2 != 0 or len(tlist)%3 != 0:
        raise nx.NetworkXError('Invalid degree sequence')

    random.shuffle(ilist)
    random.shuffle(tlist)
    while ilist:
        G.add_edge(ilist.pop(),ilist.pop())
    while tlist:
        n1 = tlist.pop()
        n2 = tlist.pop()
        n3 = tlist.pop()
        G.add_edges_from([(n1,n2),(n1,n3),(n2,n3)])
    G.name = "random_clustered %d nodes %d edges"%(G.order(),G.size())
    return G

