# -*- coding: utf-8 -*-
"""
    Unit tests for adjlist.
"""

from nose.tools import assert_equal, assert_raises
import tempfile
import networkx as nx
import sys

class TestAdjlist():
    def test_read_multiline_adjlist_1(self):
        # Unit test for https://networkx.lanl.gov/trac/ticket/252
        s = b"""# comment line
1 2
# comment line
2
3
"""
        import io
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

