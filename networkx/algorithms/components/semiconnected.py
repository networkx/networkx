# -*- coding: utf-8 -*-
"""
Semiconnectedness.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['is_semiconnected']

@not_implemented_for('undirected')
def is_semiconnected(G):
    """Return True if the graph is semiconnected, False otherwise.

    A graph is semiconnected if, and only if, for any pair of nodes, either one
    is reachable from the other, or they are mutually reachable.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph.

    Returns
    -------
    semiconnected : bool
        True if the graph is semiconnected, False otherwise.

    Raises
    ------
    NetworkXNotImplemented :
        If the input graph is not directed.

    NetworkXPointlessConcept :
        If the graph is empty.

    Examples
    --------
    >>> G=nx.path_graph(4,create_using=nx.DiGraph())
    >>> print(nx.is_semiconnected(G))
    True
    >>> G=nx.DiGraph([(1, 2), (3, 2)])
    >>> print(nx.is_semiconnected(G))
    False

    See Also
    --------
    is_strongly_connected,
    is_weakly_connected
    """
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            'Connectivity is undefined for the null graph.')

    if not nx.is_weakly_connected(G):
        return False

    G = nx.condensation(G)
    path = nx.topological_sort(G)
    return all(G.has_edge(u, v) for u, v in zip(path[:-1], path[1:]))
