# -*- coding: utf-8 -*-
"""
Eulerian circuits and graphs.
"""
import networkx as nx

__author__ = """\n""".join(['Nima Mohammadi (nima.irt[AT]gmail.com)',
                            'Aric Hagberg <hagberg@lanl.gov>'])
#    Copyright (C) 2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['is_eulerian', 'eulerian_circuit']

def is_eulerian(G):
    """Return True if G is an Eulerian graph, False otherwise.

    An Eulerian graph is a graph with an Eulerian circuit.

    Parameters
    ----------
    G : graph
       A NetworkX Graph

    Examples
    --------
    >>> nx.is_eulerian(nx.DiGraph({0:[3], 1:[2], 2:[3], 3:[0, 1]}))
    True
    >>> nx.is_eulerian(nx.complete_graph(5))
    True
    >>> nx.is_eulerian(nx.petersen_graph())
    False

    Notes
    -----
    This implementation requires the graph to be connected
    (or strongly connected for directed graphs).
    """
    if G.is_directed():
        # Every node must have equal in degree and out degree
        for n in G.nodes_iter():
            if G.in_degree(n) != G.out_degree(n):
               return False
        # Must be strongly connected
        if not nx.is_strongly_connected(G):
            return False
    else:
        # An undirected Eulerian graph has no vertices of odd degrees
        for v,d in G.degree_iter():
            if d % 2 != 0:
                return False
        # Must be connected
        if not nx.is_connected(G):
            return False
    return True


def eulerian_circuit(G, source=None):
    """Return the edges of an Eulerian circuit in G.

    An Eulerian circuit is a path that crosses every edge in G exactly once
    and finishes at the starting node.

    Parameters
    ----------
    G : NetworkX Graph or DiGraph
        A directed or undirected graph
    source : node, optional
       Starting node for circuit.

    Returns
    -------
    edges : generator
       A generator that produces edges in the Eulerian circuit.

    Raises
    ------
    NetworkXError
       If the graph is not Eulerian.

    See Also
    --------
    is_eulerian

    Notes
    -----
    Linear time algorithm, adapted from [1]_.
    General information about Euler tours [2]_.

    References
    ----------
    .. [1] J. Edmonds, E. L. Johnson.
       Matching, Euler tours and the Chinese postman.
       Mathematical programming, Volume 5, Issue 1 (1973), 111-114.
    .. [2] http://en.wikipedia.org/wiki/Eulerian_path

    Examples
    --------
    >>> G=nx.complete_graph(3)
    >>> list(nx.eulerian_circuit(G))
    [(0, 2), (2, 1), (1, 0)]
    >>> list(nx.eulerian_circuit(G,source=1))
    [(1, 2), (2, 0), (0, 1)]
    >>> [u for u,v in nx.eulerian_circuit(G)]  # nodes in circuit
    [0, 2, 1]
    """
    from operator import itemgetter
    if not is_eulerian(G):
        raise nx.NetworkXError("G is not Eulerian.")
    g = G.__class__(G) # copy graph structure (not attributes)

    # set starting node
    if source is None:
        v = next(g.nodes_iter())
    else:
        v = source

    if g.is_directed():
        degree = g.in_degree
        edges = g.in_edges_iter
        get_vertex = itemgetter(0)
    else:
        degree = g.degree
        edges = g.edges_iter
        get_vertex = itemgetter(1)

    vertex_stack = [v]
    last_vertex = None
    while vertex_stack:
        current_vertex = vertex_stack[-1]
        if degree(current_vertex) == 0:
            if last_vertex is not None:
                yield (last_vertex, current_vertex)
            last_vertex = current_vertex
            vertex_stack.pop()
        else:
            random_edge = next(edges(current_vertex))
            vertex_stack.append(get_vertex(random_edge))
            g.remove_edge(*random_edge)
