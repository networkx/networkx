#-*- coding: utf-8 -*-


import networkx as nx
__author__ = """\n""".join(['Ferdinando Papale <ferdinando.papale@gmail.com>'])
__all__ = ['is_tree', 'is_forest']


def is_tree(G):
    """Return true if the input graph is a tree

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    true if the input graph is a tree

    Notes
    -----
    For undirected graphs only. 
    """
    return not G.is_directed() \
            and (nx.number_of_nodes(G) == 0 \
            or (nx.is_connected(G) \
            and  (nx.number_of_edges(G) == nx.number_of_nodes(G)-1 )))  


def is_forest(G):
    """Return true if the input graph is a forest

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    true if the input graph is a forest

    Notes
    -----
    For undirected graphs only. 
    """

    if not G.is_directed():
        for graph in nx.connected_component_subgraphs(G):
            if not nx.is_tree(graph):
                return False
        return True
    else:
        return False
    

