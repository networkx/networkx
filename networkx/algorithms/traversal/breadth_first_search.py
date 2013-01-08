"""
====================
Breadth-first search
====================

Basic algorithms for breadth-first searching.
"""
__author__ = """\n""".join(['Aric Hagberg <hagberg@lanl.gov>'])

__all__ = ['bfs_edges', 'bfs_tree',
           'bfs_predecessors', 'bfs_successors']

import networkx as nx
from collections import defaultdict, deque

def bfs_edges(G, source, reverse=False):
    """Produce edges in a breadth-first-search starting at source."""
    # Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    # by D. Eppstein, July 2004.
    if reverse and isinstance(G, nx.DiGraph):
        neighbors = G.predecessors_iter
    else:
        neighbors = G.neighbors_iter
    visited=set([source])
    queue = deque([(source, neighbors(source))])
    while queue:
        parent, children = queue[0]
        try:
            child = next(children)
            if child not in visited:
                yield parent, child
                visited.add(child)
                queue.append((child, neighbors(child)))
        except StopIteration:
            queue.popleft()

def bfs_tree(G, source, reverse=False):
    """Return directed tree of breadth-first-search from source."""
    T = nx.DiGraph()
    T.add_node(source)
    T.add_edges_from(bfs_edges(G,source,reverse=reverse))
    return T

def bfs_predecessors(G, source):
    """Return dictionary of predecessors in breadth-first-search from source."""
    return dict((t,s) for s,t in bfs_edges(G,source))

def bfs_successors(G, source):
    """Return dictionary of successors in breadth-first-search from source."""
    d=defaultdict(list)
    for s,t in bfs_edges(G,source):
        d[s].append(t)
    return dict(d)
