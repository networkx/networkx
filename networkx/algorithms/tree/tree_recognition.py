#-*- coding: utf-8 -*-
import networkx as nx
from networkx.utils import not_implemented_for
__author__ = """\n""".join(['Ferdinando Papale <ferdinando.papale@gmail.com>'])
__all__ = ['is_tree', 'is_forest']


@not_implemented_for('directed')
def is_tree(G):
    """Return True if the input graph is a tree

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    True if the input graph is a tree

    Notes
    -----
    For undirected graphs only.
    """
    n = len(G)
    if n == 0:
        raise nx.NetworkXPointlessConcept
    return nx.number_of_edges(G) == n - 1

@not_implemented_for('directed')
def is_forest(G):
    """Return True if the input graph is a forest

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    True if the input graph is a forest

    Notes
    -----
    For undirected graphs only.
    """
    for graph in nx.connected_component_subgraphs(G):
        if not nx.is_tree(graph):
            return False
    return True
