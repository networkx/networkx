#!/usr/bin/env python
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from nose.tools import *
import networkx as nx
import networkx.readwrite.graph6 as g6
from networkx.testing.utils import *

class TestGraph6Utils(object):

    def test_n_data_n_conversion(self):
        for i in [0, 1, 42, 62, 63, 64, 258047, 258048, 7744773, 68719476735]:
            assert_equal(g6.data_to_n(g6.n_to_data(i))[0], i)
            assert_equal(g6.data_to_n(g6.n_to_data(i))[1], [])
            assert_equal(g6.data_to_n(g6.n_to_data(i) + [42, 43])[1],
                         [42, 43])

    def test_data_sparse6_data_conversion(self):
        for data in [[], [0], [63], [63, 63], [0]*42,
                     [0, 1, 62, 42, 3, 11, 0, 11]]:
            assert_equal(g6.graph6_to_data(g6.data_to_graph6(data)), data)
            assert_equal(len(g6.data_to_graph6(data)), len(data))


class TestGraph6(object):

    def test_parse_graph6(self):
        data="""DF{"""
        G=nx.parse_graph6(data)
        assert_nodes_equal(G.nodes(),[0, 1, 2, 3, 4])
        assert_edges_equal(G.edges(),
                     [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])

    def test_read_graph6(self):
        data="""DF{"""
        G=nx.parse_graph6(data)
        fh = StringIO(data)
        Gin=nx.read_graph6(fh)
        assert_nodes_equal(G.nodes(),Gin.nodes())
        assert_edges_equal(G.edges(),Gin.edges())

    def test_read_many_graph6(self):
        # Read many graphs into list
        data="""DF{\nD`{\nDqK\nD~{\n"""
        fh = StringIO(data)
        glist=nx.read_graph6(fh)
        assert_equal(len(glist),4)
        for G in glist:
            assert_equal(sorted(G.nodes()),[0, 1, 2, 3, 4])

    def test_generate_graph6(self):
        assert_equal(nx.generate_graph6(nx.empty_graph(0)), '>>graph6<<?')
        assert_equal(nx.generate_graph6(nx.empty_graph(1)), '>>graph6<<@')

        G1 = nx.complete_graph(4)
        assert_equal(nx.generate_graph6(G1, header=True), '>>graph6<<C~')
        assert_equal(nx.generate_graph6(G1, header=False), 'C~')

        G2 = nx.complete_bipartite_graph(6,9)
        assert_equal(nx.generate_graph6(G2, header=False),
                     'N??F~z{~Fw^_~?~?^_?') # verified by Sage

        G3 = nx.complete_graph(67)
        assert_equal(nx.generate_graph6(G3, header=False),
                     '~?@B' + '~' * 368 + 'w')

    def test_write_graph6(self):
        fh = StringIO()
        nx.write_graph6(nx.complete_bipartite_graph(6,9), fh)
        fh.seek(0)
        assert_equal(fh.read(), '>>graph6<<N??F~z{~Fw^_~?~?^_?\n')

    def test_generate_and_parse_graph6(self):
        for i in list(range(13)) + [31, 47, 62, 63, 64, 72]:
            g = nx.random_graphs.gnm_random_graph(i, i * i // 4, seed=i)
            gstr = nx.generate_graph6(g, header=False)
            assert_equal(len(gstr),
                         ((i-1) * i // 2 + 5) // 6 + (1 if i < 63 else 4))
            g2 = nx.parse_graph6(gstr)
            assert_equal(g2.order(), g.order())
            assert_edges_equal(g2.edges(), g.edges())

    @raises(nx.NetworkXError)
    def directed_raise(self):
        nx.generate_graph6(nx.DiGraph())
