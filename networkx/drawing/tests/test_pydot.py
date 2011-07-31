"""
    Unit tests for pydot drawing functions.
"""

import os
import tempfile

from nose import SkipTest
from nose.tools import assert_true

import networkx as nx

class TestPydot(object):
    @classmethod
    def setupClass(cls):
        global pydot
        try:
            import pydot
        except ImportError:
            raise SkipTest('pydot not available.')

    def build_graph(self, G):
        G.add_edge('A','B')
        G.add_edge('A','C')
        G.add_edge('B','C')
        G.add_edge('A','D')
        G.add_node('E')
        return G, nx.to_pydot(G)

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes())==sorted(G2.nodes()) )
        assert_true( sorted(G1.edges())==sorted(G2.edges()) )

    def pydot_checks(self, G):
        H, P = self.build_graph(G)
        G2 = H.__class__(nx.from_pydot(P))
        self.assert_equal(H, G2)

        fname = tempfile.mktemp()
        assert_true( P.write_raw(fname) )

        Pin = pydot.graph_from_dot_file(fname)   

        n1 = sorted([p.get_name() for p in P.get_node_list()])
        n2 = sorted([p.get_name() for p in Pin.get_node_list()])
        assert_true( n1 == n2 )

        e1=[(e.get_source(),e.get_destination()) for e in P.get_edge_list()]
        e2=[(e.get_source(),e.get_destination()) for e in Pin.get_edge_list()]
        assert_true( sorted(e1)==sorted(e2) )

        Hin = nx.drawing.nx_pydot.read_dot(fname)
        Hin = H.__class__(Hin)
        self.assert_equal(H, Hin)
#        os.unlink(fname)


    def testUndirected(self):
        self.pydot_checks(nx.Graph())

    def testDirected(self):
        self.pydot_checks(nx.DiGraph())


