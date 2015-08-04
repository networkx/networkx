# -*- coding: utf-8 -*-
# centrality.py - functions for computing communities using centrality notions
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing communities based on centrality notions."""

import networkx as nx

__all__ = ['girvan_newman']


def girvan_newman(G, weight=None):
    """Finds communities in a graph using the Girvan–Newman method.

    Parameters
    ----------
    G : NetworkX graph

    weight : string, optional (default=None)
       Edge data key corresponding to the edge weight.

    Returns
    -------
    iterator
        Iterator over tuples of sets of nodes in ``G``. Each set of
        nodes is a community, each tuple is a sequence of communities at
        a particular level of the algorithm.

    Examples
    --------
    To get the first pair of communities::

        >>> G = nx.path_graph(10)
        >>> comp = girvan_newman(G)
        >>> tuple(sorted(c) for c in list(comp)[0])
        ([0, 1, 2, 3, 4], [5, 6, 7, 8, 9])

    To get only the first *k* tuples of communities, use
    :func:`itertools.islice`::

        >>> import itertools
        >>> G = nx.path_graph(8)
        >>> k = 2
        >>> comp = girvan_newman(G)
        >>> for communities in itertools.islice(comp, k):
        ...     print(tuple(sorted(c) for c in communities))
        ...
        ([0, 1, 2, 3], [4, 5, 6, 7])
        ([0, 1], [2, 3], [4, 5], [6, 7])

    To stop getting tuples of communities once the number of communities
    is greater than *k*, use :func:`itertools.takewhile`::

        >>> import itertools
        >>> G = nx.path_graph(8)
        >>> k = 4
        >>> comp = girvan_newman(G)
        >>> limited = itertools.takewhile(lambda c: len(c) <= k, comp)
        >>> for communities in limited:
        ...     print(tuple(sorted(c) for c in communities))
        ...
        ([0, 1, 2, 3], [4, 5, 6, 7])
        ([0, 1], [2, 3], [4, 5], [6, 7])

    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively
    removing edges from the original graph. The algorithm removes *all*
    edges with the highest betweenness centrality at each step. As the
    graph breaks down into pieces, the tightly knit community structure
    is exposed and the result can be depicted as a dendrogram.

    """
    g = G.copy().to_undirected()
    while g.number_of_edges() > 0:
        yield _without_most_central_edges(g, weight=weight)


def _without_most_central_edges(G, weight=None):
    """Returns the connected components of the graph that results from
    repeatedly removing the edges of maximum betweenness centrality.

    This function modifies the graph ``G`` in-place; that is, it removes
    edges on the graph ``G``.

    The ``weight`` parameter is passed directly to the function that
    computes edge betweenness centrality.

    """
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        # Remove the edges of maximum betweenness centrality.
        betweenness = nx.edge_betweenness_centrality(G, weight=weight)
        max_betweenness = max(betweenness.values())
        # Use a list of edges because G is changed in the loop
        G.remove_edges_from(e for e in list(G.edges())
                            if betweenness[e] == max_betweenness)
        # Get the new connected components after having removed the edges.
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components
