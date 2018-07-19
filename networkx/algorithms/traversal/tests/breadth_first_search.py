# breadth_first_search.py - breadth-first traversal of a graph
#
# Copyright (C) 2004-2018 NetworkX Developers
#   Aric Hagberg <hagberg@lanl.gov>
#   Dan Schult <dschult@colgate.edu>
#   Pieter Swart <swart@lanl.gov>
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
# Authors:
#     Aric Hagberg <aric.hagberg@gmail.com>
#
"""Basic algorithms for breadth-first searching the nodes of a graph."""
import networkx as nx
from collections import deque

__all__ = ['bfs_edges', 'bfs_tree', 'bfs_predecessors', 'bfs_successors']


def generic_bfs_edges(G, source, neighbors=None, depth_limit = None):
    """Iterate over edges in a breadth-first search.

    The breadth-first search begins at `source` and enqueues the
    neighbors of newly visited nodes specified by the `neighbors`
    function.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node for the breadth-first search; this function
        iterates over only those edges in the component reachable from
        this node.

    neighbors : function
        A function that takes a newly visited node of the graph as input
        and returns an *iterator* (not just a list) of nodes that are
        neighbors of that node. If not specified, this is just the
        ``G.neighbors`` method, but in general it can be any function
        that returns an iterator over some or all of the neighbors of a
        given node, in any order.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.
       
    Yields
    ------
    edge
        Edges in the breadth-first search starting from `source`.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.bfs_edges(G,0)))
    [(0, 1), (1, 2)]

    >>> from breadth_first_search import bfs_edges 
    >>> G = nx.path_graph(3)
    >>> print(list(bfs_edges(G, 0, G.neighbors, depth_limit = 1)))
    [(0, 1)]
    >>> print(list(bfs_edges(G, 0, G.neighbors, depth_limit = 2)))
    [(0, 1), (1, 2)]
    >>> print(list(bfs_edges(G, 0, G.neighbors, depth_limit = 3)))
    [(0, 1), (1, 2)]
    >>> print(list(bfs_edges(G, 0, G.neighbors, depth_limit = 0)))
    []
    
    Notes
    -----
    This implementation is from `PADS`_, which was in the public domain
    when it was first accessed in July, 2004.

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS/BFS.py

    """
    if depth_limit is None:
        depth_limit = len(G)
    depth = 0
    visited = {source}
    queue = deque([(source, neighbors(source))])
    while queue:
        parent, children = queue[0]
        step = list(neighbors(source))
        if step[-1] == parent:
            depth += 1
        if depth >= depth_limit:
            return
        try:
            while True:
                child = next(children)
                if child not in visited:
                    yield parent, child
                    visited.add(child)
                    queue.append((child, neighbors(child)))
        except StopIteration:
            queue.popleft()
     
    


def bfs_edges(G, source, reverse=False, depth_limit = None):
    """Iterate over edges in a breadth-first-search starting at source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

    reverse : bool, optional
       If True traverse a directed graph in the reverse direction

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.
    
    Returns
    -------
    edges: generator
       A generator of edges in the breadth-first-search.

    Examples
    --------
    To get the edges in a breadth-first search::

        >>> G = nx.path_graph(3)
        >>> list(nx.bfs_edges(G, 0))
        [(0, 1), (1, 2)]
        >>> from breadth_first_search import bfs_edges 
        >>> G = nx.path_graph(3)
        >>> print(list(bfs_edges(G, 0, G.neighbors, depth_limit = 1)))
        [(0, 1)]

    To get the nodes in a breadth-first search order::

        >>> G = nx.path_graph(3)
        >>> root = 2
        >>> edges = nx.bfs_edges(G, root)
        >>> nodes = [root] + [v for u, v in edges]
        >>> nodes
        [2, 1, 0]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    if reverse and G.is_directed():
        successors = G.predecessors
    else:
        successors = G.neighbors
    # TODO In Python 3.3+, this should be `yield from ...`
    for e in generic_bfs_edges(G, source, successors, depth_limit):
        yield e


def bfs_tree(G, source, reverse=False, depth_limit = None):
    """Return an oriented tree constructed from of a breadth-first-search
    starting at source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

    reverse : bool, optional
       If True traverse a directed graph in the reverse direction

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.
    
    Returns
    -------
    T: NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.bfs_tree(G,1).edges()))
    [(1, 0), (1, 2)]
    >>> from breadth_first_search.py import bfs_tree
    >>> G = nx.path_graph(3)
    >>> print(list(bfs_tree(G, 0, depth_limit = 2).edges()))
    [(0, 1), (1, 2)]
    >>> print(list(bfs_tree(G, 0, depth_limit = 1).edges()))
    [(0, 1)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    if depth_limit is None:
        depth_limit = len(G)
    T = nx.DiGraph()
    T.add_node(source)
    T.add_edges_from(bfs_edges(G, source, reverse=reverse, depth_limit= depth_limit))
    return T


def bfs_predecessors(G, source, depth_limit = None):
    """Returns an iterator of predecessors in breadth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    pred: iterator
        (node, predecessors) iterator where predecessors is the list of
        predecessors of the node.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(dict(nx.bfs_predecessors(G, 0)))
    {1: 0, 2: 1}
    >>> H = nx.Graph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> dict(nx.bfs_predecessors(H, 0))
    {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}

    >>> from breadth_first_search import bfs_predecessors
    >>> G = nx.path_graph(3)
    >>> print(dict(bfs_predecessors(G, source = 0, depth_limit= 1)))
    {1: 0}
    >>> print(dict(dict(bfs_predecessors(H, 0, depth_limit= 1))))
    {1: 0, 2: 0, 3: 1, 4: 1}
    >>> print(dict(dict(bfs_predecessors(H, 0, depth_limit= 2))))
    {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    if depth_limit is None:
        depth_limit = len(G)
    for s, t in bfs_edges(G, source, depth_limit= depth_limit):
        yield (t, s)


def bfs_successors(G, source, depth_limit = None):
    """Returns an iterator of successors in breadth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

    Returns
    -------
    succ: iterator
       (node, successors) iterator where successors is the list of
       successors of the node.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(dict(nx.bfs_successors(G,0)))
    {0: [1], 1: [2]}
    >>> H = nx.Graph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> dict(nx.bfs_successors(H, 0))
    {0: [1, 2], 1: [3, 4], 2: [5, 6]}

    >>> from breadth_first_search import bfs_successors
    >>> G = nx.path_graph(3)
    >>> print(dict(bfs_successors(G, source = 0, depth_limit= 1)))
    {0: [1]}
    >>> print(dict(dict(bfs_successors(H, 0, depth_limit= 1))))
    {0: [1, 2], 1: [3, 4]}
    >>> print(dict(dict(bfs_successors(H, 0, depth_limit= 2))))
    {0: [1, 2], 1: [3, 4], 2: [5, 6]}
    
    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    if depth_limit is None:
        depth_limit = len(G)

    parent = source
    children = []
    for p, c in bfs_edges(G, source, depth_limit= depth_limit):
        if p == parent:
            children.append(c)
            continue
        yield (parent, children)
        children = [c]
        parent = p
    yield (parent, children)
