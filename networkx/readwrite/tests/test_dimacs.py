"""
    Unit tests for dimacs.
"""
import io
import os

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal


class TestDimacs:
    @classmethod
    def setup_class(cls):
        pass

    def test_read_dimacs_1(self):
        s = b"""\
c this is a test graph in DIMACS Format

c another comment

p edge 3 3

e 1 2



e 2 3

e 3 1

n 1
"""
        bytesIO = io.BytesIO(s)
        G = nx.read_dimacs(bytesIO)
        assert_edges_equal(G.edges(), [(1, 2), (2, 3), (3, 1)])

    def test_write_dimacs(self):
        G = nx.Graph()
        G.add_node(1, value=2)
        G.add_node(2, value=3)
        G.add_edge(1, 2)
        nx.write_dimacs(G, "temp")
        expected_output = """p edge 2 1
n 1 2
n 2 3
e 1 2
"""
        output = open("temp", "r").read()
        assert output == expected_output
        os.unlink("temp")

    def test_generate_dimacs(self):
        G = nx.Graph()
        G.add_node(1, value=2)
        G.add_node(2, value=3)
        G.add_edge(1, 2)
        nx.write_dimacs(G, "temp")
        expected_output = """p edge 2 1
n 1 2
n 2 3
e 1 2
""".split(
            "\n"
        )
        for generated_line, expected_line in zip(
            nx.generate_dimacs(G), expected_output
        ):
            assert generated_line == expected_line

    def test_parse_dimacs(self):
        lines = [
            "c this is a test graph in DIMACS Format",
            "c another comment",
            "p edge 3 3",
            "n 2 1",
            "e 1 2",
            "e 2 3",
            "e 3 1",
        ]
        G = nx.parse_dimacs(lines)
        assert_edges_equal(G.edges(), [(1, 2), (2, 3), (3, 1)])
        assert_nodes_equal(G.nodes(), {1: {}, 2: {"value": 2}, 3: {}})
