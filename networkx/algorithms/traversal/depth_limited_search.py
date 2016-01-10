#    Copyright 2016 NetworkX developers.
#    Copyright (C) 2004-2016 by
#    Arafat Dad Khan <arafat.da.khan@gmail.com>
#    All rights reserved.
#    BSD license.
"""
==================
Depth-limited search
==================
Basic algorithms for depth-limited search of a graph.
Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
by D. Eppstein, July 2004.
https://en.wikipedia.org/wiki/Depth-limited search
"""
import networkx as nx
from collections import defaultdict
__all__ = ['dls_edges', 'dls_tree',
           'dls_predecessors', 'dls_successors',
           'dls_preorder_nodes', 'dls_postorder_nodes',
           'dls_labeled_edges']


def dls_edges(G, source=None, search_depth=None):
    """Produce edges in a depth-limited-search (DLS).
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    edges: generator
       A generator of edges in the depth-limited-search.
    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4,5])
    >>> print(list(nx.dls_edges(G,0,3)))
    [(0, 1), (1, 2), (2, 3)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
    """
    if source is None:
        # produce edges for all components
        nodes = G
    else:
        # produce edges for components with source
        nodes = [source]
    visited = set()
    if search_depth is None:
        search_depth = len(G)
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, search_depth, iter(G[start]))]
        while stack:
            parent, depth_now, children = stack[-1]
            if not depth_now >= 1:
                stack.pop()
                continue
            try:
                child = next(children)
                if child not in visited:
                    yield parent, child
                    visited.add(child)
                    stack.append((child, depth_now-1, iter(G[child])))
            except StopIteration:
                stack.pop()


def dls_tree(G, source, search_depth=None):
    """Return oriented tree constructed from a depth-limited-search from source.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    T : NetworkX DiGraph
       An oriented tree
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4,5,6])
    >>> T = nx.dls_tree(G,3,2)
    >>> print(list(T.edges()))
    [(2, 1), (3, 2), (3, 4), (4, 5)]

    """
    T = nx.DiGraph()
    if source is None:
        T.add_nodes_from(G)
    else:
        T.add_node(source)
    T.add_edges_from(dls_edges(G, source, search_depth))
    return T


def dls_predecessors(G, source=None, search_depth=None):
    """Return dictionary of predecessors in depth-limited-search from source.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    pred: dict
       A dictionary with nodes as keys and predecessor nodes as values.
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4,5,6,7])
    >>> print(nx.dls_predecessors(G,5,2))
    {3: 4, 4: 5, 6: 5, 7: 6}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
    """
    return dict((t, s) for s, t in dls_edges(G, source=source,
    search_depth=search_depth))


def dls_successors(G, source=None, search_depth=None):
    """Return dictionary of successors in depth-limited-search from source.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    succ: dict
       A dictionary with nodes as keys and list of successor nodes as values.
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(nx.dls_successors(G,0,3))
    {0: [1], 1: [2]}

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
    """
    d = defaultdict(list)
    for s, t in dls_edges(G, source=source, search_depth=search_depth):
        d[s].append(t)
    return dict(d)


def dls_postorder_nodes(G, source=None, search_depth=None):
    """Produce nodes in a depth-limited-search post-ordering starting
    from source.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-limited-search post-ordering.
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> print(list(nx.dls_postorder_nodes(G,0,4)))
    [2, 1, 0]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
    """
    post = (v for u, v, d in nx.dls_labeled_edges(G,
    source=source, search_depth=search_depth)
          if d['dir'] == 'reverse')
    # potential modification: chain source to end of post-ordering
    # return chain(post,[source])
    return post


def dls_preorder_nodes(G, source=None, search_depth=None):
    """Produce nodes in a depth-limited-search pre-ordering starting
    from source.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    nodes: generator
       A generator of nodes in a depth-limited-search pre-ordering.
    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2,3,4,5,6])
    >>> print(list(nx.dls_preorder_nodes(G,0,2)))
    [0, 1, 2]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
    """
    pre = (v for u, v, d in nx.dls_labeled_edges(G,
    source=source, search_depth=search_depth)
        if d['dir'] == 'forward')
    # potential modification: chain source to beginning of pre-ordering
    # return chain([source],pre)
    return pre


def dls_labeled_edges(G, source=None, search_depth=None):
    """Produce edges in a depth-limited-search  labeled by type.
    Parameters
    ----------
    G : NetworkX graph
    source : node, optional
       Specify starting node for depth-limited search and return edges in
       the component reachable from source.
    search_depth : length, optional
       Specify the maximum search depth.
    Returns
    -------
    edges: generator
       A generator of edges in the depth-limited-search labeled with 'forward',
       'nontree', and 'reverse'.
    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_path([0,1,2])
    >>> edges = (list(nx.dfs_labeled_edges(G,0)))

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    by D. Eppstein, July 2004.
    https://en.wikipedia.org/wiki/Depth-limited_search
    If a source is not specified then a source is chosen arbitrarily and
    repeatedly until all components in the graph are searched.
    If search depth is not specified then it works exactly like
    depth-first search.
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
    if search_depth is None:
        search_depth = len(G)
    for start in nodes:
        if start in visited:
            continue
        yield start, start, {'dir': 'forward'}
        visited.add(start)
        stack = [(start, search_depth, iter(G[start]))]
        while stack:
            parent, depth_now, children = stack[-1]
            if not depth_now >= 1:
                stack.pop()
                continue
            try:
                child = next(children)
                if child in visited:
                    yield parent, child, {'dir': 'nontree'}
                else:
                    yield parent, child, {'dir': 'forward'}
                    visited.add(child)
                    stack.append((child, depth_now-1, iter(G[child])))
            except StopIteration:
                stack.pop()
                if stack:
                    yield stack[-1][0], parent, {'dir': 'reverse'}
        yield start, start, {'dir': 'reverse'}
