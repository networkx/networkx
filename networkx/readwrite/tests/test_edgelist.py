"""
    Unit tests for edgelists.
"""

from nose.tools import assert_equal, assert_raises
import networkx as nx
import io
import tempfile

def assert_equal_edges(elist1,elist2):
    if len(elist1[0]) == 2:
        return assert_equal(sorted(sorted(e) for e in elist1), 
                            sorted(sorted(e) for e in elist2))
    else:
        return assert_equal(sorted((sorted((u, v)), d) for u, v, d in elist1),
                            sorted((sorted((u, v)), d) for u, v, d in elist2))

class TestEdgelist:

    def test_read_edgelist_1(self):
        s = b"""\
# comment line
1 2
# comment line
2 3
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_edgelist(bytesIO,nodetype=int)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

    def test_read_edgelist_2(self):
        s = b"""\
# comment line
1 2 2.0
# comment line
2 3 3.0
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_edgelist(bytesIO,nodetype=int,data=False)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

        bytesIO = io.BytesIO(s)
        G = nx.read_weighted_edgelist(bytesIO,nodetype=int)
        assert_equal_edges(G.edges(data=True),[(1,2,{'weight':2.0}),(2,3,{'weight':3.0})])

    def test_read_edgelist_3(self):
        s = b"""\
# comment line
1 2 {'weight':2.0}
# comment line
2 3 {'weight':3.0}
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_edgelist(bytesIO,nodetype=int,data=False)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

        bytesIO = io.BytesIO(s)
        G = nx.read_edgelist(bytesIO,nodetype=int,data=True)
        assert_equal_edges(G.edges(data=True),[(1,2,{'weight':2.0}),(2,3,{'weight':3.0})])

    def test_write_edgelist_1(self):
        fh=io.BytesIO()
        G=nx.Graph()
        G.add_edges_from([(1,2),(2,3)])
        nx.write_edgelist(G,fh,data=False)
        fh.seek(0)
        assert_equal(fh.read(),b"1 2\n2 3\n")

    def test_write_edgelist_2(self):
        fh=io.BytesIO()
        G=nx.Graph()
        G.add_edges_from([(1,2),(2,3)])
        nx.write_edgelist(G,fh,data=True)
        fh.seek(0)
        assert_equal(fh.read(),b"1 2 {}\n2 3 {}\n")

    def test_write_edgelist_3(self):
        fh=io.BytesIO()
        G=nx.Graph()
        G.add_edge(1,2,weight=2.0)
        G.add_edge(2,3,weight=3.0)
        nx.write_edgelist(G,fh,data=True)
        fh.seek(0)
        assert_equal(fh.read(),b"1 2 {'weight': 2.0}\n2 3 {'weight': 3.0}\n")

    def test_write_edgelist_4(self):
        fh=io.BytesIO()
        G=nx.Graph()
        G.add_edge(1,2,weight=2.0)
        G.add_edge(2,3,weight=3.0)
        nx.write_edgelist(G,fh,data=[('weight')])
        fh.seek(0)
        assert_equal(fh.read(),b"1 2 2.0\n2 3 3.0\n")

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
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname)
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
                      nx.write_edgelist,
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
        nx.write_edgelist(G, fname, encoding = 'latin-1')
        H = nx.read_edgelist(fname, encoding = 'latin-1')
        assert_equal(G.adj, H.adj)




