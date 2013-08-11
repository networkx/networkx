#-*- coding: utf-8 -*-


import networkx as nx
__author__ = """\n""".join(['Ferdinando Papale <ferdinando.papale@gmail.com>'])
__all__ = ['is_tree']


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

    if not G.is_directed():
        return nx.number_of_nodes(G) == 0 \
            or (nx.is_connected(G) \
            and  (nx.number_of_edges(G) == nx.number_of_nodes(G)-1 ))  
    else:
        return False



