#!/usr/bin/env python
"""
UCINET tests
"""
import io
from nose.tools import *
import networkx as nx
from networkx.testing import *


class TestUcinet(object):
    def setUp(self):
        self.G = nx.MultiDiGraph()
        self.G.add_nodes_from(['a', 'b', 'c', 'd', 'e'])
        self.G.add_edges_from([('a', 'b'), ('a', 'c'), ('a', 'd'), ('a', 'e'),
                                ('b', 'a'), ('b', 'c'),
                                ('c', 'a'), ('c', 'b'), ('c', 'e'),
                                ('d', 'a'),
                                ('e', 'a'), ('e', 'c')])

    def test_generate_ucinet(self):
        Gout = nx.readwrite.generate_ucinet(self.G)
        for line in Gout:
            print line

    def test_parse_ucinet(self):
        data = """
DL N = 5
Data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0
        """
        graph = nx.MultiDiGraph()
        graph.add_nodes_from([0, 1, 2, 3, 4])
        graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 1), (2, 4), (3, 0), (4, 0), (4, 2)])
        G = nx.readwrite.parse_ucinet(data)
        assert_equal(sorted(G.nodes()), sorted(graph.nodes()))
        assert_edges_equal(G.edges(), graph.edges())
        # print [n for n in G.nodes(data=True)]
        # print [e for e in G.edges()]

    def test_parse_ucinet_labels(self):
        data = """
dl n=5
format = fullmatrix
labels:
barry,david,lin,pat,russ
data:
0 1 1 1 0
1 0 0 0 1
1 0 0 1 0
1 0 1 0 1
0 1 0 1 0
                """
        G = nx.readwrite.parse_ucinet(data)
        assert_equal(sorted(G.nodes()), sorted(['russ', 'barry', 'lin', 'pat', 'david']))
        assert_edges_equal(G.edges(), [('russ', 'pat'), ('russ', 'david'), ('barry', 'lin'), ('barry', 'pat'), ('barry', 'david'), ('lin', 'barry'), ('lin', 'pat'), ('pat', 'barry'), ('pat', 'lin'), ('pat', 'russ'), ('david', 'barry'), ('david', 'russ')])
        # print [n for n in G.nodes()]
        # print [e for e in G.edges()]

    def test_read_ucinet(self):
        fh = io.BytesIO()
        data = """
DL N = 5
Data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0
        """
        Gin = nx.readwrite.parse_ucinet(data)
        fh.write(data.encode('UTF-8'))
        fh.seek(0)
        Gout = nx.readwrite.read_ucinet(fh)
        assert_equal(sorted(Gout.nodes()), sorted(Gin.nodes()))
        assert_equal(sorted(Gout.edges()), sorted(Gin.edges()))

    def test_write_ucinet(self):
        fh = io.BytesIO()
        data = """\
dl n=5 format=fullmatrix
data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0
"""
        graph = nx.MultiDiGraph()
        graph.add_nodes_from([0, 1, 2, 3, 4])
        graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 1), (2, 4), (3, 0), (4, 0), (4, 2)])
        nx.readwrite.write_ucinet(graph, fh)
        fh.seek(0)
        assert_equal(fh.read(), data)
