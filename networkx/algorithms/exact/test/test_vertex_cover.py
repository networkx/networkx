#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import sys
sys.path.append('..')
from exact_minimum_vertex_cover import *

def test_min_vertex_cover():
        # create a simple star graph
        size = 50
        sg = nx.star_graph(size)
        cover = min_vertex_cover(sg)
        assert_equals(1, len(cover))
        for u, v in sg.edges_iter():
            ok_((u in cover or v in cover), "Node node covered!")

        wg = nx.Graph()
        wg.add_node(0)
        wg.add_node(1)
        wg.add_node(2)
        wg.add_node(3)
        wg.add_node(4)

        wg.add_edge(0, 1)
        wg.add_edge(0, 2)
        wg.add_edge(0, 3)
        wg.add_edge(0, 4)

        wg.add_edge(1,2)
        wg.add_edge(2,3)
        wg.add_edge(3,4)
        wg.add_edge(4,1)

        cover = min_vertex_cover(wg)
        
        assert_equals(3, len(cover))

        for u, v in wg.edges_iter():
            ok_((u in cover or v in cover), "Node node covered!")

