#-*- coding: utf-8 -*-
import networkx as nx

__all__ = ['girvan_newman']


def girvan_newman(G, ranking=None):
    """Find communities in graph using Girvan–Newman method.

    Parameters
    ----------
    G : NetworkX graph

    weight : string, optional (default=None)
       Edge data key corresponding to the edge weight.

    ranking : function
        Function that takes a graph as input and outputs a
        dictionary. The keys in the dictionary must be the edges of the
        graph and the values must be comparable. The edges with the
        highest value will be removed at each iteration of the
        algorithm. The function will be called during each iteration of
        the algorithm to recompute the edge rankings.

        If not specified, the function
        :func:`networkx.edge_betweenness_centrality` will be used.

    Returns
    -------
    List of tuples which contains the clusters of nodes.

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> comp = girvan_newman(G)
    >>> comp[0]
    ([0, 1, 2, 3, 4], [8, 9, 5, 6, 7])

    To utilize edge weights when choosing an edge with, for example, the
    edge betweenness centrality ranking function::

        >>> from functools import partial
        >>> G = nx.path_graph(10)
        >>> ranking = partial(nx.edge_betweenness_centrality, weight='weight')
        >>> comp = girvan_newman(G, ranking=ranking)
        >>> comp[0]
        ([0, 1, 2, 3, 4], [8, 9, 5, 6, 7])

    To specify a different ranking algorithm, for example edge current
    flow betweenness centrality, use the ``ranking`` keyword argument::

        >>> G = nx.path_graph(10)
        >>> ranking = nx.edge_current_flow_betweenness_centrality
        >>> comp = girvan_newman(G, ranking=ranking)  # doctest: +SKIP

    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively removing
    edges from the original graph. Algorithm removes edge with the highest
    betweenness centrality at each step. As the graph breaks down into pieces,
    the tightly knit community structure is exposed and result can be depicted
    as a dendrogram.
    """
    if ranking is None:
        ranking = nx.edge_betweenness_centrality
    g = G.copy().to_undirected()
    components = []
    while g.number_of_edges() > 0:
        _remove_max_edge(g, ranking)
        components.append(tuple(list(H)
                                for H in nx.connected_component_subgraphs(g)))
    return components


def _remove_max_edge(G, ranking):
    """
    Removes edge with the highest value on betweenness centrality.

    Repeat this step until more connected components than the connected
    components of the original graph are detected.

    It is part of Girvan–Newman algorithm.

    :param G: NetworkX graph
    :param weight: string, optional (default=None) Edge data key corresponding
    to the edge weight.
    """
    number_components = nx.number_connected_components(G)
    while nx.number_connected_components(G) <= number_components:
        betweenness = ranking(G)
        max_value = max(betweenness.values())
        # Use a list of edges because G is changed in the loop
        for edge in list(G.edges()):
            if betweenness[edge] == max_value:
                G.remove_edge(*edge)
