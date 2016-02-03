"""
==================
Depth-first search
==================

Basic algorithms for depth-first search and depth-limited search of a graph.

The implementation of this function is adapted from David Eppstein's
depth-first search function in `PADS`_, with modifications to allow depth
limits based on the Wikipedia article "`Depth-limited search`_".

.. _PADS: http://www.ics.uci.edu/~eppstein/PADS
.. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
"""
import networkx as nx
from collections import defaultdict
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['dfs_edges', 'dfs_tree',
           'dfs_predecessors', 'dfs_successors',
           'dfs_preorder_nodes', 'dfs_postorder_nodes',
           'dfs_labeled_edges']


def dfs_edges(G, source=None, depth_limit=None):
    """Produce edges in a depth-first-search (DFS).

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    edges: generator
       A generator of edges in the depth-first-search.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4])
    >>> list(nx.dfs_edges(G,0))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    >>> list(nx.dfs_edges(G,0,2))
    [(0, 1), (1, 2)]

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited = set()
    if depth_limit is None:
       depth_limit = len(G)
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, depth_limit, iter(G[start]))]
        while stack:
            parent, depth_now, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    yield parent, child
                    visited.add(child)
                    if depth_now > 1:
                        stack.append((child, depth_now-1, iter(G[child])))
            except StopIteration:
                stack.pop()


def dfs_tree(G, source, depth_limit=None):
    """Return oriented tree constructed from a depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    T : NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4])
    >>> T = nx.dfs_tree(G,0,2)
    >>> list(T.edges())
    [(0, 1), (1, 2)]

    >>> T = nx.dfs_tree(G,0)
    >>> list(T.edges())
    [(0, 1), (1, 2), (2, 3), (3, 4)]
    """
    T = nx.DiGraph()
    if source is None:
        T.add_nodes_from(G)
    else:
        T.add_node(source)
    T.add_edges_from(dfs_edges(G, source, depth_limit))
    return T


def dfs_predecessors(G, source=None, depth_limit=None):
    """Return dictionary of predecessors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    pred: dict
       A dictionary with nodes as keys and predecessor nodes as values.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3])
    >>> nx.dfs_predecessors(G,0)
    {1: 0, 2: 1, 3: 2}

    >>> nx.dfs_predecessors(G,0,2)
    {1: 0, 2: 1}

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    return {t: s for s, t in dfs_edges(G, source, depth_limit)}


def dfs_successors(G, source=None, depth_limit=None):
    """Return dictionary of successors in depth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    succ: dict
       A dictionary with nodes as keys and list of successor nodes as values.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4])
    >>> nx.dfs_successors(G,0)
    {0: [1], 1: [2], 2: [3], 3: [4]}

    >>> nx.dfs_successors(G,0,2)
    {0: [1], 1: [2]}

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    d = defaultdict(list)
    for s, t in dfs_edges(G, source=source, depth_limit=depth_limit):
        d[s].append(t)
    return dict(d)


def dfs_postorder_nodes(G, source=None, depth_limit=None):
    """Produce nodes in a depth-first-search post-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search post-ordering.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4])
    >>> list(nx.dfs_postorder_nodes(G,0))
    [4, 3, 2, 1, 0]

    >>> list(nx.dfs_postorder_nodes(G,0,2))
    [1, 0]

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    edges = nx.dfs_labeled_edges(G, source=source, depth_limit=depth_limit)
    return (v for u, v, d in edges if d['dir'] == 'reverse')


def dfs_preorder_nodes(G, source=None, depth_limit=None):
    """Produce nodes in a depth-first-search pre-ordering starting
    from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-first-search pre-ordering.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0, 1, 2, 3, 4])
    >>> list(nx.dfs_preorder_nodes(G,0))
    [0, 1, 2, 3, 4]

    >>> list(nx.dfs_preorder_nodes(G,0,2))
    [0, 1, 2]

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
    """
    edges = nx.dfs_labeled_edges(G, source=source, depth_limit=depth_limit)
    return (v for u, v, d in edges if d['dir'] == 'forward')


def dfs_labeled_edges(G, source=None, depth_limit=None):
    """Produce edges in a depth-first-search (DFS) labeled by type.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Specify starting node for depth-first search and return edges in
       the component reachable from source.

    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth.

    Returns
    -------
    edges: generator
       A generator of edges in the depth-first-search labeled with 'forward',
       'nontree', and 'reverse'.
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> edges = list(nx.dfs_labeled_edges(G,0))

    Notes
    -----
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.

    The implementation of this function is adapted from David Eppstein's
    depth-first search function in `PADS`_, with modifications
    to allow depth limits based on the Wikipedia article
    "`Depth-limited search`_".

    .. _PADS: http://www.ics.uci.edu/~eppstein/PADS
    .. _Depth-limited search: https://en.wikipedia.org/wiki/Depth-limited_search
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
    if depth_limit is None:
       depth_limit = len(G)
    for start in nodes:
        if start in visited:
            continue
        yield start, start, {'dir': 'forward'}
        visited.add(start)
        stack = [(start, depth_limit, iter(G[start]))]
        while stack:
            parent, depth_now, children = stack[-1]
            try:
                child = next(children)
                if child in visited:
                    yield parent, child, {'dir': 'nontree'}
                else:
                    yield parent, child, {'dir': 'forward'}
                    visited.add(child)
                    if depth_now > 1:
                        stack.append((child, depth_now-1, iter(G[child])))
            except StopIteration:
                stack.pop()
                if stack:
                    yield stack[-1][0], parent, {'dir': 'reverse'}
        yield start, start, {'dir': 'reverse'}
