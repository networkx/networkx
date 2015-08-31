# -*- coding: utf-8 -*-
import networkx as nx
__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])
__all__ = [ 'dominating_set', 'is_dominating_set']

def dominating_set(G, start_with=None):
    r"""Finds a dominating set for the graph G.

    A dominating set for a graph `G = (V, E)` is a node subset `D` of `V`
    such that every node not in `D` is adjacent to at least one member
    of `D` [1]_.

    Parameters
    ----------

    G : NetworkX graph

    start_with : Node (default=None)
        Node to use as a starting point for the algorithm.

    Returns
    -------
    D : set
        A dominating set for G.

    Notes
    -----
    This function is an implementation of algorithm 7 in [2]_ which
    finds some dominating set, not necessarily the smallest one.

    See also
    --------
    is_dominating_set

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Dominating_set

    .. [2] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    all_nodes = set(G)
    if start_with is None:
        v = set(G).pop() # pick a node
    else:
        if start_with not in G:
            raise nx.NetworkXError('node %s not in G' % start_with)
        v = start_with
    D = set([v])
    ND = set(G[v])
    other = all_nodes - ND - D
    while other:
        w = other.pop()
        D.add(w)
        ND.update([nbr for nbr in G[w] if nbr not in D])
        other = all_nodes - ND - D
    return D

def is_dominating_set(G, nbunch):
    r"""Checks if nodes in nbunch are a dominating set for G.

    A dominating set for a graph `G = (V, E)` is a node subset `D` of `V`
    such that every node not in `D` is adjacent to at least one member
    of `D` [1]_.

    Parameters
    ----------

    G : NetworkX graph

    nbunch : Node container

    See also
    --------
    dominating_set

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Dominating_set

    """
    testset = set(n for n in nbunch if n in G)
    nbrs = set()
    for n in testset:
        nbrs.update(G[n])
    if len(set(G) - testset - nbrs) > 0:
        return False
    else:
        return True
