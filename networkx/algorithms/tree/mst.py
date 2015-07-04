# -*- coding: utf-8 -*-
"""
Algorithms for calculating min/max spanning trees/forests.

"""
#    Copyright (C) 2015 NetworkX Developers
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Loïc Séguin-C. <loicseguin@gmail.com>
#    All rights reserved.
#    BSD license.

__all__ = [
    'minimum_spanning_edges', 'maximum_spanning_edges',
    'minimum_spanning_tree', 'maximum_spanning_tree',
]

from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.utils import UnionFind, not_implemented_for


def kruskal_mst_edges(G, minimum, weight='weight', data=True):
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


def prim_mst_edges(G, minimum, weight='weight', data=True):
    push = heappush
    pop = heappop

    nodes = list(G.nodes())
    c = count()

    sign = 1
    if not minimum:
        sign = -1

    while nodes:
        u = nodes.pop(0)
        frontier = []
        visited = [u]
        for u, v in G.edges(u):
            push(frontier, (G[u][v].get(weight, 1) * sign, next(c), u, v))

        while frontier:
            W, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            for v, w in G.edges(v):
                if w in visited:
                    continue
                push(frontier, (G[v][w].get(weight, 1) * sign, next(c), v, w))

            if data:
                yield u, v, G[u][v]
            else:
                yield u, v

ALGORITHMS = {
    'kruskal': kruskal_mst_edges,
    'prim': prim_mst_edges
}


@not_implemented_for('directed')
def _spanning_edges(G, minimum, algorithm='kruskal', weight='weight', data=True):
    try:
        algo = ALGORITHMS[algorithm]
    except KeyError:
        msg = '{} is not a valid choice for an algorithm.'.format(algorithm)
        raise ValueError(msg)

    return algo(G, minimum=minimum, weight=weight, data=data)


def minimum_spanning_edges(G, algorithm='kruskal', weight='weight', data=True):
    """Generate edges in a minimum spanning forest of an undirected
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree)
    with the minimum sum of edge weights.  A spanning forest is a
    union of the spanning trees for each connected component of the graph.

    Parameters
    ----------
    G : undirected Graph
       An undirected graph. If `G` is connected, then the algorithm finds a
       spanning tree. Otherwise, a spanning forest is found.

    algorithm : string
       The algorithm to use when finding a minimum spanning tree. Valid
       choices are 'kruskal' or 'prim'. Default is 'kruskal'.

    weight : string
       Edge data key to use for weight (default 'weight').

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       A generator that produces edges in the minimum spanning tree.
       The edges are three-tuples (u,v,w) where w is the weight.

    Examples
    --------
    >>> from networkx.algorithms import tree

    Find minimum spanning edges by Kruskal's algorithm

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> mst = tree.minimum_spanning_edges(G, algorithm='kruskal', data=False)
    >>> edgelist = list(mst)
    >>> sorted(edgelist)
    [(0, 1), (1, 2), (2, 3)]

    Find minimum spanning edges by Prim's algorithm

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> mst = tree.minimum_spanning_edges(G, algorithm='prim', data=False)
    >>> edgelist = list(mst)
    >>> sorted(edgelist)
    [(0, 1), (1, 2), (2, 3)]

    Notes
    -----

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.

    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/
    """
    return _spanning_edges(G, minimum=True, algorithm=algorithm,
                           weight=weight, data=data)


def maximum_spanning_edges(G, algorithm='kruskal', weight='weight', data=True):
    """Generate edges in a maximum spanning forest of an undirected
    weighted graph.

    A maximum spanning tree is a subgraph of the graph (a tree)
    with the maximum possible sum of edge weights.  A spanning forest is a
    union of the spanning trees for each connected component of the graph.

    Parameters
    ----------
    G : undirected Graph
       An undirected graph. If `G` is connected, then the algorithm finds a
       spanning tree. Otherwise, a spanning forest is found.

    algorithm : string
       The algorithm to use when finding a minimum spanning tree. Valid
       choices are 'kruskal' or 'prim'. Default is 'kruskal'.

    weight : string
       Edge data key to use for weight (default 'weight').

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       A generator that produces edges in the maximum spanning tree.
       The edges are three-tuples (u,v,w) where w is the weight.

    Examples
    --------
    >>> from networkx.algorithms import tree

    Find maximum spanning edges by Kruskal's algorithm

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 3, weight=2)
    >>> mst = tree.maximum_spanning_edges(G, algorithm='kruskal', data=False)
    >>> edgelist = list(mst)
    >>> sorted(edgelist)
    [(0, 1), (0, 3), (1, 2)]

    Find maximum spanning edges by Prim's algorithm

    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >>> mst = tree.maximum_spanning_edges(G, algorithm='prim', data=False)
    >>> edgelist = list(mst)
    >>> sorted(edgelist)
    [(0, 1), (0, 3), (3, 2)]

    Notes
    -----
    If the graph edges do not have a weight attribute a default weight of 1
    will be used.
    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/
    """
    return _spanning_edges(G, minimum=False, algorithm=algorithm,
                           weight=weight, data=data)


@not_implemented_for('directed')
def _optimum_spanning_tree(G, algorithm, minimum, weight='weight'):
    try:
        algo = ALGORITHMS[algorithm]
    except KeyError:
        msg = '{} is not a valid choice for an algorithm.'.format(algorithm)
        raise ValueError(msg)

    edges = algo(G, minimum=minimum, weight=weight, data=True)
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
    return _optimum_spanning_tree(G, algorithm=algorithm, minimum=True,
                                  weight=weight)


def maximum_spanning_tree(G, weight='weight', algorithm='kruskal'):
    """Returns a maximum spanning tree or forest on an undirected graph `G`.

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
    return _optimum_spanning_tree(G, algorithm=algorithm, minimum=False,
                                  weight=weight)
