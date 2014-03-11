#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from random import random, choice

# class TestMaxDegree:

#     def setUp(self):
#         print "test setup"

#     def test_random_graph(self):
#     	print "test random graph"
G = nx.Graph()

G.add_nodes_from([1,2,3,4,5,6,7])

G.add_edges_from([
	(1,2),
	(1,5),
	(1,6),
	(2,3),
	(2,7),
	(3,4),
	(3,7),
	(4,5),
	(4,6),
	(5,6)
])

print nx.coloring(G, strategy='gis')