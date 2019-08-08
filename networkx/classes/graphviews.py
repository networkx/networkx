#    Copyright (C) 2004-2019 by
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
In other algorithms it is convenient to temporarily morph
a graph to reverse directed edges, or treat a directed graph
as undirected, etc. This module provides those graph views.

The resulting views are essentially read-only graphs that
report data from the orignal graph object. We provide an
attribute G._graph which points to the underlying graph object.

Note: Since graphviews look like graphs, one can end up with
view-of-view-of-view chains. Be careful with chains because
they become very slow with about 15 nested views.
For the common simple case of node induced subgraphs created
from the graph class, we short-cut the chain by returning a
subgraph of the original graph directly rather than a subgraph
of a subgraph. We are careful not to disrupt any edge filter in
the middle subgraph. In general, determining how to short-cut
the chain is tricky and much harder with restricted_views than
with induced subgraphs.
Often it is easiest to use .copy() to avoid chains.
"""
from networkx.classes.coreviews import UnionAdjacency, UnionMultiAdjacency, \
    FilterAtlas, FilterAdjacency, FilterMultiAdjacency
from networkx.classes.filters import no_filter
from networkx.exception import NetworkXError, NetworkXNotImplemented
# remove the graph class import when deprecated GraphView removed
from networkx.classes import Graph, DiGraph, MultiGraph, MultiDiGraph

import networkx as nx

__all__ = ['generic_graph_view', 'subgraph_view', 'reverse_view',
           'SubGraph', 'SubDiGraph', 'SubMultiGraph', 'SubMultiDiGraph',
           'ReverseView', 'MultiReverseView',
           'DiGraphView', 'MultiDiGraphView',
           'GraphView', 'MultiGraphView',
           ]


def generic_graph_view(G, create_using=None):
    if create_using is None:
        newG = G.__class__()
    else:
        newG = nx.empty_graph(0, create_using)
    if G.is_multigraph() != newG.is_multigraph():
        raise NetworkXError("Multigraph for G must agree with create_using")
    newG = nx.freeze(newG)

    # create view by assigning attributes from G
    newG._graph = G
    newG.graph = G.graph

    newG._node = G._node
    if newG.is_directed():
        if G.is_directed():
            newG._succ = G._succ
            newG._pred = G._pred
            newG._adj = G._succ
        else:
            newG._succ = G._adj
            newG._pred = G._adj
            newG._adj = G._adj
    elif G.is_directed():
        if G.is_multigraph():
            newG._adj = UnionMultiAdjacency(G._succ, G._pred)
        else:
            newG._adj = UnionAdjacency(G._succ, G._pred)
    else:
        newG._adj = G._adj
    return newG


def subgraph_view(G, filter_node=no_filter, filter_edge=no_filter):
    newG = nx.freeze(G.__class__())
    newG._NODE_OK = filter_node
    newG._EDGE_OK = filter_edge

    # create view by assigning attributes from G
    newG._graph = G
    newG.graph = G.graph

    newG._node = FilterAtlas(G._node, filter_node)
    if G.is_multigraph():
        Adj = FilterMultiAdjacency

        def reverse_edge(u, v, k): return filter_edge(v, u, k)
    else:
        Adj = FilterAdjacency

        def reverse_edge(u, v): return filter_edge(v, u)
    if G.is_directed():
        newG._succ = Adj(G._succ, filter_node, filter_edge)
        newG._pred = Adj(G._pred, filter_node, reverse_edge)
        newG._adj = newG._succ
    else:
        newG._adj = Adj(G._adj, filter_node, filter_edge)
    return newG


def reverse_view(G):
    if not G.is_directed():
        msg = "not implemented for undirected type"
        raise NetworkXNotImplemented(msg)
    newG = generic_graph_view(G)
    newG._succ, newG._pred = G._pred, G._succ
    newG._adj = newG._succ
    return newG


# The remaining definitions are for backward compatibility with v2.0 and 2.1
def ReverseView(G):
    # remove by v3 if not before
    import warnings
    msg = 'ReverseView is deprecated. Use reverse_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return reverse_view(G)


def SubGraph(G, filter_node=no_filter, filter_edge=no_filter):
    # remove by v3 if not before
    import warnings
    msg = 'SubGraph is deprecated. Use subgraph_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return subgraph_view(G, filter_node, filter_edge)


def GraphView(G):
    # remove by v3 if not before
    import warnings
    msg = 'GraphView is deprecated. Use generic_graph_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return generic_graph_view(G, Graph)


def DiGraphView(G):
    # remove by v3 if not before
    import warnings
    msg = 'GraphView is deprecated. Use generic_graph_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return generic_graph_view(G, DiGraph)


def MultiGraphView(G):
    # remove by v3 if not before
    import warnings
    msg = 'GraphView is deprecated. Use generic_graph_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return generic_graph_view(G, MultiGraph)


def MultiDiGraphView(G):
    # remove by v3 if not before
    import warnings
    msg = 'GraphView is deprecated. Use generic_graph_view instead'
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return generic_graph_view(G, MultiDiGraph)


MultiReverseView = ReverseView
SubMultiGraph = SubMultiDiGraph = SubDiGraph = SubGraph
