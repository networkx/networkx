import unittest

import networkx as nx
from networkx.hypothesis import graph_repr_pretty


class MockPrinter:
    def __init__(self):
        self.output = []

    def text(self, text):
        self.output.append(text)

    def breakable(self):
        self.output.append(" ")

    def get_output(self):
        return "".join(self.output)


class TestGraphReprPretty(unittest.TestCase):
    def setUp(self):
        self.G = nx.Graph()
        self.G.add_edges_from([(1, 2, {"weight": 4}), (2, 3, {"weight": 5})])

        self.DG = nx.DiGraph()
        self.DG.add_edges_from([(1, 2, {"weight": 4}), (2, 3, {"weight": 5})])

        self.G_no_attr = nx.Graph()
        self.G_no_attr.add_edges_from([(1, 2), (2, 3)])

    def test_default_graph_omits_type(self):
        # Test for nx.Graph where `create_using=nx.Graph` is omitted
        mock_printer = MockPrinter()
        graph_repr_pretty(self.G, mock_printer, cycle=False)
        output = mock_printer.get_output()
        expected_output = (
            "nx.from_edgelist([(1, 2, {'weight': 4}), (2, 3, {'weight': 5})])"
        )
        self.assertEqual(output, expected_output)

    def test_directed_graph_includes_type(self):
        # Test for nx.DirectedGraph where `create_using=nx.DirectedGraph` is included
        mock_printer = MockPrinter()
        graph_repr_pretty(self.DG, mock_printer, cycle=False)
        output = mock_printer.get_output()
        expected_output = "nx.from_edgelist([(1, 2, {'weight': 4}), (2, 3, {'weight': 5})], create_using=nx.DiGraph)"
        self.assertEqual(output, expected_output)

    def test_edges_without_attributes(self):
        # Test for edges without attributes (no 'weight' field)
        mock_printer = MockPrinter()
        graph_repr_pretty(self.G_no_attr, mock_printer, cycle=False)
        output = mock_printer.get_output()
        expected_output = "nx.from_edgelist([(1, 2), (2, 3)])"
        self.assertEqual(output, expected_output)

    def test_cycle_case(self):
        # Check if an assertion error is raised when cycle=True
        with self.assertRaises(AssertionError):
            graph_repr_pretty(self.G, MockPrinter(), cycle=True)
