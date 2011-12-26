from nose.tools import assert_equal, assert_raises, assert_not_equal
import networkx as nx
import io
import tempfile
import os
from networkx.readwrite.p2g import *
from networkx.testing import *


class TestP2G:

    def setUp(self):
        self.G=nx.Graph(name="test")
        e=[('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        self.G.add_edges_from(e)
        self.G.add_node('g')
        self.DG=nx.DiGraph(self.G)

    def test_read_p2g(self):
        s = b"""\
name
3 4
a
1 2
b

c
0 2
"""
        bytesIO = io.BytesIO(s)
        G = read_p2g(bytesIO)
(G.edges(),H.edges())
