#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import sys
sys.path.append('..')
from exact_minimum_dominating_set import*
def test_min_dominating_set():
        graph = nx.Graph()
        graph.add_edge(1, 2)
        graph.add_edge(1, 5)
        graph.add_edge(2, 3)
        graph.add_edge(2, 5)
        graph.add_edge(3, 4)
        graph.add_edge(3, 6)
        graph.add_edge(5, 6)
        G=graph.copy()
        vertices = set([1, 2, 3, 4, 5, 6])
        # due to ties, this might be hard to test tight bounds
        dom_set = set(minimum_dominating_set(graph))
        for vertex in vertices - dom_set:
            neighbors = set(G.neighbors(vertex))
            ok_(len(neighbors & dom_set) > 0, "Non dominating set found!")

