# -*- coding: utf-8 -*-
"""Weakly connected components.
"""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__authors__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])

__all__ = [
    'number_weakly_connected_components',
    'weakly_connected_components',
    'weakly_connected_component_subgraphs',
    'is_weakly_connected',
]


@not_implemented_for('undirected')
def weakly_connected_components(G):
    """Generate weakly connected components of G.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph

    Returns
    -------
    comp : generator of sets
        A generator of sets of nodes, one for each weakly connected
        component of G.

    Examples
    --------
    Generate a sorted list of weakly connected components, largest first.

    >>> G = nx.path_graph(4, create_using=nx.DiGraph())
    >>> G.add_path([10, 11, 12])
    >>> [len(c) for c in sorted(nx.weakly_connected_components(G),
    ...                         key=len, reverse=True)]
    [4, 3]

    If you only want the largest component, it's more efficient to
    use max instead of sort.

    >>> largest_cc = max(nx.weakly_connected_components(G), key=len)

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    For directed graphs only.

    """
    seen = set()
    for v in G:
        if v not in seen:
            c = set(_plain_bfs(G, v))
            yield c
            seen.update(c)


@not_implemented_for('undirected')
def number_weakly_connected_components(G):
    """Return the number of weakly connected components in G.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph.

    Returns
    -------
    n : integer
        Number of weakly connected components

    See Also
    --------
    connected_components

    Notes
    -----
    For directed graphs only.

    """
    return len(list(weakly_connected_components(G)))


@not_implemented_for('undirected')
def weakly_connected_component_subgraphs(G, copy=True):
    """Generate weakly connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph.

    copy: bool (default=True)
        If True make a copy of the graph attributes

    Returns
    -------
    comp : generator
        A generator of graphs, one for each weakly connected component of G.

    Examples
    --------
    Generate a sorted list of weakly connected components, largest first.

    >>> G = nx.path_graph(4, create_using=nx.DiGraph())
    >>> G.add_path([10, 11, 12])
    >>> [len(c) for c in sorted(nx.weakly_connected_component_subgraphs(G),
    ...                         key=len, reverse=True)]
    [4, 3]

    If you only want the largest component, it's more efficient to
    use max instead of sort.

    >>> Gc = max(nx.weakly_connected_component_subgraphs(G), key=len)

    See Also
    --------
    strongly_connected_components
    connected_components

    Notes
    -----
    For directed graphs only.
    Graph, node, and edge attributes are copied to the subgraphs by default.

    """
    for comp in weakly_connected_components(G):
        if copy:
            yield G.subgraph(comp).copy()
        else:
            yield G.subgraph(comp)


@not_implemented_for('undirected')
def is_weakly_connected(G):
    """Test directed graph for weak connectivity.

    A directed graph is weakly connected if, and only if, the graph
    is connected when the direction of the edge between nodes is ignored.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    Returns
    -------
    connected : bool
        True if the graph is weakly connected, False otherwise.

    See Also
    --------
    is_strongly_connected
    is_semiconnected
    is_connected

    Notes
    -----
    For directed graphs only.

    """
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(list(weakly_connected_components(G))[0]) == len(G)


def _plain_bfs(G, source):
    """A fast BFS node generator

    The direction of the edge between nodes is ignored.

    For directed graphs only.

    """
    Gsucc = G.succ
    Gpred = G.pred

    seen = set()
    nextlevel = {source}
    while nextlevel:
        thislevel = nextlevel
        nextlevel = set()
        for v in thislevel:
            if v not in seen:
                yield v
                seen.add(v)
                nextlevel.update(Gsucc[v])
                nextlevel.update(Gpred[v])
