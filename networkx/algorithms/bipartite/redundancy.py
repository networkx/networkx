#-*- coding: utf-8 -*-
"""Node redundancy for bipartite graphs."""
#    Copyright (C) 2011 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
from itertools import combinations
import networkx as nx

__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>',
                            'Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ['node_redundancy']

def node_redundancy(G, nodes=None):
    r"""Compute bipartite node redundancy coefficient.

    The redundancy coefficient of a node `v` is the fraction of pairs of 
    neighbors of `v` that are both linked to other nodes. In a one-mode
    projection these nodes would be linked together even if `v`  were 
    not there.
    
    .. math::

        rc(v) = \frac{|\{\{u,w\} \subseteq N(v),
        \: \exists v' \neq  v,\: (v',u) \in E\: 
        \mathrm{and}\: (v',w) \in E\}|}{ \frac{|N(v)|(|N(v)|-1)}{2}}

    where `N(v)` are the neighbors of `v` in `G`.

    Parameters
    ----------
    G : graph
        A bipartite graph

    nodes : list or iterable (optional)
        Compute redundancy for these nodes. The default is all nodes in G.

    Returns
    -------
    redundancy : dictionary
        A dictionary keyed by node with the node redundancy value.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.cycle_graph(4)
    >>> rc = bipartite.node_redundancy(G)
    >>> rc[0]
    1.0

    Compute the average redundancy for the graph:

    >>> sum(rc.values())/len(G)
    1.0

    Compute the average redundancy for a set of nodes:

    >>> nodes = [0, 2]
    >>> sum(rc[n] for n in nodes)/len(nodes)
    1.0

    References
    ----------
    .. [1] Latapy, Matthieu, Clémence Magnien, and Nathalie Del Vecchio (2008).
       Basic notions for the analysis of large two-mode networks. 
       Social Networks 30(1), 31--48.
    """
    if nodes is None:
        nodes = G
    rc = {}
    for v in nodes:
        overlap = 0.0
        for u, w in combinations(G[v], 2):
            if len((set(G[u]) & set(G[w])) - set([v])) > 0:
                overlap += 1
        if overlap > 0:
            n = len(G[v])
            norm = 2.0/(n*(n-1))
        else:
            norm = 1.0
        rc[v] = overlap*norm
    return rc

