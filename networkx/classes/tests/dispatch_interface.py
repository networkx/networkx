# This file contains utilities for testing the dispatching feature

# A full test of all dispatchable algorithms is performed by
# modifying the pytest invocation and setting an environment variable
# NETWORKX_GRAPH_CONVERT=nx-loopback pytest
# This is comprehensive, but only tests the `test_override_dispatch`
# function in networkx.classes.backends.

# To test the `_dispatch` function directly, several tests scattered throughout
# NetworkX have been augmented to test normal and dispatch mode.
# Searching for `dispatch_interface` should locate the specific tests.

import networkx as nx
from networkx import DiGraph, Graph, MultiDiGraph, MultiGraph, PlanarEmbedding


class LoopbackGraph(Graph):
    __networkx_plugin__ = "nx-loopback"


class LoopbackDiGraph(DiGraph):
    __networkx_plugin__ = "nx-loopback"


class LoopbackMultiGraph(MultiGraph):
    __networkx_plugin__ = "nx-loopback"


class LoopbackMultiDiGraph(MultiDiGraph):
    __networkx_plugin__ = "nx-loopback"


class LoopbackPlanarEmbedding(PlanarEmbedding):
    __networkx_plugin__ = "nx-loopback"


def convert(graph):
    if isinstance(graph, PlanarEmbedding):
        return LoopbackPlanarEmbedding(graph)
    if isinstance(graph, MultiDiGraph):
        return LoopbackMultiDiGraph(graph)
    if isinstance(graph, MultiGraph):
        return LoopbackMultiGraph(graph)
    if isinstance(graph, DiGraph):
        return LoopbackDiGraph(graph)
    if isinstance(graph, Graph):
        return LoopbackGraph(graph)
    raise TypeError(f"Unsupported type of graph: {type(graph)}")


class LoopbackDispatcher:
    non_toplevel = {
        "inter_community_edges": nx.community.quality.inter_community_edges,
        "is_tournament": nx.algorithms.tournament.is_tournament,
        "mutual_weight": nx.algorithms.structuralholes.mutual_weight,
        "score_sequence": nx.algorithms.tournament.score_sequence,
        "tournament_matrix": nx.algorithms.tournament.tournament_matrix,
    }

    def __getattr__(self, item):
        # Return the original, undecorated NetworkX algorithm
        if hasattr(nx, item):
            return getattr(nx, item)._orig_func
        if item in self.non_toplevel:
            return self.non_toplevel[item]._orig_func
        raise AttributeError(item)

    @staticmethod
    def convert_from_nx(graph, weight=None, *, name=None):
        return graph

    @staticmethod
    def convert_to_nx(obj, *, name=None):
        return obj

    @staticmethod
    def on_start_tests(items):
        # Verify that items can be xfailed
        for item in items:
            assert hasattr(item, "add_marker")


dispatcher = LoopbackDispatcher()
