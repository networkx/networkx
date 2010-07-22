# -*- coding: utf-8 -*-
"""
Eulerian circuits and graphs.
"""
__author__ = """\n""".join(['Nima Mohammadi (nima.irt[AT]gmail.com)',
                            'Aric Hagberg <hagberg@lanl.gov>'])
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__ = ['is_eulerian', 'eulerian_circuit']

import networkx as nx

def is_eulerian(G):
    """Return True if G is an Eulerian graph, False otherwise.

    An Eulerian graph is a graph with an Eulerian circuit.

    Parameters
    ----------
    G : NetworkX graph

    Examples
    --------
    >>> is_eulerian(nx.DiGraph({0:[3], 1:[2], 2:[3], 3:[0, 1]}))
    True
    >>> is_eulerian(nx.complete_graph(5))
    True
    >>> is_eulerian(nx.petersen_graph())
    False

    Notes
    -----
    This implementation requires the graph to be connected
    (or strongly connected for directed graphs).
    """
    if G.is_directed():
        # Every node of must have equal in degree and out degree
        for n in G.nodes_iter():
            if G.in_degree(n) != G.out_degree(n):
               return False
        # Must be a strongly connected graph
        if not nx.is_strongly_connected(G):
            return False
    else:
        # An undirected Eulerian graph has no vertices of odd degrees
        for v,d in G.degree_iter():
            if d % 2 != 0:
                return False
        # Must be a connected graph
        if not nx.is_connected(G):
            return False
    return True
	  

def eulerian_circuit(G, source=None):
    """Return the edges of an Eulerian circuit in G.

    An Eulerian circuit is a path that crosses every edge in G exactly once
    and finishes at the starting node.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Starting node for circuit.

    Returns
    -------
    edges : generator
       A generator that produces edges in the Eulerian circuit.

    Examples
    --------
    >>> G=nx.complete_graph(3)
    >>> list( eulerian_circuit(G) )
    [(0, 1), (1, 2), (2, 0)]
    >>> list( eulerian_circuit(G,source=1) ) 
    [(1, 0), (0, 2), (2, 1)]
    >>> [u for u,v in eulerian_circuit(G)]  # nodes in circuit
    [0, 1, 2]

    Notes
    -----
    Uses Fleury's algorithm [1]_,[2]_  

    References
    ----------
    .. [1] Fleury, "Deux problemes de geometrie de situation", 
       Journal de mathematiques elementaires (1883), 257-261.
    .. [2] http://en.wikipedia.org/wiki/Eulerian_path
    """
    if not is_eulerian(G):
        raise nx.NetworkXError("G is not Eulerian.")

    g = G.__class__(G) # copy graph structure (not attributes)

    # set starting node
    if source is None:
        v = g.nodes_iter().next()
    else:
        v = source

    while g.size()>0:
        n = v   
        nbrs = sorted([v for u,v in g.edges(n)])
        # sort nbrs here to provide stable ordering of alternate cycles
        for v in nbrs:
            g.remove_edge(n, v)
            bridge = not nx.is_connected(g.to_undirected())
            if bridge:
                g.add_edge(n, v)  # add this edge back and try another
            else:
                break  # this edge is good, break the for loop 
        if bridge:
            g.remove_edge(n, v)            
            g.remove_node(n)
        yield (n,v)


