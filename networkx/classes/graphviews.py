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
"""View of Graphs as SubGraph, Reverse, Directed, Undirected.

In some algorithms it is convenient to temporarily morph
a graph to exclude some nodes or edges. It should be better
to do that via a view than to remove and then re-add.

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


__all__ = ['SubGraph', 'SubDiGraph', 'SubMultiGraph', 'SubMultiDiGraph',
           'ReverseView', 'MultiReverseView',
           'DiGraphView', 'MultiDiGraphView',
           'GraphView', 'MultiGraphView',
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


class SubDiGraph(ReadOnlyGraph, DiGraph):
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


class SubMultiGraph(ReadOnlyGraph, MultiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterMultiAdjacency(graph._adj, filter_node, filter_edge)


class SubMultiDiGraph(ReadOnlyGraph, MultiDiGraph):
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


class ReverseView(ReadOnlyGraph, DiGraph):
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


class MultiReverseView(ReadOnlyGraph, MultiDiGraph):
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


class DiGraphView(ReadOnlyGraph, DiGraph):
    def __init__(self, graph):
        if graph.is_multigraph():
            msg = 'Wrong View class. Use MultiDiGraphView.'
            raise NetworkXError(msg)
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        if graph.is_directed():
            self._pred = graph._pred
            self._succ = graph._succ
        else:
            self._pred = graph._adj
            self._succ = graph._adj
        self._adj = self._succ


class MultiDiGraphView(ReadOnlyGraph, MultiDiGraph):
    def __init__(self, graph):
        if not graph.is_multigraph():
            msg = 'Wrong View class. Use DiGraphView.'
            raise NetworkXError(msg)
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        if graph.is_directed():
            self._pred = graph._pred
            self._succ = graph._succ
        else:
            self._pred = graph._adj
            self._succ = graph._adj
        self._adj = self._succ


class GraphView(ReadOnlyGraph, Graph):
    UnionAdj = UnionAdjacency

    def __init__(self, graph):
        if graph.is_multigraph():
            msg = 'Wrong View class. Use MultiGraphView.'
            raise NetworkXError(msg)
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        if graph.is_directed():
            self._adj = self.UnionAdj(graph._succ, graph._pred)
        else:
            self._adj = graph._adj


class MultiGraphView(ReadOnlyGraph, MultiGraph):
    UnionAdj = UnionMultiAdjacency

    def __init__(self, graph):
        if not graph.is_multigraph():
            msg = 'Wrong View class. Use GraphView.'
            raise NetworkXError(msg)
        self._graph = graph
        self.graph = graph.graph
        self._node = graph._node
        if graph.is_directed():
            self._adj = self.UnionAdj(graph._succ, graph._pred)
        else:
            self._adj = graph._adj