#    Copyright (C) 2004-2017 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Author:  Aric Hagberg (hagberg@lanl.gov),
#          Pieter Swart (swart@lanl.gov),
#          Dan Schult(dschult@colgate.edu)
"""View of Graph with restricted nodes and edges.

In some algorithms it is convenient to temporarily morph
a graph to exclude some nodes or edges. It should be better
to do that via a view than to remove and then re-add.
"""
"""Views of Graph for reverse, to_directed, to_undirected.

In some algorithms it is convenient to temporarily morph
a graph to reverse directed edges, or treat a directed graph
as undirected, etc. This module provides those graph views.
"""
from collections import Mapping

from networkx.classes import Graph, DiGraph, MultiGraph, MultiDiGraph
from networkx.classes.coreviews import ReadOnlyGraph, \
                         AtlasView, AdjacencyView, MultiAdjacencyView, \
                         FilterAtlas, FilterAdjacency, FilterMultiAdjacency, \
                         UnionAdjacency, UnionMultiAdjacency
from networkx.classes.filters import no_filter, show_nodes, show_edges
from networkx.exception import NetworkXError, NetworkXNotImplemented
from networkx.utils import not_implemented_for


__all__ = ['SubGraph', 'DiSubGraph', 'MultiSubGraph', 'MultiDiSubGraph',
           'induced_subgraph', 'edge_subgraph',
           'ReverseView', 'MultiReverseView', 'reverse_view',
           'DirectedView', 'MultiDirectedView', 'to_directed',
           'UnDirectedView', 'MultiUnDirectedView', 'to_undirected',
           ]


class SubGraph(ReadOnlyGraph, Graph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterAdjacency(graph._adj, filter_node, filter_edge)


class DiSubGraph(ReadOnlyGraph, DiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterAdjacency(graph._adj, filter_node, filter_edge)
        self._pred = FilterAdjacency(graph._pred, filter_node,
                                     lambda u, v: filter_edge(v, u))
        self._succ = self._adj


class MultiSubGraph(ReadOnlyGraph, MultiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterMultiAdjacency(graph._adj, filter_node, filter_edge)


class MultiDiSubGraph(ReadOnlyGraph, MultiDiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        FMA = FilterMultiAdjacency
        self._adj = FMA(graph._adj, filter_node, filter_edge)
        self._pred = FMA(graph._pred, filter_node,
                         lambda u, v, k: filter_edge(v, u, k))
        self._succ = self._adj


def induced_subgraph(G, nbunch):
    """Return a SubGraph view of `G` showing only nodes in nbunch.

    The induced subgraph of a graph on a set of nodes N is the
    graph with nodes N and edges from G which have both ends in N.

    Parameters
    ----------
    G : NetworkX Graph
    nbunch : node, container of nodes or None (for all nodes)

    Returns
    -------
    subgraph : SubGraph View
        A read-only view of the subgraph in `G` induced by the nodes.
        Changes to the graph `G` will be reflected in the view.

    Notes
    -----
    To create a mutable subgraph with its own copies of nodes
    edges and attributes use `subgraph.copy()` or `Graph(subgraph)`

    For an inplace reduction of a graph to a subgraph you can remove nodes:
    `G.remove_nodes_from(n in G if n not in set(nbunch))`

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
    >>> H = G.subgraph([0, 1, 2])
    >>> list(H.edges)
    [(0, 1), (1, 2)]
    """
    induced_nodes = show_nodes(G.nbunch_iter(nbunch))
    if G.is_multigraph():
        if G.is_directed():
            return MultiDiSubGraph(G, induced_nodes)
        return MultiSubGraph(G, induced_nodes)
    if G.is_directed():
        return DiSubGraph(G, induced_nodes)
    return SubGraph(G, induced_nodes)


def edge_subgraph(G, edges):
    """Returns the subgraph induced by the specified edges.

    The induced subgraph contains each edge in `edges` and each
    node incident to any of those edges.

    Parameters
    ----------
    G : NetworkX Graph
    edges : iterable
        An iterable of edges. Edges not present in `G` are ignored.

    Returns
    -------
    subgraph : SubGraph View
        A read-only edge-induced subgraph of `G`.
        Changes to `G` are reflected in the view.

    Notes
    -----
    To create a mutable subgraph with its own copies of nodes
    edges and attributes use `subgraph.copy()` or `Graph(subgraph)`

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(5)
    >>> H = G.edge_subgraph([(0, 1), (3, 4)])
    >>> list(H.nodes)
    [0, 1, 3, 4]
    >>> list(H.edges)
    [(0, 1), (3, 4)]
    """
    edges = set(edges)
    nodes = set()
    for e in edges:
        nodes.update(e[:2])
    induced_edges = show_edges(edges)
    induced_nodes = show_nodes(nodes)
    if G.is_multigraph():
        if G.is_directed():
            return MultiDiSubGraph(G, induced_nodes, induced_edges)
        return MultiSubGraph(G, induced_nodes, induced_edges)
    if G.is_directed():
        return DiSubGraph(G, induced_nodes, induced_edges)
    return SubGraph(G, induced_nodes, induced_edges)


class ReverseView(DiGraph):
    def __init__(self, graph):
        if not graph.is_directed():
            msg = "not implemented for undirected type"
            raise NetworkXNotImplemented(msg)

        self._graph = graph
        # Set graph interface
        self.graph = graph.graph
        self._node = graph._node
        self._adj = graph._pred
        self._pred = graph._succ
        self._succ = self._adj

    def not_allowed(self, *args, **kwds):
        msg = "Reverse Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


class MultiReverseView(MultiDiGraph):
    def __init__(self, graph):
        if not graph.is_directed():
            msg = "not implemented for undirected type"
            raise NetworkXNotImplemented(msg)

        self._graph = graph
        # Set graph interface
        self.graph = graph.graph
        self._node = graph._node
        self._adj = graph._pred
        self._pred = graph._succ
        self._succ = self._adj

    def not_allowed(self, *args, **kwds):
        msg = "Reverse Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


@not_implemented_for('undirected')
def reverse_view(digraph):
    if digraph.is_multigraph():
        return MultiReverseView(digraph)
    return ReverseView(digraph)


class DirectedView(DiGraph):
    def __init__(self, graph):
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        self._pred = graph._adj
        self._succ = graph._adj
        self._adj = self._succ

    def not_allowed(self, *args, **kwds):
        msg = "Directed Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


class MultiDirectedView(MultiDiGraph):
    def __init__(self, graph):
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        self._pred = graph._adj
        self._succ = graph._adj
        self._adj = self._succ

    def not_allowed(self, *args, **kwds):
        msg = "Directed Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


def to_directed(graph):
    if graph.is_directed():
        if graph.is_multigraph():
            return induced_subgraph(graph, graph)
        return induced_subgraph(graph, graph)
    if graph.is_multigraph():
        return MultiDirectedView(graph)
    return DirectedView(graph)


class UnDirectedView(Graph):
    def __init__(self, digraph):
        self._graph = digraph
        self.graph = digraph.graph
        self._node = digraph._node
        self._adj = UnionAdjacency(digraph._succ, digraph._pred)

    def not_allowed(self, *args, **kwds):
        msg = "Directed Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


class MultiUnDirectedView(MultiGraph):
    def __init__(self, digraph):
        self._graph = digraph
        self.graph = digraph.graph
        self._node = digraph._node
        self._adj = UnionMultiAdjacency(digraph._succ, digraph._pred)

    def not_allowed(self, *args, **kwds):
        msg = "Directed Views are readonly. Mutations not allowed"
        raise NetworkXError(msg)

    add_node = not_allowed
    remove_node = not_allowed
    add_nodes_from = not_allowed
    remove_nodes_from = not_allowed

    add_edge = not_allowed
    remove_edge = not_allowed
    add_edges_from = not_allowed
    add_weighted_edges_from = not_allowed
    remove_edges_from = not_allowed

    clear = not_allowed


def to_undirected(digraph):
    if digraph.is_directed():
        if digraph.is_multigraph():
            return MultiUnDirectedView(digraph)
        return UnDirectedView(digraph)
    if digraph.is_multigraph():
        return induced_subgraph(digraph, digraph)
    return induced_subgraph(digraph, digraph)
