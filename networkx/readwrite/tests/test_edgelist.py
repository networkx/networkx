"""
    Unit tests for edgelists.
"""
import pytest
import io
import itertools
import tempfile
import os
from textwrap import dedent
from typing import Callable, List, Tuple

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal, assert_graphs_equal


class TestEdgelist:
    @classmethod
    def setup_class(cls):
        cls.G = nx.Graph(name="test")
        e = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("a", "f")]
        cls.G.add_edges_from(e)
        cls.G.add_node("g")
        cls.DG = nx.DiGraph(cls.G)
        cls.XG = nx.MultiGraph()
        cls.XG.add_weighted_edges_from([(1, 2, 5), (1, 2, 5), (1, 2, 1), (3, 3, 42)])
        cls.XDG = nx.MultiDiGraph(cls.XG)

    @staticmethod
    def bytes_io(s: str, encoding="utf8") -> io.BytesIO:
        return io.BytesIO(bytes(dedent(s), encoding=encoding))

    @staticmethod
    def string_io(s: str) -> io.StringIO:
        return io.StringIO(dedent(s))

    @pytest.fixture(params=["BytesIO", "StringIO"])
    def stream(self, request) -> Callable[[str], io.IOBase]:
        return self.bytes_io if request.param == "BytesIO" else self.string_io

    @pytest.fixture(params=["", ","])
    def delimiter(self, request) -> str:
        return request.param

    @pytest.fixture
    def edgelist_no_data(self, delimiter):
        s = f"""\
            # comment line
            1{delimiter} 2
            # comment line
            2{delimiter} 3
            """
        expected = [(1, 2), (2, 3)]
        return s, expected, delimiter if delimiter != "" else None

    @pytest.fixture(params=itertools.product([True, False], repeat=2))
    def edgelist_data_dict(self, request, delimiter) -> (str, List[Tuple]):
        weights, colors = request.param
        data1, data2 = {}, {}
        if weights:
            data1["weight"], data2["weight"] = 2.0, 3.0
        if colors:
            data1["color"], data2["color"] = "green", "red"
        s = f"""\
            # comment line
            1{delimiter} 2{delimiter} {data1}
            # comment line
            2{delimiter} 3{delimiter} {data2}
            """
        expected = [(1, 2, data1), (2, 3, data2)]
        return s, expected, delimiter if delimiter != "" else None

    @pytest.fixture
    def edgelist_data_list(self, delimiter):
        s = f"""\
            # comment line
            1{delimiter} 2{delimiter} 2.0
            # comment line
            2{delimiter} 3{delimiter} 3.0
            """
        expected = [(1, 2, {"weight": 2.0}), (2, 3, {"weight": 3.0})]
        return s, expected, delimiter if delimiter != "" else None

    @staticmethod
    def example_graph():
        G = nx.Graph()
        G.add_weighted_edges_from([(1, 2, 3.0), (2, 3, 27.0), (3, 4, 3.0)])
        return G

    def test_read_edgelist_no_data(self, edgelist_no_data, stream):
        s, expected, delimiter = edgelist_no_data
        G = nx.read_edgelist(stream(s), nodetype=int, delimiter=delimiter)
        assert_edges_equal(G.edges(), expected)

    def test_read_edgelist_data_dict(self, edgelist_data_dict, stream):
        s, expected, delimiter = edgelist_data_dict
        G = nx.read_edgelist(stream(s), nodetype=int, data=True, delimiter=delimiter)
        assert_edges_equal(G.edges(data=True), expected)

    def test_read_edgelist_data_list(self, edgelist_data_list, stream):
        s, expected, delimiter = edgelist_data_list
        G = nx.read_edgelist(
            stream(s), nodetype=int, data=(("weight", float),), delimiter=delimiter
        )
        assert_edges_equal(G.edges(data=True), expected)

    def test_read_weighted_edgelist(self, edgelist_data_list, stream):
        s, expected, delimiter = edgelist_data_list
        G = nx.read_weighted_edgelist(stream(s), nodetype=int, delimiter=delimiter)
        assert_edges_equal(G.edges(data=True), expected)

    def test_write_edgelist_1(self):
        fh = io.BytesIO()
        G = nx.OrderedGraph()
        G.add_edges_from([(1, 2), (2, 3)])
        nx.write_edgelist(G, fh, data=False)
        fh.seek(0)
        assert fh.read() == b"1 2\n2 3\n"

    def test_write_edgelist_2(self):
        fh = io.BytesIO()
        G = nx.OrderedGraph()
        G.add_edges_from([(1, 2), (2, 3)])
        nx.write_edgelist(G, fh, data=True)
        fh.seek(0)
        assert fh.read() == b"1 2 {}\n2 3 {}\n"

    def test_write_edgelist_3(self):
        fh = io.BytesIO()
        G = nx.OrderedGraph()
        G.add_edge(1, 2, weight=2.0)
        G.add_edge(2, 3, weight=3.0)
        nx.write_edgelist(G, fh, data=True)
        fh.seek(0)
        assert fh.read() == b"1 2 {'weight': 2.0}\n2 3 {'weight': 3.0}\n"

    def test_write_edgelist_4(self):
        fh = io.BytesIO()
        G = nx.OrderedGraph()
        G.add_edge(1, 2, weight=2.0)
        G.add_edge(2, 3, weight=3.0)
        nx.write_edgelist(G, fh, data=[("weight")])
        fh.seek(0)
        assert fh.read() == b"1 2 2.0\n2 3 3.0\n"

    def test_unicode(self):
        G = nx.Graph()
        name1 = chr(2344) + chr(123) + chr(6543)
        name2 = chr(5543) + chr(1543) + chr(324)
        G.add_edge(name1, "Radiohead", **{name2: 3})
        fd, fname = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname)
        assert_graphs_equal(G, H)
        os.close(fd)
        os.unlink(fname)

    def test_latin1_issue(self):
        G = nx.Graph()
        name1 = chr(2344) + chr(123) + chr(6543)
        name2 = chr(5543) + chr(1543) + chr(324)
        G.add_edge(name1, "Radiohead", **{name2: 3})
        fd, fname = tempfile.mkstemp()
        pytest.raises(
            UnicodeEncodeError, nx.write_edgelist, G, fname, encoding="latin-1"
        )
        os.close(fd)
        os.unlink(fname)

    def test_latin1(self):
        G = nx.Graph()
        name1 = "Bj" + chr(246) + "rk"
        name2 = chr(220) + "ber"
        G.add_edge(name1, "Radiohead", **{name2: 3})
        fd, fname = tempfile.mkstemp()
        nx.write_edgelist(G, fname, encoding="latin-1")
        H = nx.read_edgelist(fname, encoding="latin-1")
        assert_graphs_equal(G, H)
        os.close(fd)
        os.unlink(fname)

    def test_edgelist_graph(self):
        G = self.G
        (fd, fname) = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname)
        H2 = nx.read_edgelist(fname)
        assert H != H2  # they should be different graphs
        G.remove_node("g")  # isolated nodes are not written in edgelist
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_edgelist_digraph(self):
        G = self.DG
        (fd, fname) = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname, create_using=nx.DiGraph())
        H2 = nx.read_edgelist(fname, create_using=nx.DiGraph())
        assert H != H2  # they should be different graphs
        G.remove_node("g")  # isolated nodes are not written in edgelist
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_edgelist_integers(self):
        G = nx.convert_node_labels_to_integers(self.G)
        (fd, fname) = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname, nodetype=int)
        # isolated nodes are not written in edgelist
        G.remove_nodes_from(list(nx.isolates(G)))
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_edgelist_multigraph(self):
        G = self.XG
        (fd, fname) = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname, nodetype=int, create_using=nx.MultiGraph())
        H2 = nx.read_edgelist(fname, nodetype=int, create_using=nx.MultiGraph())
        assert H != H2  # they should be different graphs
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_edgelist_multidigraph(self):
        G = self.XDG
        (fd, fname) = tempfile.mkstemp()
        nx.write_edgelist(G, fname)
        H = nx.read_edgelist(fname, nodetype=int, create_using=nx.MultiDiGraph())
        H2 = nx.read_edgelist(fname, nodetype=int, create_using=nx.MultiDiGraph())
        assert H != H2  # they should be different graphs
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_parse_edgelist_no_data(self):
        lines = ["1 2", "2 3", "3 4"]
        G = self.example_graph()
        H = nx.parse_edgelist(lines, nodetype=int)
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges()), list(G.edges()))

    def test_parse_edgelist_with_data_dict(self):
        lines = ["1 2 {'weight': 3}", "2 3 {'weight': 27}", "3 4 {'weight': 3.0}"]
        G = self.example_graph()
        H = nx.parse_edgelist(lines, nodetype=int)
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges(data=True)), list(G.edges(data=True)))

    def test_parse_edgelist_with_data_list(self):
        lines = ["1 2 3", "2 3 27", "3 4 3.0"]
        G = self.example_graph()
        H = nx.parse_edgelist(lines, nodetype=int, data=(("weight", float),))
        assert_nodes_equal(list(H), list(G))
        assert_edges_equal(list(H.edges(data=True)), list(G.edges(data=True)))
