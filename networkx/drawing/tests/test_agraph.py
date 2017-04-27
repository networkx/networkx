"""Unit tests for PyGraphviz inteface."""
import os
import tempfile
from nose import SkipTest
from nose.tools import assert_true,assert_equal
import networkx as nx


class TestAGraph(object):
    @classmethod
    def setupClass(cls):
        global pygraphviz
        try:
            import pygraphviz
        except ImportError:
            raise SkipTest('PyGraphviz not available.')

    def build_graph(self, G):
        G.add_edges_from([('A','B'),('A','C'),('A','C'),('B','C'),('A','D')])
        G.add_node('E')
        return G

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes()) == sorted(G2.nodes()) )
        assert_true( sorted(G1.edges()) == sorted(G2.edges()) )

    def agraph_checks(self, G):
        G = self.build_graph(G)
        A = nx.nx_agraph.to_agraph(G)
        H = nx.nx_agraph.from_agraph(A)
        self.assert_equal(G, H)

        fname = tempfile.mktemp()
        nx.drawing.nx_agraph.write_dot(H, fname)
        Hin = nx.nx_agraph.read_dot(fname)
        os.unlink(fname)
        self.assert_equal(H, Hin)

        (fd,fname) = tempfile.mkstemp()
        with open(fname, 'w') as fh:
            nx.drawing.nx_agraph.write_dot(H, fh)

        with open(fname, 'r') as fh:
            Hin = nx.nx_agraph.read_dot(fh)
        os.unlink(fname)
        self.assert_equal(H, Hin)

    def test_from_agraph_name(self):
        G = nx.Graph(name='test')
        A = nx.nx_agraph.to_agraph(G)
        H = nx.nx_agraph.from_agraph(A)
        assert_equal(G.name, 'test')

    def testUndirected(self):
        self.agraph_checks(nx.Graph())

    def testDirected(self):
        self.agraph_checks(nx.DiGraph())

    def testMultiUndirected(self):
        self.agraph_checks(nx.MultiGraph())

    def testMultiDirected(self):
        self.agraph_checks(nx.MultiDiGraph())
