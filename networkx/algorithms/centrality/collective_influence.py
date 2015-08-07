# coding=utf8
"""
Collective influence measures.
"""

#   Copyright (C) 2015 by
#   Sebastian Pucilowski <smopucilowski@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as nx
__author__ = "\n".join(['Sebastian Pucilowski <smopucilowski@gmail.com>'])
__all__ = ['collective_influence']

def collective_influence(G, u=None, distance=2):
    r"""Collective influence of a network node.

    The collective influence [1]_ [2]_ of a network node is the product of its
    reduced degree and the total reduced degree of all nodes at distance `d`
    from it.

    .. math::

        \text{CI}_l (i) = (k_i - 1) \sum_{j \in \partial \text{Ball}(i,j)} (k_j - 1)

    Collective influence describes how many nodes can be reached from a given
    node. Removing nodes with high collective influence is more effective in
    fragmenting and destroying a network than nodes selected by other methods
    (e.g. PageRank or closeness centrality).

    Parameters
    ---------
    G : graph
      A NetworkX graph
    u : node, optional
      Return only the value for node u
    distance : optional (default=2)

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with collective influence as the value.

    References
    ----------
      [1] Flaviano Morone and Hernán A. Makse:
      Influence maximization in complex networks through optimal percolation
      Nature 524, 65–68 (06 August 2015)
      doi: 10.1038/nature14604
      [2] István A. Kovács and Albert-László Barabási:
      Network science: Destruction perfected
      Nature 524, 38–39 (06 August 2015)
      doi: 10.1038/524038a
    """

    reduced_degree = lambda node: G.degree(node)-1

    if u is None:
        nodes = G.nodes_iter()
    else:
        nodes = [u]

    collective_influence = dict()
    for node in nodes:
        # Find all nodes at 'distance' steps from node
        paths = nx.single_source_shortest_path(G, source=node, cutoff=distance)
        frontier_nodes = {node for node, path in paths.items()
                          if len(path)-1 == distance}

        collective_influence[node] = reduced_degree(node) * sum(map(reduced_degree, frontier_nodes))

    if u is not None:
        return collective_influence[u]
    else:
        return collective_influence
