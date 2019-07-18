# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg <aric.hagberg@gmail.com>
#          Sérgio Nery Simões <sergionery@gmail.com>
"""
Compute the shortest paths and path lengths between nodes in the graph.

These algorithms work with undirected and directed graphs.

"""
from __future__ import division

import networkx as nx

__all__ = ['shortest_path', 'all_shortest_paths',
           'shortest_path_length', 'average_shortest_path_length',
           'has_path']


def has_path(G, source, target):
    """Returns *True* if *G* has a path from *source* to *target*.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path
    """
    try:
        nx.shortest_path(G, source, target)
    except nx.NetworkXNoPath:
        return False
    return True


def shortest_path(G, source=None, target=None, weight=None, method='dijkstra'):
    """Compute shortest paths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
        Starting node for path. If not specified, compute shortest
        paths for each possible starting node.

    target : node, optional
        Ending node for path. If not specified, compute shortest
        paths to all possible nodes.

    weight : None or string, optional (default = None)
        If None, every edge has weight/distance/cost 1.
        If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.

    method : string, optional (default = 'dijkstra')
        The algorithm to use to compute the path.
        Supported options: 'dijkstra', 'bellman-ford'.
        Other inputs produce a ValueError.
        If `weight` is None, unweighted graph methods are used, and this
        suggestion is ignored.

    Returns
    -------
    path: list or dictionary
        All returned paths include both the source and target in the path.

        If the source and target are both specified, return a single list
        of nodes in a shortest path from the source to the target.

        If only the source is specified, return a dictionary keyed by
        targets with a list of nodes in a shortest path from the source
        to one of the targets.

        If only the target is specified, return a dictionary keyed by
        sources with a list of nodes in a shortest path from one of the
        sources to the target.

        If neither the source nor target are specified return a dictionary
        of dictionaries with path[source][target]=[list of nodes in path].

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    ValueError
        If `method` is not among the supported options.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.shortest_path(G, source=0, target=4))
    [0, 1, 2, 3, 4]
    >>> p = nx.shortest_path(G, source=0) # target not specified
    >>> p[4]
    [0, 1, 2, 3, 4]
    >>> p = nx.shortest_path(G, target=4) # source not specified
    >>> p[0]
    [0, 1, 2, 3, 4]
    >>> p = nx.shortest_path(G) # source, target not specified
    >>> p[0][4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    There may be more than one shortest path between a source and target.
    This returns only one of them.

    See Also
    --------
    all_pairs_shortest_path()
    all_pairs_dijkstra_path()
    all_pairs_bellman_ford_path()
    single_source_shortest_path()
    single_source_dijkstra_path()
    single_source_bellman_ford_path()
    """
    if method not in ('dijkstra', 'bellman-ford'):
        # so we don't need to check in each branch later
        raise ValueError('method not supported: {}'.format(method))
    method = 'unweighted' if weight is None else method
    if source is None:
        if target is None:
            # Find paths between all pairs.
            if method == 'unweighted':
                paths = dict(nx.all_pairs_shortest_path(G))
            elif method == 'dijkstra':
                paths = dict(nx.all_pairs_dijkstra_path(G, weight=weight))
            else:  # method == 'bellman-ford':
                paths = dict(nx.all_pairs_bellman_ford_path(G, weight=weight))
        else:
            # Find paths from all nodes co-accessible to the target.
            with nx.utils.reversed(G):
                if method == 'unweighted':
                    paths = nx.single_source_shortest_path(G, target)
                elif method == 'dijkstra':
                    paths = nx.single_source_dijkstra_path(G, target,
                                                           weight=weight)
                else:  # method == 'bellman-ford':
                    paths = nx.single_source_bellman_ford_path(G, target,
                                                               weight=weight)
                # Now flip the paths so they go from a source to the target.
                for target in paths:
                    paths[target] = list(reversed(paths[target]))
    else:
        if target is None:
            # Find paths to all nodes accessible from the source.
            if method == 'unweighted':
                paths = nx.single_source_shortest_path(G, source)
            elif method == 'dijkstra':
                paths = nx.single_source_dijkstra_path(G, source,
                                                       weight=weight)
            else:  # method == 'bellman-ford':
                paths = nx.single_source_bellman_ford_path(G, source,
                                                           weight=weight)
        else:
            # Find shortest source-target path.
            if method == 'unweighted':
                paths = nx.bidirectional_shortest_path(G, source, target)
            elif method == 'dijkstra':
                paths = nx.dijkstra_path(G, source, target, weight)
            else:  # method == 'bellman-ford':
                paths = nx.bellman_ford_path(G, source, target, weight)
    return paths


def shortest_path_length(G,
                         source=None,
                         target=None,
                         weight=None,
                         method='dijkstra'):
    """Compute shortest path lengths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
        Starting node for path.
        If not specified, compute shortest path lengths using all nodes as
        source nodes.

    target : node, optional
        Ending node for path.
        If not specified, compute shortest path lengths using all nodes as
        target nodes.

    weight : None or string, optional (default = None)
        If None, every edge has weight/distance/cost 1.
        If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.

    method : string, optional (default = 'dijkstra')
        The algorithm to use to compute the path length.
        Supported options: 'dijkstra', 'bellman-ford'.
        Other inputs produce a ValueError.
        If `weight` is None, unweighted graph methods are used, and this
        suggestion is ignored.

    Returns
    -------
    length: int or iterator
        If the source and target are both specified, return the length of
        the shortest path from the source to the target.

        If only the source is specified, return a dict keyed by target
        to the shortest path length from the source to that target.

        If only the target is specified, return a dict keyed by source
        to the shortest path length from that source to the target.

        If neither the source nor target are specified, return an iterator
        over (source, dictionary) where dictionary is keyed by target to
        shortest path length from source to that target.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    ValueError
        If `method` is not among the supported options.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.shortest_path_length(G, source=0, target=4)
    4
    >>> p = nx.shortest_path_length(G, source=0) # target not specified
    >>> p[4]
    4
    >>> p = nx.shortest_path_length(G, target=4) # source not specified
    >>> p[0]
    4
    >>> p = dict(nx.shortest_path_length(G)) # source,target not specified
    >>> p[0][4]
    4

    Notes
    -----
    The length of the path is always 1 less than the number of nodes involved
    in the path since the length measures the number of edges followed.

    For digraphs this returns the shortest directed path length. To find path
    lengths in the reverse direction use G.reverse(copy=False) first to flip
    the edge orientation.

    See Also
    --------
    all_pairs_shortest_path_length()
    all_pairs_dijkstra_path_length()
    all_pairs_bellman_ford_path_length()
    single_source_shortest_path_length()
    single_source_dijkstra_path_length()
    single_source_bellman_ford_path_length()
    """
    if method not in ('dijkstra', 'bellman-ford'):
        # so we don't need to check in each branch later
        raise ValueError('method not supported: {}'.format(method))
    method = 'unweighted' if weight is None else method
    if source is None:
        if target is None:
            # Find paths between all pairs.
            if method == 'unweighted':
                paths = nx.all_pairs_shortest_path_length(G)
            elif method == 'dijkstra':
                paths = nx.all_pairs_dijkstra_path_length(G, weight=weight)
            else:  # method == 'bellman-ford':
                paths = nx.all_pairs_bellman_ford_path_length(G, weight=weight)
        else:
            # Find paths from all nodes co-accessible to the target.
            with nx.utils.reversed(G):
                if method == 'unweighted':
                    # We need to exhaust the iterator as Graph needs
                    # to be reversed.
                    path_length = nx.single_source_shortest_path_length
                    paths = path_length(G, target)
                elif method == 'dijkstra':
                    path_length = nx.single_source_dijkstra_path_length
                    paths = path_length(G, target, weight=weight)
                else:  # method == 'bellman-ford':
                    path_length = nx.single_source_bellman_ford_path_length
                    paths = path_length(G, target, weight=weight)
    else:
        if target is None:
            # Find paths to all nodes accessible from the source.
            if method == 'unweighted':
                paths = nx.single_source_shortest_path_length(G, source)
            elif method == 'dijkstra':
                path_length = nx.single_source_dijkstra_path_length
                paths = path_length(G, source, weight=weight)
            else:  # method == 'bellman-ford':
                path_length = nx.single_source_bellman_ford_path_length
                paths = path_length(G, source, weight=weight)
        else:
            # Find shortest source-target path.
            if method == 'unweighted':
                p = nx.bidirectional_shortest_path(G, source, target)
                paths = len(p) - 1
            elif method == 'dijkstra':
                paths = nx.dijkstra_path_length(G, source, target, weight)
            else:  # method == 'bellman-ford':
                paths = nx.bellman_ford_path_length(G, source, target, weight)
    return paths


def average_shortest_path_length(G, weight=None, method='dijkstra'):
    r"""Returns the average shortest path length.

    The average shortest path length is

    .. math::

       a =\sum_{s,t \in V} \frac{d(s, t)}{n(n-1)}

    where `V` is the set of nodes in `G`,
    `d(s, t)` is the shortest path from `s` to `t`,
    and `n` is the number of nodes in `G`.

    Parameters
    ----------
    G : NetworkX graph

    weight : None or string, optional (default = None)
       If None, every edge has weight/distance/cost 1.
       If a string, use this edge attribute as the edge weight.
       Any edge attribute not present defaults to 1.

    method : string, optional (default = 'dijkstra')
        The algorithm to use to compute the path lengths.
        Supported options: 'dijkstra', 'bellman-ford'.
        Other inputs produce a ValueError.
        If `weight` is None, unweighted graph methods are used, and this
        suggestion is ignored.

    Raises
    ------
    NetworkXPointlessConcept
        If `G` is the null graph (that is, the graph on zero nodes).

    NetworkXError
        If `G` is not connected (or not weakly connected, in the case
        of a directed graph).

    ValueError
        If `method` is not among the supported options.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.average_shortest_path_length(G)
    2.0

    For disconnected graphs, you can compute the average shortest path
    length for each component

    >>> G = nx.Graph([(1, 2), (3, 4)])
    >>> for C in nx.connected_component_subgraphs(G):
    ...     print(nx.average_shortest_path_length(C))
    1.0
    1.0

    """
    method = 'unweighted' if weight is None else method
    n = len(G)
    # For the special case of the null graph, raise an exception, since
    # there are no paths in the null graph.
    if n == 0:
        msg = ('the null graph has no paths, thus there is no average'
               'shortest path length')
        raise nx.NetworkXPointlessConcept(msg)
    # For the special case of the trivial graph, return zero immediately.
    if n == 1:
        return 0
    # Shortest path length is undefined if the graph is disconnected.
    if G.is_directed() and not nx.is_weakly_connected(G):
        raise nx.NetworkXError("Graph is not weakly connected.")
    if not G.is_directed() and not nx.is_connected(G):
        raise nx.NetworkXError("Graph is not connected.")
    # Compute all-pairs shortest paths.

    def path_length(v):
        if method == 'unweighted':
            return nx.single_source_shortest_path_length(G, v)
        elif method == 'dijkstra':
            return nx.single_source_dijkstra_path_length(G, v, weight=weight)
        elif method == 'bellman-ford':
            return nx.single_source_bellman_ford_path_length(G, v,
                                                             weight=weight)
        else:
            raise ValueError('method not supported: {}'.format(method))
    # Sum the distances for each (ordered) pair of source and target node.
    s = sum(l for u in G for l in path_length(u).values())
    return s / (n * (n - 1))


def all_shortest_paths(G, source, target, weight=None, method='dijkstra'):
    """Compute all shortest paths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path.

    target : node
       Ending node for path.

    weight : None or string, optional (default = None)
       If None, every edge has weight/distance/cost 1.
       If a string, use this edge attribute as the edge weight.
       Any edge attribute not present defaults to 1.

    method : string, optional (default = 'dijkstra')
       The algorithm to use to compute the path lengths.
       Supported options: 'dijkstra', 'bellman-ford'.
       Other inputs produce a ValueError.
       If `weight` is None, unweighted graph methods are used, and this
       suggestion is ignored.

    Returns
    -------
    paths : generator of lists
        A generator of all paths between source and target.

    Raises
    ------
    ValueError
        If `method` is not among the supported options.

    NetworkXNoPath
        If `target` cannot be reached from `source`.

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_path(G, [0, 1, 2])
    >>> nx.add_path(G, [0, 10, 2])
    >>> print([p for p in nx.all_shortest_paths(G, source=0, target=2)])
    [[0, 1, 2], [0, 10, 2]]

    Notes
    -----
    There may be many shortest paths between the source and target.

    See Also
    --------
    shortest_path()
    single_source_shortest_path()
    all_pairs_shortest_path()
    """
    method = 'unweighted' if weight is None else method
    if method == 'unweighted':
        pred = nx.predecessor(G, source)
    elif method == 'dijkstra':
        pred, dist = nx.dijkstra_predecessor_and_distance(G, source,
                                                          weight=weight)
    elif method == 'bellman-ford':
        pred, dist = nx.bellman_ford_predecessor_and_distance(G, source,
                                                              weight=weight)
    else:
        raise ValueError('method not supported: {}'.format(method))

    if target not in pred:
        raise nx.NetworkXNoPath('Target {} cannot be reached'
                                'from Source {}'.format(target, source))

    stack = [[target, 0]]
    top = 0
    while top >= 0:
        node, i = stack[top]
        if node == source:
            yield [p for p, n in reversed(stack[:top + 1])]
        if len(pred[node]) > i:
            top += 1
            if top == len(stack):
                stack.append([pred[node][i], 0])
            else:
                stack[top] = [pred[node][i], 0]
        else:
            stack[top - 1][1] += 1
            top -= 1
