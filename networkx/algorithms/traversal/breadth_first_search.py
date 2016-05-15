"""
====================
Breadth-first search
====================

Basic algorithms for breadth-first searching the nodes of a graph.
"""
import networkx as nx
from collections import deque

__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>', 'Matus Cimerman <matus.cimerman@gmail.com>'])
__all__ = ['bfs_edges', 'bfs_tree', 'bfs_predecessors', 'bfs_successors']


def bfs_edges(G, source, reverse=False, depth_limit=float('inf')):
    """Produce edges in a breadth-first-search starting at source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

    reverse : bool, optional
       If True traverse a directed graph in the reverse direction

    depth_limit : integer, optional
       Depth limit where should breadth-first stop exploring graph space.

    Returns
    -------
    edges: generator
       A generator of edges in the breadth-first-search.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.bfs_edges(G,0)))
    [(0, 1), (1, 2)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    if reverse and isinstance(G, nx.DiGraph):
        neighbors = G.predecessors
    else:
        neighbors = G.neighbors
    visited = set([source])
    queue = deque([(source, neighbors(source))])
    time_to_depth_increase = len(queue)
    current_depth = 1
    pending_depth_increase = False
    while queue and current_depth <= depth_limit:
        parent, children = queue[0]
        try:
            child = next(children)
            if child not in visited:
                yield parent, child
                visited.add(child)
                if pending_depth_increase:
                    time_to_depth_increase = len(queue)
                    pending_depth_increase = False
                queue.append((child, neighbors(child)))
        except StopIteration:
            queue.popleft()
            time_to_depth_increase -= 1
            if time_to_depth_increase == 0:
                current_depth += 1
                pending_depth_increase = True


def bfs_tree(G, source, reverse=False, depth_limit=float('inf')):
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

    Returns
    -------
    T: NetworkX DiGraph
       An oriented tree

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> print(list(nx.bfs_edges(G,0)))
    [(0, 1), (1, 2)]

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    T = nx.DiGraph()
    T.add_node(source)
    T.add_edges_from(bfs_edges(G, source, reverse=reverse, depth_limit=depth_limit))
    return T


def bfs_predecessors(G, source, depth_limit=float('inf')):
    """Returns an iterator of predecessors in breadth-first-search from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for breadth-first search and return edges in
       the component reachable from source.

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

    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    for s, t in bfs_edges(G, source, depth_limit=depth_limit):
        yield (t, s)


def bfs_successors(G, source, depth_limit=float('inf')):
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


    Notes
    -----
    Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    by D. Eppstein, July 2004.
    """
    parent = source
    children = []
    for p, c in bfs_edges(G, source, depth_limit=depth_limit):
        if p == parent:
            children.append(c)
            continue
        yield (parent, children)
        children = [c]
        parent = p
    yield (parent, children)
