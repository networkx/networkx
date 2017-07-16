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
from __future__ import division
from collections import Mapping

from networkx.classes import AtlasView, EdgeView
from networkx.classes import Graph, DiGraph, MultiGraph, MultiDiGraph

__all__ = ['HiddenAtlasView', 'HiddenAtlasView2', 'HiddenAtlasView3',
           'GraphView', 'DiGraphView', 'MultiGraphView', 'MultiDiGraphView']


class HiddenAtlasView(Mapping):
    def __init__(self, d, hidden_keys):
        self._atlas = d
        self.hidden_keys = hidden_keys

    def __len__(self):
        return len(set(self._atlas) - self.hidden_keys)

    def __iter__(self):
        return (n for n in self._atlas if n not in self.hidden_keys)

    def __getitem__(self, key):
        if key in self._atlas and key not in self.hidden_keys:
            return self._atlas[key]
        raise KeyError("Key {} not found".format(key))

    def copy(self):
        return {u: d for u, d in self._atlas.items()
                if u not in self.hidden_keys}

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self._atlas,
                               self.hidden_keys)


class HiddenAtlasView2(Mapping):
    def __init__(self, d, hidden_nodes, hidden_edges):
        self._atlas = d
        self.hidden_nodes = hidden_nodes
        self.hidden_edges = hidden_edges

    def __len__(self):
        return len(set(self._atlas) - self.hidden_nodes)

    def __iter__(self):
        return (n for n in self._atlas if n not in self.hidden_nodes)

    def __getitem__(self, node):
        if node in self._atlas and node not in self.hidden_nodes:
            he = set(v for u, v in self.hidden_edges if u == node)
            hn = he | self.hidden_nodes
            return HiddenAtlasView(self._atlas[node], hn)
        raise KeyError("Key {} not found".format(node))

    def copy(self):
        return {u: {v: d for v, d in nbrs.items() if v not in self.hidden_nodes
                    if (u, v) not in self.hidden_edges}
                for u, nbrs in self._atlas.items()
                if u not in self.hidden_nodes}

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self._atlas,
                                   self.hidden_nodes, self.hidden_edges)


class HiddenAtlasView2Multi(HiddenAtlasView2):
    def __getitem__(self, node):
        if node in self._atlas and node not in self.hidden_nodes:
            hk = set(k for v, k in self.hidden_edges if v == node)
            return HiddenAtlasView(self._atlas[node], hk)
        raise KeyError("Key {} not found".format(node))

    def copy(self):
        return {v: {k: d for k, d in nbrs.items()
                    if (v, k) not in self.hidden_edges}
                for v, nbrs in self._atlas.items()
                if v not in self.hidden_nodes}


class HiddenAtlasView3(HiddenAtlasView2):
    def __getitem__(self, key):
        if key in self._atlas and key not in self.hidden_nodes:
            he = set((v, k) for u, v, k in self.hidden_edges if u == key)
            hn = self.hidden_nodes
            return HiddenAtlasView2(self._atlas[key], hn, he)
        raise KeyError("Key {} not found".format(key))

    def copy(self):
        return {u: {v: {k: d for k, d in kd.items()
                        if (u, v, k) not in self.hidden_edges}
                    for v, kd in nbrs.items() if v not in self.hidden_nodes}
                for u, nbrs in self._atlas.items()
                    if u not in self.hidden_nodes}


class GraphView(Graph):
    def __init__(self, graph, hidden_nodes, hidden_edges):
        self._graph = graph
        self.graph = graph.graph
        hn = set(hidden_nodes)
        # ensure 2-tuples and store undirected edges as both directed
        he = set(hidden_edges) | set((v, u) for u, v in hidden_edges)
        self._node = HiddenAtlasView(graph._node, hn)
        self._adj = HiddenAtlasView2(graph._adj, hn, he)


class DiGraphView(DiGraph):
    def __init__(self, graph, hidden_nodes, hidden_edges):
        self._graph = graph
        self.graph = graph.graph
        hn = set(hidden_nodes)
        # ensure edges are all 2-tuples
        he = set((u, v) for u, v in hidden_edges)
        phe = set((v, u) for u, v in hidden_edges)
        self._node = HiddenAtlasView(graph._node, hn)
        self._adj = HiddenAtlasView2(graph._adj, hn, he)
        self._pred = HiddenAtlasView2(graph._pred, hn, phe)
        self._succ = self._adj


class MultiGraphView(MultiGraph):
    def __init__(self, graph, hidden_nodes, hidden_edges):
        self._graph = graph
        self.graph = graph.graph
        hn = set(hidden_nodes)
        # ensure 3-tuples and store undirected edges as both directed
        he = set(hidden_edges) | set((v, u, k) for u, v, k in hidden_edges)
        self._node = HiddenAtlasView(graph._node, hn)
        self._adj = HiddenAtlasView3(graph._adj, hn, he)


class MultiDiGraphView(MultiDiGraph):
    def __init__(self, graph, hidden_nodes, hidden_edges):
        self._graph = graph
        self.graph = graph.graph
        hn = set(hidden_nodes)
        # ensure edges are all 3-tuples
        he = set((u, v, k) for u, v, k in hidden_edges)
        phe = set((v, u, k) for u, v, k in hidden_edges)
        self._node = HiddenAtlasView(graph._node, hn)
        self._adj = HiddenAtlasView3(graph._adj, hn, he)
        self._pred = HiddenAtlasView3(graph._pred, hn, phe)
        self._succ = self._adj
