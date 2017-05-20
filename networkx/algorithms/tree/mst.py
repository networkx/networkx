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


@not_implemented_for('multigraph')
def boruvka_mst_edges(G, minimum=True, weight='weight', keys=False, data=True):
    """Iterates over the edges of a minimum spanning tree as computed by
    Borůvka's algorithm.

    `G` is a NetworkX graph. Also, the edges must have distinct weights,
    otherwise the edges may not form a tree.

    `weight` is the edge attribute that stores the edge weights. Each
    edge in the graph must have such an attribute, otherwise a
    :exc:`KeyError` will be raised.

    If `data` is True, this iterator yields edges of the form
    ``(u, v, d)``, where ``u`` and ``v`` are nodes and ``d`` is the edge
    attribute dictionary. Otherwise, it yields edges of the form
    ``(u, v)``.

    The `keys` argument is ignored, since this function is not
    implemented for multigraphs; it exists only for consistency with the
    other minimum spanning tree functions.

    """
    opt = min if minimum else max
    # Initialize a forest, assuming initially that it is the discrete
    # partition of the nodes of the graph.
    forest = UnionFind(G)

    def best_edge(component):
        """Returns the optimum (minimum or maximum) edge on the edge
        boundary of the given set of nodes.

        A return value of ``None`` indicates an empty boundary.

        """
        # TODO In Python 3.4 and later, we can just do
        #
        #     boundary = nx.edge_boundary(G, component, data=weight)
        #     return opt(boundary, key=lambda e: e[-1][weight], default=None)
        #
        # which is better because it doesn't require creating a list.
        boundary = list(nx.edge_boundary(G, component, data=True))
        if not boundary:
            return None
        return opt(boundary, key=lambda e: e[-1][weight])

    # Determine the optimum edge in the edge boundary of each component
    # in the forest.
    best_edges = (best_edge(component) for component in forest.to_sets())
    best_edges = [edge for edge in best_edges if edge is not None]
    # If each entry was ``None``, that means the graph was disconnected,
    # so we are done generating the forest.
    while best_edges:
        # Determine the optimum edge in the edge boundary of each
        # component in the forest.
        #
        # This must be a sequence, not an iterator. In this list, the
        # same edge may appear twice, in different orientations (but
        # that's okay, since a union operation will be called on the
        # endpoints the first time it is seen, but not the second time).
        #
        # Any ``None`` indicates that the edge boundary for that
        # component was empty, so that part of the forest has been
        # completed.
        #
        # TODO This can be parallelized, both in the outer loop over
        # each component in the forest and in the computation of the
        # minimum. (Same goes for the identical lines outside the loop.)
        best_edges = (best_edge(component) for component in forest.to_sets())
        best_edges = [edge for edge in best_edges if edge is not None]
        # Join trees in the forest using the best edges, and yield that
        # edge, since it is part of the spanning tree.
        #
        # TODO This loop can be parallelized, to an extent (the union
        # operation must be atomic).
        for u, v, d in best_edges:
            if forest[u] != forest[v]:
                if data:
                    yield u, v, d
                else:
                    yield u, v
                forest.union(u, v)


def kruskal_mst_edges(G, minimum, weight='weight', keys=True, data=True):
    subtrees = UnionFind()
    if G.is_multigraph():
        edges = G.edges(keys=True, data=True)
    else:
        edges = G.edges(data=True)
    getweight = lambda t: t[-1].get(weight, 1)
    edges = sorted(edges, key=getweight, reverse=not minimum)
    is_multigraph = G.is_multigraph()
    # Multigraphs need to handle edge keys in addition to edge data.
    if is_multigraph:
        for u, v, k, d in edges:
            if subtrees[u] != subtrees[v]:
                if keys:
                    if data:
                        yield (u, v, k, d)
                    else:
                        yield (u, v, k)
                else:
                    if data:
                        yield (u, v, d)
                    else:
                        yield (u, v)
                subtrees.union(u, v)
    else:
        for u, v, d in edges:
            if subtrees[u] != subtrees[v]:
                if data:
                    yield (u, v, d)
                else:
                    yield (u, v)
                subtrees.union(u, v)


def prim_mst_edges(G, minimum, weight='weight', keys=True, data=True):
    is_multigraph = G.is_multigraph()
    push = heappush
    pop = heappop

    nodes = list(G)
    c = count()

    sign = 1
    if not minimum:
        sign = -1

    while nodes:
        u = nodes.pop(0)
        frontier = []
        visited = [u]
        if is_multigraph:
            for u, v, k, d in G.edges(u, keys=True, data=True):
                push(frontier, (d.get(weight, 1) * sign, next(c), u, v, k))
        else:
            for u, v, d in G.edges(u, data=True):
                push(frontier, (d.get(weight, 1) * sign, next(c), u, v))
        while frontier:
            if is_multigraph:
                W, _, u, v, k = pop(frontier)
            else:
                W, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            if is_multigraph:
                for _, w, k2, d2 in G.edges(v, keys=True, data=True):
                    if w in visited:
                        continue
                    new_weight = d2.get(weight, 1) * sign
                    push(frontier, (new_weight, next(c), v, w, k2))
            else:
                for _, w, d2 in G.edges(v, data=True):
                    if w in visited:
                        continue
                    new_weight = d2.get(weight, 1) * sign
                    push(frontier, (new_weight, next(c), v, w))
            # Multigraphs need to handle edge keys in addition to edge data.
            if is_multigraph and keys:
                if data:
                    yield u, v, k, G[u][v]
                else:
                    yield u, v, k
            else:
                if data:
                    yield u, v, G[u][v]
                else:
                    yield u, v

ALGORITHMS = {
    'boruvka': boruvka_mst_edges,
    u'borůvka': boruvka_mst_edges,
    'kruskal': kruskal_mst_edges,
    'prim': prim_mst_edges
}


@not_implemented_for('directed')
def _spanning_edges(G, minimum, algorithm='kruskal', weight='weight',
                    keys=True, data=True):
    try:
        algo = ALGORITHMS[algorithm]
    except KeyError:
        msg = '{} is not a valid choice for an algorithm.'.format(algorithm)
        raise ValueError(msg)

    return algo(G, minimum=minimum, weight=weight, keys=keys, data=data)


def minimum_spanning_edges(G, algorithm='kruskal', weight='weight', keys=True,
                           data=True):
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
       choices are 'kruskal', 'prim', or 'boruvka'. The default is
       'kruskal'.

    weight : string
       Edge data key to use for weight (default 'weight').

    keys : bool
       Whether to yield edge key in multigraphs in addition to the
       edge. If `G` is not a multigraph, this is ignored.

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       An iterator over tuples representing edges in a minimum spanning
       tree of `G`.

       If `G` is a multigraph and both `keys` and `data` are
       True, then the tuples are four-tuples of the form `(u, v, k,
       w)`, where `(u, v)` is an edge, `k` is the edge key
       identifying the particular edge joining `u` with `v`, and
       `w` is the weight of the edge. If `keys` is True but
       `data` is False, the tuples are three-tuples of the form
       `(u, v, k)`.

       If `G` is not a multigraph, the tuples are of the form `(u, v,
       w)` if `data` is True or `(u, v)` if `data` is
       False.

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
    For Borůvka's algorithm, each edge must have a weight attribute, and
    each edge weight must be distinct.

    For the other algorithms, if the graph edges do not have a weight
    attribute a default weight of 1 will be used.

    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/

    """
    return _spanning_edges(G, minimum=True, algorithm=algorithm,
                           weight=weight, keys=keys, data=data)


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
       The algorithm to use when finding a maximum spanning tree. Valid
       choices are 'kruskal', 'prim', or 'boruvka'. The default is
       'kruskal'.

    weight : string
       Edge data key to use for weight (default 'weight').

    keys : bool
       Whether to yield edge key in multigraphs in addition to the
       edge. If `G` is not a multigraph, this is ignored.

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       An iterator over tuples representing edges in a maximum spanning
       tree of `G`.

       If `G` is a multigraph and both `keys` and `data` are
       True, then the tuples are four-tuples of the form `(u, v, k,
       w)`, where `(u, v)` is an edge, `k` is the edge key
       identifying the particular edge joining `u` with `v`, and
       `w` is the weight of the edge. If `keys` is True but
       `data` is False, the tuples are three-tuples of the form
       `(u, v, k)`.

       If `G` is not a multigraph, the tuples are of the form `(u, v,
       w)` if `data` is True or `(u, v)` if `data` is
       False.

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
    For Borůvka's algorithm, each edge must have a weight attribute, and
    each edge weight must be distinct.

    For the other algorithms, if the graph edges do not have a weight
    attribute a default weight of 1 will be used.

    Modified code from David Eppstein, April 2006
    http://www.ics.uci.edu/~eppstein/PADS/
    """
    return _spanning_edges(G, minimum=False, algorithm=algorithm,
                           weight=weight, data=data)


@not_implemented_for('directed')
def _optimum_spanning_tree(G, algorithm, minimum, weight='weight'):
    # When creating the spanning tree, we can ignore the key used to
    # identify multigraph edges, since a tree is guaranteed to have no
    # multiedges. This is why we use `keys=False`.
    edges = _spanning_edges(G, minimum, algorithm=algorithm, weight=weight,
                            keys=False, data=True)
    T = nx.Graph(edges)

    # Add isolated nodes
    if len(T) != len(G):
        T.add_nodes_from(nx.isolates(G))

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

    algorithm : string
       The algorithm to use when finding a minimum spanning tree. Valid
       choices are 'kruskal', 'prim', or 'boruvka'. The default is
       'kruskal'.

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
    For Borůvka's algorithm, each edge must have a weight attribute, and
    each edge weight must be distinct.

    For the other algorithms, if the graph edges do not have a weight
    attribute a default weight of 1 will be used.

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

    algorithm : string
       The algorithm to use when finding a minimum spanning tree. Valid
       choices are 'kruskal', 'prim', or 'boruvka'. The default is
       'kruskal'.


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
    For Borůvka's algorithm, each edge must have a weight attribute, and
    each edge weight must be distinct.

    For the other algorithms, if the graph edges do not have a weight
    attribute a default weight of 1 will be used.

    There may be more than one tree with the same minimum or maximum weight.
    See :mod:`networkx.tree.recognition` for more detailed definitions.

    """
    return _optimum_spanning_tree(G, algorithm=algorithm, minimum=False,
                                  weight=weight)
