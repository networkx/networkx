# -*- coding: utf-8 -*-
#
#    Copyright (C) 2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
#    eulerian_path()
#    Copyright 2015 by
#    Edwardo Rivera-Hazim <edwardo.rivera@upr.edu>
#    Humberto Ortiz-Zuazaga <humberto.ortiz@upr.edu>
#    BSD license.
"""
Eulerian circuits and graphs.
"""
from operator import itemgetter

import networkx as nx

from ..utils import arbitrary_element

from collections import deque

__author__ = """\n""".join(['Nima Mohammadi (nima.irt[AT]gmail.com)',
                            'Aric Hagberg <hagberg@lanl.gov>',
                            'Edwardo Rivera-Hazim <edwardo.rivera@upr.edu>',
                            'Humberto Ortiz-Zuazaga <humberto.ortiz@upr.edu>'])

__all__ = ['is_eulerian', 'eulerian_circuit',
           'has_eulerian_path', 'eulerian_path']


def is_eulerian(G):
    """Returns ``True`` if and only if ``G`` is Eulerian.

    An graph is *Eulerian* if it has an Eulerian circuit. An *Eulerian
    circuit* is a closed walk that includes each edge of a graph exactly
    once.

    Parameters
    ----------
    G : NetworkX graph
       A graph, either directed or undirected.

    Examples
    --------
    >>> nx.is_eulerian(nx.DiGraph({0: [3], 1: [2], 2: [3], 3: [0, 1]}))
    True
    >>> nx.is_eulerian(nx.complete_graph(5))
    True
    >>> nx.is_eulerian(nx.petersen_graph())
    False

    Notes
    -----
    If the graph is not connected (or not strongly connected, for
    directed graphs), this function returns ``False``.

    """
    if G.is_directed():
        # Every node must have equal in degree and out degree and the
        # graph must be strongly connected
        return (all(G.in_degree(n) == G.out_degree(n) for n in G) and
                nx.is_strongly_connected(G))
    # An undirected Eulerian graph has no vertices of odd degree and
    # must be connected.
    return all(d % 2 == 0 for v, d in G.degree()) and nx.is_connected(G)


def eulerian_circuit(G, source=None):
    """Returns an iterator over the edges of an Eulerian circuit in ``G``.

    An *Eulerian circuit* is a closed walk that includes each edge of a
    graph exactly once.

    Parameters
    ----------
    G : NetworkX graph
       A graph, either directed or undirected.

    source : node, optional
       Starting node for circuit.

    Returns
    -------
    edges : iterator
       An iterator over edges in the Eulerian circuit.

    Raises
    ------
    NetworkXError
       If the graph is not Eulerian.

    See Also
    --------
    is_eulerian

    Notes
    -----
    This is a linear time implementation of an algorithm adapted from [1]_.

    For general information about Euler tours, see [2]_.

    References
    ----------
    .. [1] J. Edmonds, E. L. Johnson.
       Matching, Euler tours and the Chinese postman.
       Mathematical programming, Volume 5, Issue 1 (1973), 111-114.
    .. [2] http://en.wikipedia.org/wiki/Eulerian_path

    Examples
    --------
    To get an Eulerian circuit in an undirected graph::

        >>> G = nx.complete_graph(3)
        >>> list(nx.eulerian_circuit(G))
        [(0, 2), (2, 1), (1, 0)]
        >>> list(nx.eulerian_circuit(G, source=1))
        [(1, 2), (2, 0), (0, 1)]

    To get the sequence of vertices in an Eulerian circuit::

        >>> [u for u, v in nx.eulerian_circuit(G)]
        [0, 2, 1]

    """
    if not is_eulerian(G):
        raise nx.NetworkXError("G is not Eulerian.")
    g = G.__class__(G)  # copy graph structure (not attributes)

    # set starting node
    if source is None:
        v = arbitrary_element(g)
    else:
        v = source

    if g.is_directed():
        degree = g.in_degree
        edges = g.in_edges
        get_vertex = itemgetter(0)
    else:
        degree = g.degree
        edges = g.edges
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
            arbitrary_edge = next(edges(current_vertex))
            vertex_stack.append(get_vertex(arbitrary_edge))
            g.remove_edge(*arbitrary_edge)


def has_eulerian_path(G):
    """Returns ``True'' iff ``G'' has an Eulerian path.

    An Eulerian path is a path that crosses every edge in G
    exactly once.

    Parameters
    ----------
    G: NetworkX Graph, DiGraph, MultiGraph or MultiDiGraph
        A directed or undirected Graph or MultiGraph.

    Returns
    -------
    True, False

    Examples
    --------
    >>> G = nx.DiGraph([(1,2),(2,3)])                                      
    >>> nx.has_eulerian_path(G)
    True
    """
    is_directed = G.is_directed()

    # Verify that graph is connected, short circuit
    if is_directed and not nx.is_weakly_connected(G):
        return False

    # is undirected
    if not is_directed and not nx.is_connected(G):
        return False

    # Now verify if has an Eulerian circuit: even condition of all
    # nodes is satisfied.
    if nx.is_eulerian(G):
        return True

    # Not all vertex have even degree, check if exactly two vertex
    # have odd degrees.  If yes, then there is an Euler path. If not,
    # raise an error (no Euler path can be found)

    # if the odd condition is not meet, raise an error.
    start = _find_path_start(G)
    if not start:
        return False

    return True


def _find_path_start(G):
    """Returns a suitable starting vertex for Eulerian path

    The function also verifies that the graph contains a path. If no
    path exists, returns ``None''.

    """
    is_directed = G.is_directed()

    # list to check the odd degree condition
    check_odd = []

    if is_directed:
        degree = G.in_degree
        out_degree = G.out_degree
    else:
        degree = G.degree

    # Verify if an Euler path can be found. Complexity O(n) ?
    for v in G:
        deg = degree(v)
        # directed case
        if is_directed:
            outdeg = out_degree(v)
            if deg != outdeg:
                # if we have more than 2 odd nodes no Euler path exists
                if len(check_odd) > 2:
                    return False
                # is odd and we append it.
                check_odd.append(v)
        # undirected case
        else:
            if deg % 2 != 0:
                # if we have more than 2 odd nodes no Euler path exists
                if len(check_odd) > 2:
                    return False
                # is odd and we append it.
                check_odd.append(v)

    if is_directed:

        first = check_odd[0]
        second = check_odd[1]
        if G.out_degree(first) == G.in_degree(first) + 1 and \
           G.in_degree(second) == G.out_degree(second) + 1:
            start = second
        elif G.out_degree(second) == G.in_degree(second) + 1 and \
             G.in_degree(first) == G.out_degree(first) + 1:
            start = first
        else:
            start = None

    else:
        start = check_odd[0]

    return start


def _find_eulerian_path(G):
    """Returns a generator for the edges of an Eulerian path in G.

    An Eulerian path is a path that crosses every edge in G
    exactly once.

    Parameters
    ----------
    G: NetworkX Graph, DiGraph, MultiGraph or MultiDiGraph
        A directed or undirected Graph or MultiGraph.

    Returns
    -------
    edges: generator
        A generator that produces edges in the Eulerian path.

    Raises
    ------
    NetworkXError: If the graph does not have an Eulerian path.

    Notes
    -----
    Linear time algorithm, adapted from [1]_ and [3]_.
    Information about Euler paths in [2]_.
    Code for Eulerian circuit in [3]_.

    Important: In [1], Euler path is in reverse order,
    this implementation gives the path in correct order
    as in [3]_ for Eulerian_circuit. The distinction for
    directed graph is in using the in_degree neighbors, not the out
    ones. for undirected, it is using itemgetter(1) for get_vertex,
    which uses the correct vertex for this order. Also, every graph
    has an even number of odd vertices by the Handshaking Theorem [4]_.

    References
    ----------
    .. [1] http://www.graph-magics.com/articles/euler.php
    .. [2] http://en.wikipedia.org/wiki/Eulerian_path
    .. [3] https://github.com/networkx/networkx/blob/master/networkx/algorithms/euler.py
    .. [4] https://www.math.ku.edu/~jmartin/courses/math105-F11/Lectures/chapter5-part2.pdf

    """
    g = G.__class__(G)  # copy graph structure (not attributes)
    is_directed = g.is_directed()

    if is_directed:
        degree = g.in_degree
        edges = g.in_edges
        get_vertex = itemgetter(0)
    else:
        degree = g.degree
        edges = g.edges
        get_vertex = itemgetter(1)

    # Begin algorithm:
    start = _find_path_start(g)
    if not start:
        raise nx.NetworkXError("G has no Eulerian path.")

    vertex_stack = deque([start])
    last_vertex = None

    while vertex_stack:

        current_vertex = vertex_stack[-1]
        # if no neighbors:
        if degree(current_vertex) == 0:
            # Special case, we cannot add a None vertex to the path.
            if last_vertex is not None:
                yield (last_vertex, current_vertex)
            last_vertex = current_vertex
            vertex_stack.pop()
        # we have neighbors, so add the vertex to the stack (2), take
        # any of its neighbors (1) remove the edge between selected
        # neighbor and that vertex, and set that neighbor as the
        # current vertex (4).
        else:
            edge = next(edges(current_vertex))
            vertex_stack.append(get_vertex(edge))
            g.remove_edge(*edge)


def eulerian_path(G):
    """Return the edges of an Eulerian path in G.

    Check if the graph ``G'' has an Eulerian path or circuit and
    return a generator for the edges. If no path is available, raise
    an error.

    Parameters
    ----------
    G: NetworkX Graph, DiGraph, MultiGraph or MultiDiGraph
        A directed or undirected Graph or MultiGraph.

    Returns
    -------
    edges: generator
        A generator that produces edges in the Eulerian path.

    Raises
    ------
    NetworkXError: If the graph does not have an Eulerian path.

    Examples
    --------
    >>> G = nx.Graph([('W', 'N'), ('N', 'E'), ('E', 'W'), ('W', 'S'), ('S', 'E')])
    >>> len(list(nx.eulerian_path(G)))
    5

    >>> G = nx.DiGraph([(1, 2), (2, 3)])
    >>> list(nx.eulerian_path(G))
    [(1, 2), (2, 3)]
    """
    if is_eulerian(G):
        return eulerian_circuit(G)

    start = has_eulerian_path(G)
    if start:
        return _find_eulerian_path(G)

    raise nx.NetworkXError("G does not have an Eulerian path.")
