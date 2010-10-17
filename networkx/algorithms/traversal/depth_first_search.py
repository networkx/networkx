"""
==================
Depth-first search 
==================

Basic algorithms for depth-first searching.

Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
by D. Eppstein, July 2004.
"""
__author__ = """\n""".join(['Aric Hagberg <hagberg@lanl.gov>'])

__all__ = ['dfs_edges', 'dfs_tree',
           'dfs_predecessors', 'dfs_successors',
           'dfs_preorder_nodes','dfs_postorder_nodes',
           'dfs_labeled_edges']

import networkx as nx
from collections import defaultdict
from itertools import chain

def dfs_edges(G,source):
    """Produce edges in a depth-first-search starting at source."""
    # Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    # by D. Eppstein, July 2004.
    visited=set([source])
    stack = [(source,iter(G[source]))]
    while stack:
        parent,children = stack[-1]
        try:
            child = children.next()
            if child not in visited:
                yield parent,child
                visited.add(child)
                stack.append((child,iter(G[child])))
        except StopIteration:
            stack.pop()


def dfs_tree(G, source):
    """Return directed tree of depth-first-search from source."""
    return nx.DiGraph(dfs_edges(G,source))


def dfs_predecessors(G, source):
    """Return dictionary of predecessors in depth-first-search from source."""
    return dict((t,s) for s,t in dfs_edges(G,source))


def dfs_successors(G, source):
    """Return dictionary of successors in depth-first-search from source."""
    d=defaultdict(list)
    for s,t in dfs_edges(G,source):
        d[s].append(t)
    return dict(d)


def dfs_postorder_nodes(G,source):
    """Produce nodes in a depth-first-search post-ordering starting 
    from source.
    """
    post=(v for u,v,d in nx.dfs_labeled_edges(G,source) if d['dir']=='reverse')
    # chain source to end of pre-ordering
    return chain(post,[source])


def dfs_preorder_nodes(G,source):
    """Produce nodes in a depth-first-search pre-ordering starting at source."""
    pre=(v for u,v,d in nx.dfs_labeled_edges(G,source) if d['dir']=='forward')
    # chain source to beginning of pre-ordering
    return chain([source],pre)


def dfs_labeled_edges(G,source):
    """Produce edges in a depth-first-search starting at source and
    labeled by direction type (forward, reverse, nontree).
    """
    # Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
    # by D. Eppstein, July 2004.
    visited=set([source])
    stack = [(source,iter(G[source]))]
    while stack:
        parent,children = stack[-1]
        try:
            child = children.next()
            if child in visited:
                yield parent,child,{'dir':'nontree'}
            else:
                yield parent,child,{'dir':'forward'}
                visited.add(child)
                stack.append((child,iter(G[child])))
        except StopIteration:
            stack.pop()
            if stack:
                yield stack[-1][0],parent,{'dir':'reverse'}

