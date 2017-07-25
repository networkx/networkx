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
from collections import Mapping

from networkx.classes import Graph, DiGraph, MultiGraph, MultiDiGraph
from networkx.classes.filters import no_filter

__all__ = ['SubGraph', 'DiSubGraph', 'MultiSubGraph', 'MultiDiSubGraph']


class FilterAtlas(Mapping):  # nodedict, nbrdict, keydict
    def __init__(self, d, NODE_OK):
        self._atlas = d
        self.NODE_OK = NODE_OK

    def __len__(self):
        return sum(1 for n in self._atlas if self.NODE_OK(n))

    def __iter__(self):
        return (n for n in self._atlas if self.NODE_OK(n))

    def __getitem__(self, key):
        if key in self._atlas and self.NODE_OK(key):
            return self._atlas[key]
        raise KeyError("Key {} not found".format(key))

    def copy(self):
        return {u: d for u, d in self._atlas.items()
                if self.NODE_OK(u)}

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self._atlas,
                               self.NODE_OK)


class FilterAdjacency(Mapping):   # edgedict
    def __init__(self, d, NODE_OK, EDGE_OK):
        self._atlas = d
        self.NODE_OK = NODE_OK
        self.EDGE_OK = EDGE_OK

    def __len__(self):
        return sum(1 for n in self._atlas if self.NODE_OK(n))

    def __iter__(self):
        return (n for n in self._atlas if self.NODE_OK(n))

    def __getitem__(self, node):
        if node in self._atlas and self.NODE_OK(node):
            def new_node_ok(nbr):
                return self.NODE_OK(nbr) and self.EDGE_OK(node, nbr)
            return FilterAtlas(self._atlas[node], new_node_ok)
        raise KeyError("Key {} not found".format(node))

    def copy(self):
        return {u: {v: d for v, d in nbrs.items() if self.NODE_OK(v)
                    if self.EDGE_OK(u, v)}
                for u, nbrs in self._atlas.items()
                if self.NODE_OK(u)}

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self._atlas,
                                   self.NODE_OK, self.EDGE_OK)


class FilterMultiInner(FilterAdjacency):  # muliedge_seconddict
    def __len__(self):
        return sum(1 for n in self)

    def __iter__(self):
        for n in self._atlas:
            if self.NODE_OK(n):
                some_keys_ok = False
                for key in self._atlas[n]:
                    if self.EDGE_OK(n, key):
                        some_keys_ok = True
                        break
                if some_keys_ok is True:
                    yield n

    def __getitem__(self, nbr):
        if nbr in self._atlas and self.NODE_OK(nbr):
            def new_node_ok(key):
                return self.EDGE_OK(nbr, key)
            return FilterAtlas(self._atlas[nbr], new_node_ok)
        raise KeyError("Key {} not found".format(nbr))

    def copy(self):
        return {v: {k: d for k, d in nbrs.items() if self.EDGE_OK(v, k)}
                for v, nbrs in self._atlas.items() if self.NODE_OK(v)}


class FilterMultiAdjacency(FilterAdjacency):  # multiedgedict
    def __getitem__(self, node):
        if node in self._atlas and self.NODE_OK(node):
            def edge_ok(nbr, key):
                return self.NODE_OK(nbr) and self.EDGE_OK(node, nbr, key)
            return FilterMultiInner(self._atlas[node], self.NODE_OK, edge_ok)
        raise KeyError("Key {} not found".format(node))

    def copy(self):
        return {u: {v: {k: d for k, d in kd.items()
                        if self.EDGE_OK(u, v, k)}
                    for v, kd in nbrs.items() if self.NODE_OK(v)}
                for u, nbrs in self._atlas.items() if self.NODE_OK(u)}


class SubGraph(Graph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterAdjacency(graph._adj, filter_node, filter_edge)


class DiSubGraph(DiGraph):
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


class MultiSubGraph(MultiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterMultiAdjacency(graph._adj, filter_node, filter_edge)


class MultiDiSubGraph(MultiDiGraph):
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
