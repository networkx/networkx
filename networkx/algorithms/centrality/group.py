# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Nanda H Krishna <nanda.harishankar@gmail.com>
#    All rights reserved.
#    BSD license.
#
"""Group centrality measures."""
from itertools import combinations


import networkx as nx


__all__ = ['group_betweenness_centrality']


def group_betweenness_centrality(G, C, normalized=True, weight=None):
    r"""Compute the group betweenness centrality for a group of nodes.

    Group betweenness centrality of a group of nodes $C$ is the sum of the
    fraction of all-pairs shortest paths that pass through any vertex in $C$

    .. math::

    c_B(C) =\sum_{s,t \in V-C; s<t} \frac{\sigma(s, t|C)}{\sigma(s, t)}

    where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
    shortest $(s, t)$-paths, and $\sigma(s, t|C)$ is the number of
    those paths passing through some node in group $C$. Note that
    $(s, t)$ are not members of the group ($V-C$ is the set of nodes
    in $V$ that are not in $C$).

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    C : list or set
      C is a group of nodes which belong to G, for which group betweenness
      centrality is to be calculated.

    normalized : bool, optional
      If True, group betweenness is normalized by `2/((|V|-|C|)(|V|-|C|-1))`
      for graphs and `1/((|V|-|C|)(|V|-|C|-1))` for directed graphs where `|V|`
      is the number of nodes in G and `|C|` is the number of nodes in C.

    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    betweenness : float
       Group betweenness centrality of the group C.

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    The measure is described in [1]_.
    The algorithm is an extension of the one proposed by Ulrik Brandes for
    betweenness centrality of nodes. Group betweenness is also mentioned in
    his paper [2]_ along with the algorithm. The importance of the measure is
    discussed in [3]_.

    The number of nodes in the group must be a maximum of n - 2 where `n`
    is the total number of nodes in the graph.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length
    paths between pairs of nodes.

    References
    ----------
    .. [1] M G Everett and S P Borgatti:
       The Centrality of Groups and Classes.
       Journal of Mathematical Sociology. 23(3): 181-201. 1999.
       http://www.analytictech.com/borgatti/group_centrality.htm
    .. [2] Ulrik Brandes:
       On Variants of Shortest-Path Betweenness
       Centrality and their Generic Computation.
       Social Networks 30(2):136-145, 2008.
       http://www.inf.uni-konstanz.de/algo/publications/b-vspbc-08.pdf
    .. [3] Sourav Medya et. al.:
       Group Centrality Maximization via Network Design.
       SIAM International Conference on Data Mining, SDM 2018, 126–134.
       https://sites.cs.ucsb.edu/~arlei/pubs/sdm18.pdf

    """
    betweenness = 0  # initialize betweenness to 0
    V = set(G.nodes())  # set of nodes in G
    C = set(C)  # set of nodes in C (group)
    V_C = set(V - C)  # set of nodes in V but not in C
    # accumulation
    for pair in combinations(V_C, 2):  # (s, t) pairs of V_C
        try:
            paths = 0
            paths_through_C = 0
            for path in nx.all_shortest_paths(G, source=pair[0],
                                              target=pair[1], weight=weight):
                if set(path) & C:
                    paths_through_C += 1
                paths += 1
            betweenness += paths_through_C / paths
        except nx.exception.NetworkXNoPath:
            betweenness += 0
    # rescaling
    v, c = len(G), len(C)
    if normalized:
        scale = 1 / ((v - c) * (v - c - 1))
        if not G.is_directed():
            scale *= 2
    else:
        scale = None
    if scale is not None:
        betweenness *= scale
    return betweenness
