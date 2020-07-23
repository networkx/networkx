r"""Function for computing a junction tree of a graph."""

import networkx as nx
from networkx.utils import not_implemented_for
from networkx.algorithms import moral, complete_to_chordal_graph, chordal_graph_cliques
from itertools import combinations

__all__ = ["junction_tree"]


@not_implemented_for("multigraph", "MultiDiGraph")
def junction_tree(G):
    r"""Returns a junction tree of a given graph.

    Notes
    -----
    A junction tree (or clique tree) is a tree T generated from a (un)directed graph G.
    The tree's nodes consist of cliques and connecting sepsets of the original graph
    respectively. The sepset of two cliques is the intersection ot the variables
    of these cliques, e.g. the sepset of (A,B,C) and (A,C,E,F) is (A,C).
    The junction tree algorithm consists of five steps:

    1. Moralize graph
    2. Triangulate graph
    3. Find maximum cliques
    4. Build graph from cliques, connecting cliques with shared
       variables, set edge-weight to number of shared variables.
    5. Find maximum spanning tree

    https://en.wikipedia.org/wiki/Junction_tree_algorithm

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
    clique_graph.add_nodes_from(cliques, type="clique")

    for edge in combinations(cliques, 2):
        set_edge_0 = set(edge[0])
        set_edge_1 = set(edge[1])
        if not set_edge_0.isdisjoint(set_edge_1):
            sepset = tuple(sorted(set_edge_0.intersection(set_edge_1)))
            clique_graph.add_edge(edge[0], edge[1], weight=len(sepset), sepset=sepset)

    junction_tree = nx.maximum_spanning_tree(clique_graph)

    for edge in list(junction_tree.edges(data=True)):
        junction_tree.add_node(edge[2]["sepset"], type="sepset")
        junction_tree.add_edge(edge[0], edge[2]["sepset"])
        junction_tree.add_edge(edge[1], edge[2]["sepset"])
        junction_tree.remove_edge(edge[0], edge[1])

    return junction_tree
