# depth_first_search.py - depth-first traversals of a graph
#
# Copyright 2004-2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
# Author:
#   Aric Hagberg <aric.hagberg@gmail.com>
"""
Basic algorithms for depth-first searching the nodes of a graph.

Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
by D. Eppstein, July 2004.
"""
import networkx as nx
from collections import defaultdict

__all__ = ['dfs_edges', 'dfs_tree',
           'dfs_predecessors', 'dfs_successors',
           'dfs_preorder_nodes','dfs_postorder_nodes',
           'dfs_labeled_edges']

def dfs_edges(G, source=None):
    """Produce edges in a depth-first-search (DFS).

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    edges: generator
       A generator of edges in the depth-first-search.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.dfs_edges(G,0)))
    [(0, 1), (1, 2)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited=set()
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start,iter(G[start]))]
        while stack:
            parent,children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    yield parent,child
                    visited.add(child)
                    stack.append((child,iter(G[child])))
            except StopIteration:
                stack.pop()

def dfs_tree(G, source=None):
    """Return oriented tree constructed from a depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search.

    Returns
    -------
    T : NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> T = nx.dfs_tree(G,0)
    >>> print(list(T.edges()))
    [(0, 1), (1, 2)]
    """
    T = nx.DiGraph()
    if source is None:
        T.add_nodes_from(G)
    else:
        T.add_node(source)
    T.add_edges_from(dfs_edges(G,source))
    return T

def dfs_predecessors(G, source=None):
    """Return dictionary of predecessors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    pred: dict
       A dictionary with nodes as keys and predecessor nodes as values.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(nx.dfs_predecessors(G,0))
    {1: 0, 2: 1}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    return dict((t,s) for s,t in dfs_edges(G,source=source))


def dfs_successors(G, source=None):
    """Return dictionary of successors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    succ: dict
       A dictionary with nodes as keys and list of successor nodes as values.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(nx.dfs_successors(G,0))
    {0: [1], 1: [2]}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    d = defaultdict(list)
    for s,t in dfs_edges(G,source=source):
        d[s].append(t)
    return dict(d)


def dfs_postorder_nodes(G,source=None):
    """Produce nodes in a depth-first-search post-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search post-ordering.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.dfs_postorder_nodes(G,0)))
    [2, 1, 0]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    post = (v for u, v, d in nx.dfs_labeled_edges(G, source=source)
            if d == 'reverse')
    # potential modification: chain source to end of post-ordering
    # return chain(post,[source])
    return post


def dfs_preorder_nodes(G, source=None):
    """Produce nodes in a depth-first-search pre-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search pre-ordering.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.dfs_preorder_nodes(G,0)))
    [0, 1, 2]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    """
    pre = (v for u, v, d in nx.dfs_labeled_edges(G, source=source)
           if d == 'forward')
    # potential modification: chain source to beginning of pre-ordering
    # return chain([source],pre)
    return pre


def dfs_labeled_edges(G, source=None):
    """Produce edges in a depth-first-search (DFS) labeled by type.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    edges: generator
       A generator of triples of the form (*u*, *v*, *d*), where (*u*,
       *v*) is the edge being explored in the depth-first search and *d*
       is one of the strings 'forward', 'nontree', or 'reverse'. A
       'forward' edge is one in which *u* has been visited but *v* has
       not. A 'nontree' edge is one in which both *u* and *v* have been
       visited but the edge is not in the DFS tree. A 'reverse' edge is
       on in which both *u* and *v* have been visited and the edge is in
       the DFS tree.

    Examples
    --------

    The labels reveal the complete transcript of the depth-first search
    algorithm in more detail than, for example, :func:`dfs_edges`::

        >>> from pprint import pprint
        >>>
        >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 1)])
        >>> pprint(list(nx.dfs_labeled_edges(G, source=0)))
        [(0, 0, 'forward'),
         (0, 1, 'forward'),
         (1, 2, 'forward'),
         (2, 1, 'nontree'),
         (1, 2, 'reverse'),
         (0, 1, 'reverse'),
         (0, 0, 'reverse')]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.

    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    """
    # Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    # by D. Eppstein, July 2004.
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited = set()
    for start in nodes:
        if start in visited:
            continue
        yield start, start, 'forward'
        visited.add(start)
        stack = [(start,iter(G[start]))]
        while stack:
            parent,children = stack[-1]
            try:
                child = next(children)
                if child in visited:
                    yield parent, child, 'nontree'
                else:
                    yield parent, child, 'forward'
                    visited.add(child)
                    stack.append((child,iter(G[child])))
            except StopIteration:
                stack.pop()
                if stack:
                    yield stack[-1][0], parent, 'reverse'
        yield start, start, 'reverse'
