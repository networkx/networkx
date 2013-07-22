# encoding: utf-8
"""
Functions for finding bridges (or cut-edges) of a graph.

Created by Peng Yu <pengyu.ut@gmail.com>
and Christoph Siedentop <christoph@siedentop.name>.
Copyright (c) 2013. All rights reserved.
BSD License.
"""
__author__ = """\n""".join(['Christoph Siedentop <christoph@siedentop.name>',
                            'Peng Yu <pengyu.ut@gmail.com>'])
__all__=['bridges']

import networkx as nx
from collections import defaultdict

def bridges(G):
    """Returns the bridges of an undirected graph.

    Bridges, also called cut-edges, are edges in a graph that when cut would
    make the graph unconnected. More formally: "An edge e in a graph is said
    to be a bridge if there exist vertices u and v such that all paths from u
    to v pass through e" [1].

    The classic algorithm for this is [Tarjan 1974][1]. This algorithm is based
    on WGB-DFS.

    Parameters
    ----------
    G : graph
        An undirected networkx Graph.

    Returns
    -------
    bridges : an iterator of edges
    
    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_edge(1, 2)
    >>> list(bridges(G))
    [(1, 2)]

    References
    ----------
    .. [1] R.Endre Tarjan, A note on finding the bridges of a graph,
    Information Processing Letters, Volume 2, Issue 6, April 1974,
    Pages 160-161, ISSN 0020-0190, http://dx.doi.org/10.1016/0020-0190(74)90003-9.
    (http://www.sciencedirect.com/science/article/pii/0020019074900039)

    """
    if G.is_directed():
        raise nx.NetworkXError('This function is for undirected graphs.\n'
                               'Use directed_wgb_dfs() for directed graphs.')

    class WhiteGrayBlackDFS:
        def __init__(self, G):
            # white: empty
            # gray: 1
            # black: 2

            self.visited = set()
            self.dfs_num = {}
            self.num = 0
            self.G = G
            self.back_edges = defaultdict(set)

        def bridges(self, parent, current):
            #print '{'
            #print 'parent, current:', parent, current
            #print 'dfs_num:', self.dfs_num
            self.visited.add(current)
            current_lowpoint = self.dfs_num[current] = self.num

            self.num += 1
            #print 'dfs_num:', self.dfs_num

            for child in G.neighbors(current):
                if child != parent:
                    #print 'current, child:', current, child
                    if not current in self.back_edges or (current in self.back_edges and not child in self.back_edges[current]):
                        if child in self.visited:
                            current_lowpoint = min(current_lowpoint, self.dfs_num[child])
                        else:
                            for x in self.bridges(current, child):
                                yield x
                            if self.child_lowpoint > self.dfs_num[current]:
                                #print '>>> bridge:', current, child
                                yield (current, child)
                            current_lowpoint = min(current_lowpoint, self.child_lowpoint)

            #print 'parent, current, current_lowpoint:', parent, current, current_lowpoint
            #print 'dfs_num:', self.dfs_num
            #print '}'
            self.child_lowpoint = current_lowpoint


    dfs = WhiteGrayBlackDFS(G)

    if G.is_multigraph(): # Need to check for parallel edges.
        for x in G:
            if not x in dfs.visited:
                for e in dfs.bridges(x, x):
                    if len(G[e[0]][e[1]]) == 1:
                        yield e
    else:
        for x in G:
            if not x in dfs.visited:
                #print x
                for e in dfs.bridges(x, x):
                    yield e
