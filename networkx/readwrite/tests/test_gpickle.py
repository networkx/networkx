#!/usr/bin/env python
from nose.tools import assert_equal
import networkx as nx
import os,tempfile

class TestGpickle(object):
    def setUp(self):
        G=nx.Graph(name="test")
        e=[('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        G.add_edges_from(e,width=10)
        G.add_node('g',color='green')
        G.graph['number']=1
        self.G=G

    def test_gpickle(self):
        G=self.G
        (fd,fname)=tempfile.mkstemp()
        nx.write_gpickle(G,fname);  
        Gin=nx.read_gpickle(fname);
        assert_equal(sorted(G.nodes(data=True)),
                     sorted(Gin.nodes(data=True)))
        assert_equal(sorted(G.edges(data=True)),
                     sorted(Gin.edges(data=True)))
        assert_equal(G.graph,Gin.graph)
        os.close(fd)
        os.unlink(fname)

