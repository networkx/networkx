# -*- coding: utf-8 -*-
import networkx as nx
__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])
__all__ = [ 'dominating_set', 'is_dominating_set']

def dominating_set(G, start_with=None):
    # Algorithm 7 in [1]
    all_nodes = set(G)
    if start_with is None:
        v = set(G).pop() # pick a node
    else:
        if start_with not in G:
            raise nx.NetworkXError('node %s not in G' % start_with)
        v = start_with
    D = set([v])
    ND = set([nbr for nbr in G[v]])
    other = all_nodes - ND - D
    while other:
        w = other.pop()
        D.add(w)
        ND.update([nbr for nbr in G[w] if nbr not in D])
        other = all_nodes - ND - D
    return D

def is_dominating_set(G, nbunch):
    # Proposed by Dan on the mailing list
    testset = set(n for n in nbunch if n in G)
    nbrs = set()
    for n in testset:
        nbrs.update(G[n])
    if len(set(G) - testset - nbrs) > 0:
        return False
    else:
        return True
