# -*- coding: utf-8 -*-
#    Copyright (C) 2012 by
#    Sergio Nery Simoes <sergionery@gmail.com>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Sérgio Nery Simões <sergionery@gmail.com>'])
__all__ = ['all_simple_paths']

def all_simple_paths(G, source, target, cutoff=None):
    """Genereate all simple paths in the graph G from source to target.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path.

    target : node
       Ending node for path.

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> for path in nx.all_simple_paths(G,source=0,target=4):
    ...    print(path)
    [0, 1, 2, 3, 4]

    Notes
    -----
    This algorithm uses a modified depth-first search to generate the
    paths [1]_.  A single path can be found in `O(V+E)` time but the
    number of simple paths in a graph can be very large, e.g. `O(n!)` in
    the complete graph of order n.

    References
    ----------
    .. [1] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
       Addison Wesley Professional, 3rd ed., 2001.

    See Also
    --------
    shortest_path
    """
    if G.is_multigraph():
        def neighbors(G,n):
            return (v for u,v in G.edges(n))
    else:
        def neighbors(G,n):
            return iter(G[n])
    if cutoff is None:
        cutoff = len(G)-1
    visited = [source]
    stack = [neighbors(G,source)]
    while stack:
        children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            visited.pop()
        elif len(visited) <= cutoff:
            if child == target:
                yield visited + [target]
            elif child not in visited:
                visited.append(child)
                stack.append(neighbors(G,child))
