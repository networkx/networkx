# -*- coding: utf-8 -*-
"""
    Unit tests for adjlist.
"""
import io
from nose.tools import assert_equal, assert_raises, assert_not_equal
import os
import tempfile
import networkx as nx
from networkx.testing import *


class TestAdjlist():

    def setUp(self):
        self.G=nx.Graph(name="test")
        e=[('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        self.G.add_edges_from(e)
        self.G.add_node('g')
        self.DG=nx.DiGraph(self.G)
        self.XG=nx.MultiGraph()
        self.XG.add_weighted_edges_from([(1,2,5),(1,2,5),(1,2,1),(3,3,42)])
        self. XDG=nx.MultiDiGraph(self.XG)

    def test_read_multiline_adjlist_1(self):
        # Unit test for https://networkx.lanl.gov/trac/ticket/252
        s = b"""# comment line
1 2
# comment line
2
3
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_multiline_adjlist(bytesIO)
        adj = {'1': {'3': {}, '2': {}}, '3': {'1': {}}, '2': {'1': {}}}
        assert_equal(G.adj, adj)

    def test_unicode(self):
        G = nx.Graph()
        try: # Python 3.x
            name1 = chr(2344) + chr(123) + chr(6543)
            name2 = chr(5543) + chr(1543) + chr(324)
        except ValueError: # Python 2.6+
            name1 = unichr(2344) + unichr(123) + unichr(6543)
            name2 = unichr(5543) + unichr(1543) + unichr(324)
        G.add_edge(name1, 'Radiohead', {name2: 3})
        fd, fname = tempfile.mkstemp()
        nx.write_multiline_adjlist(G, fname)
        H = nx.read_multiline_adjlist(fname)
        assert_equal(G.adj, H.adj)
        os.close(fd)
        os.unlink(fname)

    def test_latin1_error(self):
        G = nx.Graph()
        try: # Python 3.x
            name1 = chr(2344) + chr(123) + chr(6543)
            name2 = chr(5543) + chr(1543) + chr(324)
        except ValueError: # Python 2.6+
            name1 = unichr(2344) + unichr(123) + unichr(6543)
            name2 = unichr(5543) + unichr(1543) + unichr(324)
        G.add_edge(name1, 'Radiohead', {name2: 3})
        fd, fname = tempfile.mkstemp()
        assert_raises(UnicodeEncodeError,
                      nx.write_multiline_adjlist,
                      G, fname, encoding = 'latin-1')
        os.close(fd)
        os.unlink(fname)

    def test_latin1(self):
        G = nx.Graph()
        try: # Python 3.x
            blurb = chr(1245) # just to trigger the exception
            name1 = 'Bj' + chr(246) + 'rk'
            name2 = chr(220) + 'ber'
        except ValueError: # Python 2.6+
            name1 = 'Bj' + unichr(246) + 'rk'
            name2 = unichr(220) + 'ber'
        G.add_edge(name1, 'Radiohead', {name2: 3})
        fd, fname = tempfile.mkstemp()
        nx.write_multiline_adjlist(G, fname, encoding = 'latin-1')
        H = nx.read_multiline_adjlist(fname, encoding = 'latin-1')
        assert_equal(G.adj, H.adj)
        os.close(fd)
        os.unlink(fname)



    def test_adjlist_graph(self):
        G=self.G
        (fd,fname)=tempfile.mkstemp()
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname)
        H2=nx.read_adjlist(fname)
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_adjlist_digraph(self):
        G=self.DG
        (fd,fname)=tempfile.mkstemp()
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname,create_using=nx.DiGraph())
        H2=nx.read_adjlist(fname,create_using=nx.DiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_adjlist_integers(self):
        (fd,fname)=tempfile.mkstemp()
        G=nx.convert_node_labels_to_integers(self.G)
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname,nodetype=int)
        H2=nx.read_adjlist(fname,nodetype=int)
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_adjlist_digraph(self):
        G=self.DG
        (fd,fname)=tempfile.mkstemp()
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname,create_using=nx.DiGraph())
        H2=nx.read_adjlist(fname,create_using=nx.DiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_adjlist_multigraph(self):
        G=self.XG
        (fd,fname)=tempfile.mkstemp()
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname,nodetype=int,
                          create_using=nx.MultiGraph())
        H2=nx.read_adjlist(fname,nodetype=int,
                           create_using=nx.MultiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_adjlist_multidigraph(self):
        G=self.XDG
        (fd,fname)=tempfile.mkstemp()
        nx.write_adjlist(G,fname)
        H=nx.read_adjlist(fname,nodetype=int,
                          create_using=nx.MultiDiGraph())
        H2=nx.read_adjlist(fname,nodetype=int,
                           create_using=nx.MultiDiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_adjlist_delimiter(self):
        fh=io.BytesIO()
        G = nx.path_graph(3)
        nx.write_adjlist(G, fh, delimiter=':')
        fh.seek(0)
        H = nx.read_adjlist(fh, nodetype=int, delimiter=':')
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))






class TestMultilineAdjlist():

    def setUp(self):
        self.G=nx.Graph(name="test")
        e=[('a','b'),('b','c'),('c','d'),('d','e'),('e','f'),('a','f')]
        self.G.add_edges_from(e)
        self.G.add_node('g')
        self.DG=nx.DiGraph(self.G)
        self.DG.remove_edge('b','a')
        self.DG.remove_edge('b','c')
        self.XG=nx.MultiGraph()
        self.XG.add_weighted_edges_from([(1,2,5),(1,2,5),(1,2,1),(3,3,42)])
        self. XDG=nx.MultiDiGraph(self.XG)


    def test_multiline_adjlist_graph(self):
        G=self.G
        (fd,fname)=tempfile.mkstemp()
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname)
        H2=nx.read_multiline_adjlist(fname)
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_multiline_adjlist_digraph(self):
        G=self.DG
        (fd,fname)=tempfile.mkstemp()
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname,create_using=nx.DiGraph())
        H2=nx.read_multiline_adjlist(fname,create_using=nx.DiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_multiline_adjlist_integers(self):
        (fd,fname)=tempfile.mkstemp()
        G=nx.convert_node_labels_to_integers(self.G)
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname,nodetype=int)
        H2=nx.read_multiline_adjlist(fname,nodetype=int)
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)


    def test_multiline_adjlist_digraph(self):
        G=self.DG
        (fd,fname)=tempfile.mkstemp()
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname,create_using=nx.DiGraph())
        H2=nx.read_multiline_adjlist(fname,create_using=nx.DiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_edges_equal(H.edges(),G.edges())
        os.close(fd)
        os.unlink(fname)


    def test_multiline_adjlist_multigraph(self):
        G=self.XG
        (fd,fname)=tempfile.mkstemp()
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname,nodetype=int,
                                    create_using=nx.MultiGraph())
        H2=nx.read_multiline_adjlist(fname,nodetype=int,
                                     create_using=nx.MultiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_multiline_adjlist_multidigraph(self):
        G=self.XDG
        (fd,fname)=tempfile.mkstemp()
        nx.write_multiline_adjlist(G,fname)
        H=nx.read_multiline_adjlist(fname,nodetype=int,
                                    create_using=nx.MultiDiGraph())
        H2=nx.read_multiline_adjlist(fname,nodetype=int,
                                     create_using=nx.MultiDiGraph())
        assert_not_equal(H,H2) # they should be different graphs
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_multiline_adjlist_delimiter(self):
        fh=io.BytesIO()
        G = nx.path_graph(3)
        nx.write_multiline_adjlist(G, fh, delimiter=':')
        fh.seek(0)
        H = nx.read_multiline_adjlist(fh, nodetype=int, delimiter=':')
        assert_equal(sorted(H.nodes()),sorted(G.nodes()))
        assert_equal(sorted(H.edges()),sorted(G.edges()))
