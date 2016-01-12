"""
    Unit tests for pydot drawing functions.
"""
import os
import tempfile

from nose import SkipTest
from nose.tools import assert_true

import networkx as nx
from networkx.testing import assert_graphs_equal

class TestPydot(object):
    @classmethod
    def setupClass(cls):
        global pydotplus
        try:
            import pydotplus
        except ImportError:
            raise SkipTest('pydotplus not available.')

    def pydot_checks(self, G):
        G.add_edge('A','B')
        G.add_edge('A','C')
        G.add_edge('B','C')
        G.add_edge('A','D')
        G.add_node('E')
        P = nx.nx_pydot.to_pydot(G)
        G2 = G.__class__(nx.nx_pydot.from_pydot(P))
        assert_graphs_equal(G, G2)

        fname = tempfile.mktemp()
        assert_true( P.write_raw(fname) )

        Pin = pydotplus.graph_from_dot_file(fname)

        n1 = sorted([p.get_name() for p in P.get_node_list()])
        n2 = sorted([p.get_name() for p in Pin.get_node_list()])
        assert_true( n1 == n2 )

        e1=[(e.get_source(),e.get_destination()) for e in P.get_edge_list()]
        e2=[(e.get_source(),e.get_destination()) for e in Pin.get_edge_list()]
        assert_true( sorted(e1)==sorted(e2) )

        Hin = nx.nx_pydot.read_dot(fname)
        Hin = G.__class__(Hin)
        assert_graphs_equal(G, Hin)

#        os.unlink(fname)


    def testUndirected(self):
        self.pydot_checks(nx.Graph())

    def testDirected(self):
        self.pydot_checks(nx.DiGraph())
