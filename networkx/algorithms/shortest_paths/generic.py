# -*- coding: utf-8 -*-
"""
Compute the shortest paths and path lengths between nodes in the graph.

These algorithms work with undirected and directed graphs.

For directed graphs the paths can be computed in the reverse
order by first flipping the edge orientation using R=G.reverse(copy=False).

"""
#    Copyright (C) 2004-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                            'Sérgio Nery Simões <sergionery@gmail.com>'])
__all__ = ['shortest_path', 'all_shortest_paths',
           'shortest_path_length', 'average_shortest_path_length',
           'has_path']

def has_path(G, source, target):
    """Return True if G has a path from source to target, False otherwise.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path
    """
    try:
        sp = nx.shortest_path(G,source, target)
    except nx.NetworkXNoPath:
        return False
    return True


def shortest_path(G, source=None, target=None, weight=None):
    """Compute shortest paths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
        Starting node for path.
        If not specified, compute shortest paths using all nodes as source nodes.

    target : node, optional
        Ending node for path.
        If not specified, compute shortest paths using all nodes as target nodes.

    weight : None or string, optional (default = None)
        If None, every edge has weight/distance/cost 1.
        If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.

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

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print(nx.shortest_path(G,source=0,target=4))
    [0, 1, 2, 3, 4]
    >>> p=nx.shortest_path(G,source=0) # target not specified
    >>> p[4]
    [0, 1, 2, 3, 4]
    >>> p=nx.shortest_path(G,target=4) # source not specified
    >>> p[0]
    [0, 1, 2, 3, 4]
    >>> p=nx.shortest_path(G) # source,target not specified
    >>> p[0][4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    There may be more than one shortest path between a source and target.
    This returns only one of them.

    For digraphs this returns a shortest directed path. To find paths in the
    reverse direction first use G.reverse(copy=False) to flip the edge
    orientation.

    See Also
    --------
    all_pairs_shortest_path()
    all_pairs_dijkstra_path()
    single_source_shortest_path()
    single_source_dijkstra_path()
    """
    if source is None:
        if target is None:
            ## Find paths between all pairs.
            if weight is None:
                paths=nx.all_pairs_shortest_path(G)
            else:
                paths=nx.all_pairs_dijkstra_path(G,weight=weight)
        else:
            ## Find paths from all nodes co-accessible to the target.
            directed = G.is_directed()
            if directed:
               G.reverse(copy=False)

            if weight is None:
                paths=nx.single_source_shortest_path(G,target)
            else:
                paths=nx.single_source_dijkstra_path(G,target,weight=weight)

            # Now flip the paths so they go from a source to the target.
            for target in paths:
                paths[target] = list(reversed(paths[target]))

            if directed:
                G.reverse(copy=False)
    else:
        if target is None:
            ## Find paths to all nodes accessible from the source.
            if weight is None:
                paths=nx.single_source_shortest_path(G,source)
            else:
                paths=nx.single_source_dijkstra_path(G,source,weight=weight)
        else:
            ## Find shortest source-target path.
            if weight is None:
                paths=nx.bidirectional_shortest_path(G,source,target)
            else:
                paths=nx.dijkstra_path(G,source,target,weight)

    return paths


def shortest_path_length(G, source=None, target=None, weight=None):
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

    Returns
    -------
    length: int or dictionary
        If the source and target are both specified, return the length of
        the shortest path from the source to the target.

        If only the source is specified, return a dictionary keyed by
        targets whose values are the lengths of the shortest path from the
        source to one of the targets.

        If only the target is specified, return a dictionary keyed by
        sources whose values are the lengths of the shortest path from one
        of the sources to the target.

        If neither the source nor target are specified return a dictionary
        of dictionaries with path[source][target]=L, where L is the length
        of the shortest path from source to target.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print(nx.shortest_path_length(G,source=0,target=4))
    4
    >>> p=nx.shortest_path_length(G,source=0) # target not specified
    >>> p[4]
    4
    >>> p=nx.shortest_path_length(G,target=4) # source not specified
    >>> p[0]
    4
    >>> p=nx.shortest_path_length(G) # source,target not specified
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
    single_source_shortest_path_length()
    single_source_dijkstra_path_length()

    """
    if source is None:
        if target is None:
            ## Find paths between all pairs.
            if weight is None:
                paths=nx.all_pairs_shortest_path_length(G)
            else:
                paths=nx.all_pairs_dijkstra_path_length(G, weight=weight)
        else:
            ## Find paths from all nodes co-accessible to the target.
            directed = G.is_directed()
            if directed:
               G.reverse(copy=False)

            if weight is None:
                paths=nx.single_source_shortest_path_length(G,target)
            else:
                paths=nx.single_source_dijkstra_path_length(G,target,
                                                            weight=weight)

            if directed:
                G.reverse(copy=False)
    else:
        if target is None:
            ## Find paths to all nodes accessible from the source.
            if weight is None:
                paths=nx.single_source_shortest_path_length(G,source)
            else:
                paths=nx.single_source_dijkstra_path_length(G,source,weight=weight)
        else:
            ## Find shortest source-target path.
            if weight is None:
                p=nx.bidirectional_shortest_path(G,source,target)
                paths=len(p)-1
            else:
                paths=nx.dijkstra_path_length(G,source,target,weight)
    return paths


def average_shortest_path_length(G, weight=None):
    r"""Return the average shortest path length.

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

    Raises
    ------
    NetworkXError:
       if the graph is not connected.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print(nx.average_shortest_path_length(G))
    2.0

    For disconnected graphs you can compute the average shortest path
    length for each component:
    >>> G=nx.Graph([(1,2),(3,4)])
    >>> for g in nx.connected_component_subgraphs(G):
    ...     print(nx.average_shortest_path_length(g))
    1.0
    1.0

    """
    if G.is_directed():
        if not nx.is_weakly_connected(G):
            raise nx.NetworkXError("Graph is not connected.")
    else:
        if not nx.is_connected(G):
            raise nx.NetworkXError("Graph is not connected.")
    avg=0.0
    if weight is None:
        for node in G:
            path_length=nx.single_source_shortest_path_length(G, node)
            avg += sum(path_length.values())
    else:
        for node in G:
            path_length=nx.single_source_dijkstra_path_length(G, node, weight=weight)
            avg += sum(path_length.values())
    n=len(G)
    return avg/(n*(n-1))


def all_shortest_paths(G, source, target, weight=None):
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

    Returns
    -------
    paths: generator of lists
        A generator of all paths between source and target.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_path([0,1,2])
    >>> G.add_path([0,10,2])
    >>> print([p for p in nx.all_shortest_paths(G,source=0,target=2)])
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
    if weight is not None:
        pred,dist = nx.dijkstra_predecessor_and_distance(G,source,weight=weight)
    else:
        pred = nx.predecessor(G,source)
    if target not in pred:
        raise nx.NetworkXNoPath()
    stack = [[target,0]]
    top = 0
    while top >= 0:
        node,i = stack[top]
        if node == source:
            yield [p for p,n in reversed(stack[:top+1])]
        if len(pred[node]) > i:
            top += 1
            if top == len(stack):
                stack.append([pred[node][i],0])
            else:
                stack[top] = [pred[node][i],0]
        else:
            stack[top-1][1] += 1
            top -= 1
