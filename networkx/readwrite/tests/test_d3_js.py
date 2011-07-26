#!/usr/bin/env python
# encoding: utf-8
"""
test_d3_js.py

Unit test for d3_js

Created by Drew Conway on 2011-07-26.
"""

import unittest
import networkx as nx
from networkx.readwrite import d3_js
import io
import tempfile
import os

class test_d3_js(unittest.TestCase):
	
	def setUp(self):
		self.e=[(0,1), (0,5), (1,2), (2,3), (3,4), (4,5)]
		self.attributes = range(6)
		self.G=nx.DiGraph(name="test")
		self.G.add_edges_from(self.e)
		self.H=nx.DiGraph()
		self.H.add_nodes_from(map(lambda v: (v, {'group' : self.attributes[v]}), xrange(self.G.number_of_nodes())))
		self.H.add_edges_from(map(lambda i: (self.e[i][0], self.e[i][1], {'weight' : self.attributes[i]}), xrange(len(self.e))))

	def test_d3_json1(self):
		G_json=d3_js.d3_json(self.G)
		G_nodes=map(lambda v: int(v['name']), G_json['nodes'])
		G_nodes.sort()
		self.assertEquals(G_nodes, range(6))
		G_group=map(lambda v: int(v['group']), G_json['nodes'])
		self.assertTrue(all(g == 0 for g in G_group))
		G_edges=map(lambda e: (e['source'], e['target'], e['value']), G_json['links'])
		G_edges.sort()
		self.assertEquals(G_edges, [(a,b,1) for (a,b) in self.e])
		
	def test_d3_json2(self):
		H_json=d3_js.d3_json(self.H, group='group')
		self.assertRaises(nx.NetworkXError, d3_js.d3_json, self.H, 'fake')
		H_nodes=map(lambda v: int(v['name']), H_json['nodes'])
		H_nodes.sort()
		self.assertEquals(H_nodes, range(6))
		H_group=map(lambda v: int(v['group']), H_json['nodes'])
		self.assertEquals(H_group, range(6))
		H_edges=map(lambda e: (e['source'], e['target'], e['value']), H_json['links'])
		H_edges.sort()
		self.assertEquals(H_edges, map(lambda i: (self.e[i][0], self.e[i][1], self.attributes[i]), xrange(6)))
		
		

if __name__ == '__main__':
	unittest.main()