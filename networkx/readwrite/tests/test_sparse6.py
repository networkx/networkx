#!/usr/bin/env python
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from nose.tools import *
import networkx as nx
import networkx.readwrite.sparse6 as sg6
import os,tempfile

class TestSparseGraph6(object):

    def test_parse_sparse6(self):
        data=""":Q___eDcdFcDeFcE`GaJ`IaHbKNbLM"""
        G=nx.parse_sparse6(data)
        assert_equal(sorted(G.nodes()),
                     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                      10, 11, 12, 13, 14, 15, 16, 17])
        assert_equal([e for e in sorted(G.edges())],
                     [(0, 1), (0, 2), (0, 3), (1, 12), (1, 14), (2, 13),
                      (2, 15), (3, 16), (3, 17), (4, 7), (4, 9), (4, 11),
                      (5, 6), (5, 8), (5, 9), (6, 10), (6, 11), (7, 8),
                      (7, 10), (8, 12), (9, 15), (10, 14), (11, 13),
                      (12, 16), (13, 17), (14, 17), (15, 16)])

    def test_parse_multigraph_graph(self):
        graph_data = ':An'
        G = nx.parse_sparse6(graph_data)
        assert_true(type(G), nx.Graph)
        multigraph_data = ':Ab'
        M = nx.parse_sparse6(multigraph_data)
        assert_true(type(M), nx.MultiGraph)

    def test_read_sparse6(self):
        data=""":Q___eDcdFcDeFcE`GaJ`IaHbKNbLM"""
        G=nx.parse_sparse6(data)
        fh = StringIO(data)
        Gin=nx.read_sparse6(fh)
        assert_equal(sorted(G.nodes()),sorted(Gin.nodes()))
        assert_equal(sorted(G.edges()),sorted(Gin.edges()))

    def test_read_many_graph6(self):
        # Read many graphs into list
        data=':Q___eDcdFcDeFcE`GaJ`IaHbKNbLM\n'+\
            ':Q___dCfDEdcEgcbEGbFIaJ`JaHN`IM'
        fh = StringIO(data)
        glist=nx.read_sparse6(fh)
        assert_equal(len(glist),2)
        for G in glist:
            assert_equal(sorted(G.nodes()),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                          10, 11, 12, 13, 14, 15, 16, 17])

    def test_generate_sparse6(self):
        # Checked against sage encoder
        assert_equal(nx.generate_sparse6(nx.empty_graph(0)), '>>sparse6<<:?')
        assert_equal(nx.generate_sparse6(nx.empty_graph(1)), '>>sparse6<<:@')
        assert_equal(nx.generate_sparse6(nx.empty_graph(5)), '>>sparse6<<:D')
        assert_equal(nx.generate_sparse6(nx.empty_graph(68)),
                     '>>sparse6<<:~?@C')
        assert_equal(nx.generate_sparse6(nx.empty_graph(258049)),
                     '>>sparse6<<:~~???~?@')

        G1 = nx.complete_graph(4)
        assert_equal(nx.generate_sparse6(G1, header=True),
                     '>>sparse6<<:CcKI')
        assert_equal(nx.generate_sparse6(G1, header=False), ':CcKI')

        # Padding testing
        assert_equal(nx.generate_sparse6(nx.path_graph(4), header=False),
                     ':Cdv')
        assert_equal(nx.generate_sparse6(nx.path_graph(5), header=False),
                     ':DaYn')
        assert_equal(nx.generate_sparse6(nx.path_graph(6), header=False),
                     ':EaYnN')
        assert_equal(nx.generate_sparse6(nx.path_graph(7), header=False),
                     ':FaYnL')
        assert_equal(nx.generate_sparse6(nx.path_graph(8), header=False),
                     ':GaYnLz')

    def test_write_sparse6(self):
        fh = StringIO()
        nx.write_sparse6(nx.complete_bipartite_graph(6,9), fh)
        fh.seek(0)
        assert_equal(fh.read(),
                     '>>sparse6<<:Nk?G`cJ?G`cJ?G`cJ?G`'+
                     'cJ?G`cJ?G`cJ?G`cJ?G`cJ?G`cJ\n')
        # Compared with sage


    def test_generate_and_parse_sparse6(self):
        for i in list(range(13)) + [31, 47, 62, 63, 64, 72]:
            m = min(2 * i, i * i // 2)
            g = nx.random_graphs.gnm_random_graph(i, m, seed=i)
            gstr = nx.generate_sparse6(g, header=False)
            g2 = nx.parse_sparse6(gstr)
            assert_equal(g2.order(), g.order())
            assert_equal(sorted(g2.edges()), sorted(g.edges()))

    @raises(nx.NetworkXError)
    def directed_error(self):
        nx.generate_sparse6(nx.DiGraph())
