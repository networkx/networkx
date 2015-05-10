# -*- coding: utf-8 -*-
"""
Connected components.
"""
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils.decorators import not_implemented_for

__authors__ = "\n".join(['Eben Kenah',
                         'Aric Hagberg <aric.hagberg@gmail.com>'
                         'Christopher Ellison'])
__all__ = [
    'number_connected_components',
    'connected_components',
    'connected_component_subgraphs',
    'is_connected',
    'node_connected_component',
]


@not_implemented_for('directed')
def connected_components(G):
    """Generate connected components.

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph

    Returns
    -------
    comp : generator of sets
       A generator of sets of nodes, one for each component of G.

    Examples
    --------
    Generate a sorted list of connected components, largest first.

    >>> G = nx.path_graph(4)
    >>> G.add_path([10, 11, 12])
    >>> [len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
    [4, 3]

    If you only want the largest connected component, it's more
    efficient to use max instead of sort.

    >>> largest_cc = max(nx.connected_components(G), key=len)

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    For undirected graphs only.

    """
    seen = set()
    for v in G:
        if v not in seen:
            c = set(_plain_bfs(G, v))
            yield c
            seen.update(c)


@not_implemented_for('directed')
def connected_component_subgraphs(G, copy=True):
    """Generate connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph.

    copy: bool (default=True)
      If True make a copy of the graph attributes

    Returns
    -------
    comp : generator
      A generator of graphs, one for each connected component of G.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> G.add_edge(5,6)
    >>> graphs = list(nx.connected_component_subgraphs(G))

    If you only want the largest connected component, it's more
    efficient to use max than sort.

    >>> Gc = max(nx.connected_component_subgraphs(G), key=len)

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only.
    Graph, node, and edge attributes are copied to the subgraphs by default.

    """
    for c in connected_components(G):
        if copy:
            yield G.subgraph(c).copy()
        else:
            yield G.subgraph(c)


def number_connected_components(G):
    """Return the number of connected components.

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph.

    Returns
    -------
    n : integer
       Number of connected components

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only.

    """
    return len(list(connected_components(G)))


@not_implemented_for('directed')
def is_connected(G):
    """Return True if the graph is connected, false otherwise.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    connected : bool
      True if the graph is connected, false otherwise.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> print(nx.is_connected(G))
    True

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only.

    """
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept('Connectivity is undefined ',
                                          'for the null graph.')
    return len(set(_plain_bfs(G, next(G.nodes_iter())))) == len(G)


@not_implemented_for('directed')
def node_connected_component(G, n):
    """Return the nodes in the component of graph containing node n.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    n : node label
       A node in G

    Returns
    -------
    comp : set
       A set of nodes in the component of G containing node n.

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only.

    """
    return set(_plain_bfs(G, n))


def _plain_bfs(G, source):
    """A fast BFS node generator"""
    seen = set()
    nextlevel = {source}
    while nextlevel:
        thislevel = nextlevel
        nextlevel = set()
        for v in thislevel:
            if v not in seen:
                yield v
                seen.add(v)
                nextlevel.update(G[v])
