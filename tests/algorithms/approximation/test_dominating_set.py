#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import networkx.algorithms.approximation as apxa


class TestMinWeightDominatingSet:

    def test_min_weighted_dominating_set(self):
        graph = nx.Graph()
        graph.add_edge(1, 2)
        graph.add_edge(1, 5)
        graph.add_edge(2, 3)
        graph.add_edge(2, 5)
        graph.add_edge(3, 4)
        graph.add_edge(3, 6)
        graph.add_edge(5, 6)

        vertices = set([1, 2, 3, 4, 5, 6])
        # due to ties, this might be hard to test tight bounds
        dom_set = apxa.min_weighted_dominating_set(graph)
        for vertex in vertices - dom_set:
            neighbors = set(graph.neighbors(vertex))
            ok_(len(neighbors & dom_set) > 0, "Non dominating set found!")

    def test_min_edge_dominating_set(self):
        graph = nx.path_graph(5)
        dom_set = apxa.min_edge_dominating_set(graph)

        # this is a crappy way to test, but good enough for now.
        for edge in graph.edges_iter():
            if edge in dom_set:
                continue
            else:
                u, v = edge
                found = False
                for dom_edge in dom_set:
                    found |= u == dom_edge[0] or u == dom_edge[1]
                ok_(found, "Non adjacent edge found!")

        graph = nx.complete_graph(10)
        dom_set = apxa.min_edge_dominating_set(graph)

        # this is a crappy way to test, but good enough for now.
        for edge in graph.edges_iter():
            if edge in dom_set:
                continue
            else:
                u, v = edge
                found = False
                for dom_edge in dom_set:
                    found |= u == dom_edge[0] or u == dom_edge[1]
                ok_(found, "Non adjacent edge found!")
