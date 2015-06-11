# -*- coding: utf-8 -*-
"""
Algorithms for calculating min/max spanning trees/forest.

"""
#    Copyright (C) 2009-2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Loïc Séguin-C. <loicseguin@gmail.com>
#    All rights reserved.
#    BSD license.

__all__ = [
    # Algorithms
    'kruskal_mst_edges',
    'prim_mst_edges',

    # Recommended API
    'minimum_spanning_tree',
    'maximum_spanning_tree',
]

from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.utils import UnionFind

@nx.utils.not_implemented_for('directed')
def kruskal_mst_edges(G, minimum, weight='weight', data=True):
    """Generates the edges of a minimum or maximum spanning tree on `G`.

    Parameters
    ----------
    G : undirected graph
        An undirected graph. If `G` is connected, then the algorithm finds a
        spanning tree. Otherwise, a spanning forest is found.

    minimum : bool
       If `True`, find a minimum spanning tree. Otherwise, find a maximum
       spanning tree.

    weight : str
       Data key to use for edge weights.

    data : bool
       If `True`, the edge data is included with each yielded edge.


    Returns
    -------
    edges : iterator
        A generator that produces edges in the minimum/maximum spanning tree.
        The edges are 2-tuples (u, v) or 3-tuples (u, v, d) where u and v
        define the included edge and d is the edge data.


    Examples
    --------
    Find a minimum spanning tree.

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> mst = nx.kruskal_mst_edges(G, minimum=True, data=False)
    >>> sorted(mst)
    [(0, 1), (1, 2), (2, 3)]

    Find a maximum spanning tree.

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2)
    >>> mst = nx.kruskal_mst_edges(G, minimum=False, data=False)
    >>> sorted(mst)
    [(0, 1), (0, 3), (1, 2)]


    Notes
    -----
    Uses Kruskal's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.

    There may be more than one tree with the same minimum or maximum weight.
    See :mod:`networkx.tree.recognition` for more detailed definitions.

    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/
    """
    subtrees = UnionFind()
    edges = sorted(G.edges(data=True), key=lambda t: t[2].get(weight, 1),
                   reverse=not minimum)

    for u, v, d in edges:
        if subtrees[u] != subtrees[v]:
            if data:
                yield (u, v, d)
            else:
                yield (u, v)
            subtrees.union(u, v)


@nx.utils.not_implemented_for('directed')
def prim_mst_edges(G, minimum, weight='weight', data=True):
    """Generates the edges of a minimum or maximum spanning tree on `G`.

    Parameters
    ----------
    G : undirected graph
        An undirected graph. If `G` is connected, then the algorithm finds a
        spanning tree. Otherwise, a spanning forest is found.

    minimum : bool
       If `True`, find a minimum spanning tree. Otherwise, find a maximum
       spanning tree.

    weight : str
       Data key to use for edge weights.

    data : bool
       If `True`, the edge data is included with each yielded edge.


    Returns
    -------
    edges : iterator
        A generator that produces edges in the minimum/maximum spanning tree.
        The edges are 2-tuples (u, v) or 3-tuples (u, v, d) where u and v
        define the included edge and d is the edge data.


    Examples
    --------
    Find a minimum spanning tree.

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> mst = nx.prim_mst_edges(G, minimum=True, data=False)
    >>> sorted(mst)
    [(0, 1), (1, 2), (2, 3)]

    Find a maximum spanning tree.

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2)
    >>> mst = nx.prim_mst_edges(G, minimum=False, data=False)
    >>> sorted(mst)
    [(0, 1), (0, 3), (3, 2)]


    Notes
    -----
    Uses Prim's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.

    There may be more than one tree with the same minimum or maximum weight.
    See :mod:`networkx.tree.recognition` for more detailed definitions.

    """
    push = heappush
    pop = heappop

    nodes = G.nodes()
    c = count()

    neg = 1
    if not minimum:
        neg = -1

    while nodes:
        u = nodes.pop(0)
        frontier = []
        visited = [u]
        for u, v in G.edges(u):
            push(frontier, (G[u][v].get(weight, 1) * neg, next(c), u, v))

        while frontier:
            W, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            for v, w in G.edges(v):
                if w in visited:
                    continue
                push(frontier, (G[v][w].get(weight, 1) * neg, next(c), v, w))

            if data:
                yield u, v, G[u][v]
            else:
                yield u, v


ALGORITHMS = {
    'kruskal': kruskal_mst_edges,
    'prim': prim_mst_edges
}

def mst_tree(G, algorithm, minimum, weight='weight'):
    if algorithm not in ALGORITHMS:
        msg = '{} is not a valid choice for an algorithm.'.format(algorithm)
        raise ValueError(msg)

    edges = ALGORITHMS[algorithm](G, minimum=minimum, weight=weight, data=True)
    T = nx.Graph(edges)

    # Add isolated nodes
    if len(T) != len(G):
        T.add_nodes_from([n for n, d in G.degree().items() if d == 0])

    # Add node and graph attributes as shallow copy
    for n in T:
        T.node[n] = G.node[n].copy()
    T.graph = G.graph.copy()

    return T


def minimum_spanning_tree(G, weight='weight', algorithm='kruskal'):
    """Returns a minimum spanning tree or forest on an undirected graph `G`.

    Parameters
    ----------
    G : undirected graph
        An undirected graph. If `G` is connected, then the algorithm finds a
        spanning tree. Otherwise, a spanning forest is found.

    weight : str
       Data key to use for edge weights.

    algorithm : str
        The algorithm to use when finding a minimum spanning tree. Valid
        choices are 'kruskal' or 'prim'.


    Returns
    -------
    G : NetworkX Graph
       A minimum spanning tree or forest.


    Examples
    --------
    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> T = nx.minimum_spanning_tree(G)
    >>> sorted(T.edges(data=True))
    [(0, 1, {}), (1, 2, {}), (2, 3, {})]


    Notes
    -----
    If the graph edges do not have a weight attribute a default weight of 1
    will be used.

    There may be more than one tree with the same minimum or maximum weight.
    See :mod:`networkx.tree.recognition` for more detailed definitions.

    """
    return mst_tree(G, algorithm=algorithm, minimum=True, weight=weight)


def maximum_spanning_tree(G, weight='weight', algorithm='kruskal'):
    """Returns a minimum spanning tree or forest on an undirected graph `G`.

    Parameters
    ----------
    G : undirected graph
        An undirected graph. If `G` is connected, then the algorithm finds a
        spanning tree. Otherwise, a spanning forest is found.

    weight : str
       Data key to use for edge weights.

    algorithm : str
        The algorithm to use when finding a minimum spanning tree. Valid
        choices are 'kruskal' or 'prim'.


    Returns
    -------
    G : NetworkX Graph
       A minimum spanning tree or forest.


    Examples
    --------
    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> T = nx.maximum_spanning_tree(G)
    >>> sorted(T.edges(data=True))
    [(0, 1, {}), (0, 3, {'weight': 2}), (1, 2, {})]


    Notes
    -----
    If the graph edges do not have a weight attribute a default weight of 1
    will be used.

    There may be more than one tree with the same minimum or maximum weight.
    See :mod:`networkx.tree.recognition` for more detailed definitions.

    """
    return mst_tree(G, algorithm=algorithm, minimum=False, weight=weight)

