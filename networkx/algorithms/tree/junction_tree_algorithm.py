# -*- coding: utf-8 -*-
#   Copyright (C) 2020 by
#   Matthias Bruhns <matthias.bruhns@uni-jena.de>
#   All rights reserved.
#   BSD license.
#   Copyright 2016-2020 NetworkX developers.
#   NetworkX is distributed under a BSD license
#
# Authors: Matthias Bruhns <matthias.bruhns@uni-jena.de>
r"""Function for computing a junction tree of a graph."""

import networkx as nx
from networkx.utils import not_implemented_for
from networkx.algorithms import moral, complete_to_chordal_graph, chordal_graph_cliques
import matplotlib.pyplot as plt
from itertools import combinations

__all__ = ['junction_tree']


@not_implemented_for('multigraph', 'MultiDiGraph')
def junction_tree(G):
    r"""Returns a junction tree of a given graph.

    Parameters
    ----------
    G : NetworkX graph
        Directed graph

    Returns
    -------
    junction_tree : NetworkX graph
                    The corresponding junction tree of G.

    Raises
    ------
    NetworkXNotImplemented
        The algorithm does not support Graph, MultiGraph and MultiDiGraph.
        If the input graph is an instance of one of these classes, a
        :exc:`NetworkXNotImplemented` is raised.

    Notes
    -----
    A junction tree (or clique tree) is a tree T generated from a (un)directed graph G.
    Its nodes consist of cliques and connecting sepsets respectively.
    The junction tree algorithm consists of five steps:

    1. Moralize graph
    2. Triangulate graph
    3. Find maximum cliques
    4. Build graph from cliques, connecting cliques with shared
       variables, set edge-weight to number of shared variables.
    5. Find maximum spanning tree

    https://en.wikipedia.org/wiki/Junction_tree_algorithm

    References
    ----------
    .. [1] Finn V. Jensen and Frank Jensen. 1994. Optimal
          junction trees. In Proceedings of the Tenth international
          conference on Uncertainty in artificial intelligence (UAI’94).
          Morgan Kaufmann Publishers Inc., San Francisco, CA, USA, 360–366.
    """

    clique_graph = nx.Graph()
    if G.is_directed():
        moralized = moral.moral_graph(G)
        chordal_graph, _ = complete_to_chordal_graph(moralized)
    else:
        chordal_graph, _ = complete_to_chordal_graph(G)

    cliques = [tuple(sorted(i)) for i in chordal_graph_cliques(chordal_graph)]
    clique_graph.add_nodes_from(cliques, type='clique')

    for edge in combinations(cliques, 2):
        set_edge_0 = set(edge[0])
        set_edge_1 = set(edge[1])
        if not set_edge_0.isdisjoint(set_edge_1):
            sepset = tuple(sorted(set_edge_0.intersection(set_edge_1)))
            clique_graph.add_edge(
                edge[0], edge[1], weight=len(sepset), sepset=sepset)

    junction_tree = nx.maximum_spanning_tree(clique_graph)

    for edge in list(junction_tree.edges(data=True)):
        junction_tree.add_node(edge[2]['sepset'], type='sepset')
        junction_tree.add_edge(edge[0], edge[2]['sepset'])
        junction_tree.add_edge(edge[1], edge[2]['sepset'])
        junction_tree.remove_edge(edge[0], edge[1])

    return junction_tree


if __name__ == '__main__':
    B = nx.DiGraph()
    B.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G'])
    B.add_edges_from([('A', 'B'), ('A', 'F'), ('C', 'B'),
                      ('B', 'D'), ('F', 'G'), ('E', 'G')])
    bayes_pos = nx.spring_layout(B, k=3)
    plt.subplot(1, 2, 1)
    plt.title('Bayesian Network')
    nx.draw_networkx(B, with_labels=True)

    jt = junction_tree(B)

    plt.subplot(1, 2, 2)
    plt.title('Junction Tree')
    nx.draw_networkx(jt, with_labels=True)
    plt.show()
