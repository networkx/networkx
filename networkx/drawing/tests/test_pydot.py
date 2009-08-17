"""
    Unit tests for pydot drawing functions.
"""

import os, sys
import tempfile

from nose import SkipTest
from nose.tools import assert_true

import networkx as nx
from networkx.drawing import nx_pydot

class TestPydot(object):
    def setUp(self):
        global pydot
        try:
            import pydot
            # Because NetworkX uses a lazy import, this might work.
            # To really test it, we need to use it.
            pydot.__file__
        except ImportError:
            raise SkipTest('pydot not available.')

        self.H1, self.P1 = self.build_graph(nx.Graph())
        self.H2, self.P2 = self.build_graph(nx.DiGraph())

    def build_graph(self, G):
        G.add_edge('A','B')
        G.add_edge('A','C')
        G.add_edge('B','C')
        G.add_edge('A','D')
        G.add_node('E')
        return G, nx_pydot.to_pydot(G)

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes())==sorted(G2.nodes()) )
        assert_true( sorted(G1.edges())==sorted(G2.edges()) )

    def pydot_checks(self, H, P):
        fname = tempfile.mktemp()
        assert_true( P.write_raw(fname) )

        Pin = pydot.graph_from_dot_file(fname)   
        n1 = sorted([p.get_name() for p in P.get_node_list()])
        n2 = sorted([p.get_name() for p in Pin.get_node_list()])
        assert_true( n1 == n2 )

        e1=[(e.get_source(),e.get_destination()) for e in P.get_edge_list()]
        e2=[(e.get_source(),e.get_destination()) for e in Pin.get_edge_list()]
        assert_true( sorted(e1)==sorted(e2) )

        Hin = nx_pydot.read_dot(fname)
        Hin = H.__class__(Hin)
        self.assert_equal(H, Hin)
        os.unlink(fname)

    def testUndirected(self):
        G = nx.Graph(nx_pydot.from_pydot(self.P1))
        self.assert_equal(self.H1, G)
        self.pydot_checks(self.H1, self.P1)

    def testDirected(self):
        G = nx.DiGraph(nx_pydot.from_pydot(self.P2))
        self.assert_equal(self.H2, G)
        self.pydot_checks(self.H2, self.P2)


