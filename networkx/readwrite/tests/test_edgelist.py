"""
    Unit tests for edgelists.
"""
import pytest
import io
import tempfile
import os
from textwrap import dedent

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

    @staticmethod
    def example_data(weights=False, colors=False, as_dict=False):
        if weights and colors and not as_dict:
            msg = "Cannot have both weights and colors if as_dict=False"
            raise ValueError(msg)
        data1, data2 = "", ""
        if as_dict:
            data1, data2 = {}, {}
            if weights:
                data1["weight"] = 2.0
                data2["weight"] = 3.0
            if colors:
                data1["color"] = "green"
                data2["color"] = "red"
        elif weights:
            data1, data2 = 2.0, 3.0
        elif colors:
            data1, data2 = "green", "red"
        return data1, data2

    @staticmethod
    def example_edgelist(
        weights=False, colors=False, as_dict=False, delimiter=""
    ) -> str:
        data1, data2 = TestEdgelist.example_data(weights, colors, as_dict)
        s = f"""\
            # comment line
            1{delimiter} 2{delimiter} {data1}
            # comment line
            2{delimiter} 3{delimiter} {data2}
            """
        return s

    @staticmethod
    def example_edges(weights=False, colors=False):
        has_data = weights or colors
        data1, data2 = TestEdgelist.example_data(weights, colors, as_dict=True)
        return [
            (1, 2, data1) if has_data else (1, 2),
            (2, 3, data2) if has_data else (2, 3),
        ]

    @staticmethod
    def example_graph():
        G = nx.Graph()
        G.add_weighted_edges_from([(1, 2, 3.0), (2, 3, 27.0), (3, 4, 3.0)])
        return G

    def test_read_edgelist_no_data(self):
        s = self.example_edgelist()
        G = nx.read_edgelist(self.bytes_io(s), nodetype=int)
        assert_edges_equal(G.edges(), self.example_edges())

    def test_read_edgelist_with_data(self):
        s = self.example_edgelist(weights=True)
        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=False)
        assert_edges_equal(G.edges(), self.example_edges())

        G = nx.read_weighted_edgelist(self.bytes_io(s), nodetype=int)
        assert_edges_equal(G.edges(data=True), self.example_edges(weights=True))

    def test_read_edgelist_with_data_dict(self):
        s = self.example_edgelist(weights=True, as_dict=True)
        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=False)
        assert_edges_equal(G.edges(), self.example_edges())

        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=True)
        assert_edges_equal(G.edges(data=True), self.example_edges(weights=True))

    def test_read_edgelist_from_string_io(self):
        s = self.example_edgelist(weights=True, as_dict=True)
        G = nx.read_edgelist(self.string_io(s), nodetype=int, data=False)
        assert_edges_equal(G.edges(), self.example_edges())

        G = nx.read_edgelist(self.string_io(s), nodetype=int, data=True)
        assert_edges_equal(G.edges(data=True), self.example_edges(weights=True))

    def test_read_edgelist_with_data_dict_2(self):
        s = self.example_edgelist(weights=True, colors=True, as_dict=True)
        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=False)
        assert_edges_equal(G.edges(), self.example_edges())

        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=True)
        assert_edges_equal(
            G.edges(data=True), self.example_edges(weights=True, colors=True)
        )

    def test_read_edgelist_comma_delimited(self):
        s = self.example_edgelist(
            weights=True, colors=True, as_dict=True, delimiter=","
        )
        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=False, delimiter=",")
        assert_edges_equal(G.edges(), self.example_edges())

        G = nx.read_edgelist(self.bytes_io(s), nodetype=int, data=True, delimiter=",")
        assert_edges_equal(
            G.edges(data=True), self.example_edges(weights=True, colors=True)
        )

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
