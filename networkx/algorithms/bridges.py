# -*- coding: utf-8 -*-
# bridges.py - bridge-finding algorithms
#
# Copyright 2004-2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Bridge-finding algorithms."""
from itertools import chain

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['bridges', 'has_bridges']


@not_implemented_for('multigraph')
@not_implemented_for('directed')
def bridges(G, root=None):
    """Generate all bridges in a graph.

    A *bridge* in a graph is an edge whose removal causes the number of
    connected components of the graph to increase.

    Parameters
    ----------
    G : undirected graph

    root : node (optional)
       A node in the graph `G`. If specified, only the bridges in the
       connected component containing this node will be returned.

    Yields
    ------
    e : edge
       An edge in the graph whose removal disconnects the graph (or
       causes the number of connected components to increase).

    Raises
    ------
    NodeNotFound
       If `root` is not in the graph `G`.

    Examples
    --------
    The barbell graph with parameter zero has a single bridge::

        >>> G = nx.barbell_graph(10, 0)
        >>> list(nx.bridges(G))
        [(9, 10)]

    Notes
    -----
    This implementation uses the :func:`networkx.chain_decomposition`
    function, so it shares its worst-case time complexity, :math:`O(m +
    n)`, ignoring polylogarithmic factors, where *n* is the number of
    nodes in the graph and *m* is the number of edges.

    """
    chains = nx.chain_decomposition(G, root=root)
    chain_edges = set(chain.from_iterable(chains))
    for u, v in G.edges():
        if (u, v) not in chain_edges and (v, u) not in chain_edges:
            yield u, v


@not_implemented_for('multigraph')
@not_implemented_for('directed')
def has_bridges(G, root=None):
    """Decide whether a graph has any bridges.

    A *bridge* in a graph is an edge whose removal causes the number of
    connected components of the graph to increase.

    Parameters
    ----------
    G : undirected graph

    root : node (optional)
       A node in the graph `G`. If specified, only the bridges in the
       connected component containing this node will be considered.

    Returns
    -------
    bool
       Whether the graph (or the connected component containing `root`)
       has any bridges.

    Raises
    ------
    NodeNotFound
       If `root` is not in the graph `G`.

    Examples
    --------
    The barbell graph with parameter zero has a single bridge::

        >>> G = nx.barbell_graph(10, 0)
        >>> nx.has_bridges(G)
        True

    On the other hand, the cycle graph has no bridges::

        >>> G = nx.cycle_graph(5)
        >>> nx.has_bridges(G)
        False

    Notes
    -----
    This implementation uses the :func:`networkx.bridges` function, so
    it shares its worst-case time complexity, :math:`O(m + n)`, ignoring
    polylogarithmic factors, where *n* is the number of nodes in the
    graph and *m* is the number of edges.

    """
    try:
        next(bridges(G))
    except StopIteration:
        return False
    else:
        return True
