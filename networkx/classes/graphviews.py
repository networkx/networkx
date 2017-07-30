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
"""Views of Graph for reverse, to_directed, to_undirected.

In some algorithms it is convenient to temporarily morph
a graph to reverse directed edges, or treat a directed graph
as undirected, etc. This module provides those graph views.
"""
import networkx as nx
from networkx.classes import DiGraph, MultiDiGraph
from networkx.classes import Graph, MultiGraph
from networkx.utils import not_implemented_for
from networkx.classes.coreviews import UnionAdjacency, UnionMultiAdjacency


__all__ = ['ReverseView', 'MultiReverseView', 'reverse_view',
           'DirectedView', 'MultiDirectedView', 'to_directed',
           'UnDirectedView', 'MultiUnDirectedView', 'to_undirected',
           ]


class ReverseView(DiGraph):
    def __init__(self, graph):
        if not graph.is_directed():
            msg = "not implemented for undirected type"
            raise nx.NetworkXNotImplemented(msg)

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
            raise nx.NetworkXNotImplemented(msg)

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
            return nx.induced_subgraph(graph, graph)
        return nx.induced_subgraph(graph, graph)
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
        return nx.induced_subgraph(digraph, digraph)
    return nx.induced_subgraph(digraph, digraph)
