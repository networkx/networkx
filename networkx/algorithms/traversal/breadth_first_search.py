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
from collections import defaultdict

def bfs_edges(G,source):
    """Produce edges in a breadth-first-search starting at source."""
    # Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
    # by D. Eppstein, July 2004.
    visited=set([source])
    stack = [(source,iter(G[source]))]
    while stack:
        parent,children = stack[0]
        try:
            child = next(children)
            if child not in visited:
                yield parent,child
                visited.add(child)
                stack.append((child,iter(G[child])))
        except StopIteration:
            stack.pop(0)


def bfs_tree(G, source):
    """Return directed tree of breadth-first-search from source."""
    return nx.DiGraph(bfs_edges(G,source))


def bfs_predecessors(G, source):
    """Return dictionary of predecessors in breadth-first-search from source."""
    return dict((t,s) for s,t in bfs_edges(G,source))


def bfs_successors(G, source):
    """Return dictionary of successors in breadth-first-search from source."""
    d=defaultdict(list)
    for s,t in bfs_edges(G,source):
        d[s].append(t)
    return dict(d)



