"""
    Unit tests for yaml.
"""

import os,tempfile
from nose import SkipTest

import networkx as nx

class TestYaml(object):
    @classmethod
    def setupClass(cls):
        global yaml
        try:
            import yaml
            # Because NetworkX uses a lazy import, this might work.
            # To really test it, we need to use it.
            yaml.__file__
        except ImportError:
            raise SkipTest('yaml not available.')

        self.build_graphs()

    def build_graphs(self):
        self.G = nx.Graph(name="test")
        e = [('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        self.G.add_edges_from(e)
        self.G.add_node('g')    

        self.DG = nx.DiGraph(G)

        self.XG = nx.MultiGraph()
        self.XG.add_weighted_edges_from([(1,2,5),(1,2,5),(1,2,1),(3,3,42)])

    def assert_equal(self, G, data=False):
        (fd, fname) = tempfile.mkstemp()
        nx.write_yaml(G, fname)
        Gin = read_yaml(fname);

        assert_true( sorted(G.nodes())==sorted(Gin.nodes()) )
        assert_true( sorted(G.edges(data=data))==sorted(Gin.edges(data=data)) )

        os.close(fd)
        os.unlink(fname)
   
    def testUndirected(self):
        self.assert_equal(self.G, False)

    def testDirected(self):
        self.assert_equal(self.DG, False)

    def testMultiGraph(self):
        self.assert_equal(self.MG, True)

