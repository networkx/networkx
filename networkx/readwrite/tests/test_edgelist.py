"""
    Unit tests for edgelists.
"""

from nose.tools import assert_equal
import networkx as nx

def assert_equal_edges(elist1,elist2):
    return assert_equal(sorted(sorted(e) for e in elist1), 
                        sorted(sorted(e) for e in elist2))
class TestEdgelist:

    def test_read_adjlist_1(self):
        import StringIO
        s = """\
# comment line
1 2
# comment line
2 3
"""
        strIO = StringIO.StringIO(s)
        G = nx.read_edgelist(strIO,nodetype=int)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

    def test_read_adjlist_2(self):
        import StringIO
        s = """\
# comment line
1 2 2.0
# comment line
2 3 3.0
"""
        strIO = StringIO.StringIO(s)
        G = nx.read_edgelist(strIO,nodetype=int,data=False)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

        strIO = StringIO.StringIO(s)
        G = nx.read_weighted_edgelist(strIO,nodetype=int)
        assert_equal_edges(G.edges(data=True),[(1,2,{'weight':2.0}),(2,3,{'weight':3.0})])

    def test_read_adjlist_3(self):
        import StringIO
        s = """\
# comment line
1 2 {'weight':2.0}
# comment line
2 3 {'weight':3.0}
"""
        strIO = StringIO.StringIO(s)
        G = nx.read_edgelist(strIO,nodetype=int,data=False)
        assert_equal_edges(G.edges(),[(1,2),(2,3)])

        strIO = StringIO.StringIO(s)
        G = nx.read_edgelist(strIO,nodetype=int,data=True)
        assert_equal_edges(G.edges(data=True),[(1,2,{'weight':2.0}),(2,3,{'weight':3.0})])

    def test_write_adjlist_1(self):
        import StringIO
        fh=StringIO.StringIO()
        G=nx.Graph()
        G.add_edges_from([(1,2),(2,3)])
        nx.write_edgelist(G,fh,data=False)
        fh.seek(0)
        assert_equal(fh.read(),"1 2\n2 3\n")

    def test_write_adjlist_2(self):
        import StringIO
        fh=StringIO.StringIO()
        G=nx.Graph()
        G.add_edges_from([(1,2),(2,3)])
        nx.write_edgelist(G,fh,data=True)
        fh.seek(0)
        assert_equal(fh.read(),"1 2 {}\n2 3 {}\n")

    def test_write_adjlist_3(self):
        import StringIO
        fh=StringIO.StringIO()
        G=nx.Graph()
        G.add_edge(1,2,weight=2.0)
        G.add_edge(2,3,weight=3.0)
        nx.write_edgelist(G,fh,data=True)
        fh.seek(0)
        assert_equal(fh.read(),"1 2 {'weight': 2.0}\n2 3 {'weight': 3.0}\n")

    def test_write_adjlist_4(self):
        import StringIO
        fh=StringIO.StringIO()
        G=nx.Graph()
        G.add_edge(1,2,weight=2.0)
        G.add_edge(2,3,weight=3.0)
        nx.write_edgelist(G,fh,data=[('weight')])
        fh.seek(0)
        assert_equal(fh.read(),"1 2 2.0\n2 3 3.0\n")


