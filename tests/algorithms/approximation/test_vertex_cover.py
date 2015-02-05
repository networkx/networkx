#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from  networkx.algorithms import approximation as a

class TestMWVC:

    def test_min_vertex_cover(self):
        # create a simple star graph
        size = 50
        sg = nx.star_graph(size)
        cover = a.min_weighted_vertex_cover(sg)
        assert_equals(2, len(cover))
        for u, v in sg.edges_iter():
            ok_((u in cover or v in cover), "Node node covered!")

        wg = nx.Graph()
        wg.add_node(0, weight=10)
        wg.add_node(1, weight=1)
        wg.add_node(2, weight=1)
        wg.add_node(3, weight=1)
        wg.add_node(4, weight=1)

        wg.add_edge(0, 1)
        wg.add_edge(0, 2)
        wg.add_edge(0, 3)
        wg.add_edge(0, 4)

        wg.add_edge(1,2)
        wg.add_edge(2,3)
        wg.add_edge(3,4)
        wg.add_edge(4,1)

        cover = a.min_weighted_vertex_cover(wg, weight="weight")
        csum = sum(wg.node[node]["weight"] for node in cover)
        assert_equals(4, csum)

        for u, v in wg.edges_iter():
            ok_((u in cover or v in cover), "Node node covered!")
