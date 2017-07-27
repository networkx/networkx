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
from networkx.classes.coreviews import AtlasView
from networkx.classes.coreviews import AdjacencyView, MultiAdjacencyView
from networkx.classes.filters import no_filter, show_nodes, show_edges
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for


__all__ = ['SubGraph', 'DiSubGraph', 'MultiSubGraph', 'MultiDiSubGraph',
           'induced_subgraph', 'edge_subgraph']


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


class SubGraphVeil(object):
    def __init__(self, graph, filter_node, filter_edge):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        if graph.is_multigraph():
            FA = FilterMultiAdjacency
        else:
            FA = FilterAdjacency
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FA(graph._adj, filter_node, filter_edge)
        if graph.is_directed():
            self._succ = self._adj
            self._pred = FA(graph._pred, filter_node,
                            lambda u, v: filter_edge(v, u))

    def not_allowed(self, *args, **kwds):
        msg = "SubGraph Views are readonly. Mutations not allowed"
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


def subgraph(graph, filter_node=no_filter, filter_edge=no_filter):
    class SubGraph(SubGraphVeil, graph.__class__):
        pass
    return SubGraph(graph, filter_node, filter_edge)


def slow_subgraph(graph, filter_node=no_filter, filter_edge=no_filter):
    cls = graph.__class__

    class SubGraph(cls):
        def __init__(self, graph, filter_node, filter_edge):
            self._graph = graph
            self._NODE_OK = filter_node
            self._EDGE_OK = filter_edge

            # Set graph interface
            if graph.is_multigraph():
                FA = FilterMultiAdjacency
            else:
                FA = FilterAdjacency
            self.graph = graph.graph
            self._node = FilterAtlas(graph._node, filter_node)
            self._adj = FA(graph._adj, filter_node, filter_edge)
            if graph.is_directed():
                self._succ = self._adj
                self._pred = FA(graph._pred, filter_node,
                                lambda u, v: filter_edge(v, u))

        def not_allowed(self, *args, **kwds):
            msg = "SubGraph Views are readonly. Mutations not allowed"
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

    return SubGraph(graph, filter_node, filter_edge)


class SubGraph(Graph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterAdjacency(graph._adj, filter_node, filter_edge)

    def not_allowed(self, *args, **kwds):
        msg = "SubGraph Views are readonly. Mutations not allowed"
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

    def not_allowed(self, *args, **kwds):
        msg = "SubGraph Views are readonly. Mutations not allowed"
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


class MultiSubGraph(MultiGraph):
    def __init__(self, graph, filter_node=no_filter, filter_edge=no_filter):
        self._graph = graph
        self._NODE_OK = filter_node
        self._EDGE_OK = filter_edge

        # Set graph interface
        self.graph = graph.graph
        self._node = FilterAtlas(graph._node, filter_node)
        self._adj = FilterMultiAdjacency(graph._adj, filter_node, filter_edge)

    def not_allowed(self, *args, **kwds):
        msg = "SubGraph Views are readonly. Mutations not allowed"
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

    def not_allowed(self, *args, **kwds):
        msg = "SubGraph Views are readonly. Mutations not allowed"
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
    edges and attributes use `subgraph.copy()` or `nx.Graph(subgraph)`

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
    edges and attributes use `subgraph.copy()` or `nx.Graph(subgraph)`

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


@not_implemented_for('undirected')
def reverse_view(digraph):
    if digraph.is_multigraph():
        G = MultiDiGraph()
        adj_view = MultiAdjacencyView
    else:
        G = DiGraph()
        adj_view = AdjacencyView
    # set graph interface
    G.graph = digraph.graph
    G._node = AtlasView(digraph._node)
    G._adj = adj_view(digraph._pred)
    G._pred = adj_view(digraph._succ)
    G._succ = G._adj
    return G


def to_directed(graph):
    return graph


def to_undirected(digraph):
    return digraph
