import pytest

import networkx as nx
from networkx.readwrite.gdf import read_gdf, write_gdf, gdf_split, gdf_escape
from networkx.utils import edges_equal
import tempfile


class TestGDF:
    @classmethod
    def setup_class(cls):
        cls.encoding = "utf-8"
        cls.gdf_line = "'foo\\'bar','bar,baz',baz,'TRUE','25','9.8'\n"
        cls.gdf_file_ok_directed = """\
nodedef>name,comma_foo,foo,quote_foo
'first','bar,baz','bar','bar\\'baz'
'second','bar,baz','bar','bar\\'baz'
'third','bar,baz','bar','bar\\'baz'
edgedef>node1,node2,attribute_bar,attribute_foo,directed
'first','second',,'foo',TRUE
'first','third',,,TRUE
'second','third','bar',,TRUE
"""
        cls.gdf_file_ok_undirected = """\
nodedef>name,comma_foo,foo,quote_foo
'first','bar,baz','bar','bar\\'baz'
'second','bar,baz','bar','bar\\'baz'
'third','bar,baz','bar','bar\\'baz'
edgedef>node1,node2,attribute_bar,attribute_foo
'first','second',,'foo'
'first','third',,
'second','third','bar',
"""
        cls.gdf_file_node_attr_error = """\
nodedef>name,comma_foo,foo
'first','bar,baz','bar','bar\\'baz'
'second','bar,baz','bar','bar\\'baz'
'third','bar,baz','bar','bar\\'baz'
edgedef>node1,node2,attribute_bar,attribute_foo
'first','second',,'foo'
'first','third',,
'second','third','bar',
"""
        cls.gdf_file_edge_attr_error = """\
nodedef>name,comma_foo,foo,quote_foo
'first','bar,baz','bar','bar\\'baz'
'second','bar,baz','bar','bar\\'baz'
'third','bar,baz','bar','bar\\'baz'
edgedef>node1,node2,attribute_bar,attribute_foo
'first','second',,'foo'
'first','third',,
'second','third','bar',
"""
        cls.G = nx.Graph()
        cls.G.add_nodes_from([
            (1, {"name": "first", "foo": "bar", "comma_foo": "bar,baz", "quote_foo": "bar'baz"}),
            (2, {"name": "second", "foo": "bar", "comma_foo": "bar,baz", "quote_foo": "bar'baz"}),
            (3, {"name": "third", "foo": "bar", "comma_foo": "bar,baz", "quote_foo": "bar'baz"})
        ])
        cls.G.add_edges_from([
            (1, 2, {"attribute_foo": "foo"}),
            (2, 3, {"attribute_bar": "bar"}),
            (1, 3)
        ])

        cls.DiG = nx.DiGraph()
        cls.DiG.add_nodes_from(cls.G.nodes(data=True))
        cls.DiG.add_edges_from(cls.G.edges(data=True))

    def test_gdf_split(self):
        expected_naive = ["foo'bar", "bar,baz", "baz", "TRUE", "25", "9.8"]
        expected_typed = ["foo'bar", "bar,baz", "baz", True, 25, 9.8]
        types = ["VARCHAR", "VARCHAR", "VARCHAR", "BOOLEAN", "INTEGER", "FLOAT"]

        assert expected_naive == gdf_split(self.gdf_line)
        assert expected_typed == gdf_split(self.gdf_line, types)

    def test_gdf_escape(self):
        assert gdf_escape(True) == "TRUE"
        assert gdf_escape(None) == ""
        assert gdf_escape("") == ""
        assert gdf_escape("foobar") == "'foobar'"
        assert gdf_escape("foo,bar") == "'foo,bar'"
        assert gdf_escape("foo'bar") == "'foo\\'bar'"

    def test_read_gdf_undirected(self):
        with tempfile.TemporaryFile("w+", encoding=self.encoding) as fake_file:
            fake_file.write(self.gdf_file_ok_undirected)
            fake_file.seek(0)
            G = read_gdf(fake_file, encoding=self.encoding)

        assert type(G) is nx.Graph
        assert G.nodes(data=True) == self.G.nodes(data=True)
        assert edges_equal(G.edges(), self.G.edges())

    def test_read_gdf_directed(self):
        with tempfile.TemporaryFile("w+", encoding=self.encoding) as fake_file:
            fake_file.write(self.gdf_file_ok_directed)
            fake_file.seek(0)
            DiG = read_gdf(fake_file, encoding=self.encoding)

        assert type(DiG) is nx.DiGraph
        assert DiG.nodes(data=True) == self.DiG.nodes(data=True)
        assert edges_equal(DiG.edges(), self.DiG.edges())

    def test_read_gdf_node_exceptions(self):
        with tempfile.TemporaryFile("w+", encoding=self.encoding) as fake_file:
            fake_file.write(self.gdf_file_node_attr_error)
            fake_file.seek(0)
            pytest.raises(ImportError, read_gdf, fake_file, self.encoding)

    def test_read_gdf_edge_exceptions(self):
        with tempfile.TemporaryFile("w+", encoding=self.encoding) as fake_file:
            fake_file.write(self.gdf_file_node_attr_error)
            fake_file.seek(0)
            pytest.raises(ImportError, read_gdf, fake_file, self.encoding)

    def test_write_gdf_undirected(self):
        with tempfile.TemporaryFile("w+b") as fake_file:
            write_gdf(self.G, fake_file, encoding=self.encoding)
            fake_file.seek(0)
            fake_file.seek(0)
            assert fake_file.read() == self.gdf_file_ok_undirected.encode(self.encoding)

    def test_write_gdf_directed(self):
        with tempfile.TemporaryFile("w+b") as fake_file:
            write_gdf(self.DiG, fake_file, encoding=self.encoding)
            fake_file.seek(0)
            assert fake_file.read() == self.gdf_file_ok_directed.encode(self.encoding)
