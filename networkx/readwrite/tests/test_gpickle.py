#!/usr/bin/env python
from nose.tools import assert_equal
import networkx as nx
import os,tempfile

class TestGpickle(object):
    def setUp(self):
        G=nx.Graph(name="test")
        e=[('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        G.add_edges_from(e)
        G.add_node('g')
        self.G=G

    def test_gpickle(self):
        G=self.G
        (fd,fname)=tempfile.mkstemp()
        nx.write_gpickle(G,fname);  
        Gin=nx.read_gpickle(fname);
        assert_equal(sorted(G.nodes()),sorted(Gin.nodes()))
        assert_equal(sorted(G.edges()),sorted(Gin.edges()))
        os.close(fd)
        os.unlink(fname)

