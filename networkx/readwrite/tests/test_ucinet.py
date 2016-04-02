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
                                ('b', 'a'), ('b', 'c'), ('b', 'd'),
                                ('c', 'a'), ('c', 'b'),
                                ('d', 'a'), ('d', 'b'),
                                ('e', 'a')])

    def test_generate_ucinet(self):
        Gout = nx.readwrite.generate_ucinet(self.G)
        s = ''
        for line in Gout:
            s += line + '\n'
        G_generated = nx.readwrite.parse_ucinet(s)

        data = """\
dl n=5 format=fullmatrix
labels:
a,b,c,d,e
data:
0 1 1 1 1
1 0 1 1 0
1 1 0 0 0
1 1 0 0 0
1 0 0 0 0"""
        G = nx.readwrite.parse_ucinet(data)

        assert_equal(sorted(G.nodes()), sorted(G_generated.nodes()))
        assert_edges_equal(G.edges(), G_generated.edges())

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
        graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4),
                              (1, 0), (1, 2),
                              (2, 0), (2, 1), (2, 4),
                              (3, 0),
                              (4, 0), (4, 2)])
        G = nx.readwrite.parse_ucinet(data)
        assert_equal(sorted(G.nodes()), sorted(graph.nodes()))
        assert_edges_equal(G.edges(), graph.edges())
        # print [n for n in G.nodes(data=True)]
        # print [e for e in G.edges()]

    def test_parse_ucinet_labels(self):
        """
        Test parsing of labels : single line (data1), multiple lines (data2), embedded (data3)

        Labels must be separated by spaces, carriage returns, equal signs or commas.
        Labels with embedded spaces are not advisable, but can be entered by
        surrounding the label in quotes (e.g., "Humpty Dumpty").
        """
        data1 = """
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
        data2 = """
dl n=5
format = fullmatrix
labels:
barry,david
lin,pat
russ
data:
0 1 1 1 0
1 0 0 0 1
1 0 0 1 0
1 0 1 0 1
0 1 0 1 0
        """
        data3 = """\
dl n=5
format = fullmatrix
labels embedded
data:
barry david lin pat russ
Barry 0 1 1 1 0
david 1 0 0 0 1
Lin 1 0 0 1 0
Pat 1 0 1 0 1
Russ 0 1 0 1 0
        """
        G = nx.MultiDiGraph()
        G.add_nodes_from(['russ', 'barry', 'lin', 'pat', 'david'])
        G.add_edges_from([('russ', 'pat'), ('russ', 'david'),
                            ('barry', 'lin'), ('barry', 'pat'), ('barry', 'david'),
                            ('lin', 'barry'), ('lin', 'pat'),
                            ('pat', 'barry'), ('pat', 'lin'), ('pat', 'russ'),
                            ('david', 'barry'), ('david', 'russ')])
        G1 = nx.readwrite.parse_ucinet(data1)
        G2 = nx.readwrite.parse_ucinet(data2)
        G3 = nx.readwrite.parse_ucinet(data3)
        assert_equal(sorted(G1.nodes()), sorted(G.nodes()))
        assert_equal(sorted(G2.nodes()), sorted(G.nodes()))
        assert_equal(sorted(G3.nodes()), sorted(G.nodes()))
        assert_edges_equal(G1.edges(), G.edges())
        assert_edges_equal(G2.edges(), G.edges())
        assert_edges_equal(G3.edges(), G.edges())
        # print [n for n in G.nodes()]
        # print [e for e in G.edges()]

    def test_parse_ucinet_nodelist1(self):
        data1 = """
DL n=4
format = nodelist1
data:
  1  3 2 1
  4  1 4
  2  2 4 1
        """
        data2 = """
DL n=4
format = nodelist1b
data:
  3  1 2 3
  3  1 2 4
  0
  2  1 4
        """
        G = nx.MultiDiGraph()
        G.add_nodes_from([1, 2, 3, 4])
        G.add_edges_from([(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 4), (4, 1), (4, 4)])
        G1 = nx.readwrite.parse_ucinet(data1)
        G2 = nx.readwrite.parse_ucinet(data2)
        assert_equal(sorted(G1.nodes()), sorted(G.nodes()))
        assert_equal(sorted(G2.nodes()), sorted(G.nodes()))
        assert_edges_equal(G1.edges(), G.edges())
        assert_edges_equal(G2.edges(), G.edges())

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
        graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4),
                              (1, 0), (1, 2),
                              (2, 0), (2, 1), (2, 4),
                              (3, 0),
                              (4, 0), (4, 2)])

        nx.readwrite.write_ucinet(graph, fh)
        fh.seek(0)
        G = nx.readwrite.parse_ucinet(fh.readlines())

        assert_equal(sorted(G.nodes()), sorted(graph.nodes()))
        assert_edges_equal(G.edges(), graph.edges())
