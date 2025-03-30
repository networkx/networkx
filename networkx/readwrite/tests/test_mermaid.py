"""
Unit tests for mermaid flowcharts.
"""

import io
import textwrap

import pytest

import networkx as nx
from networkx.utils import edges_equal, graphs_equal, nodes_equal

basic_chart = textwrap.dedent(
    """
    flowchart
        1 --> 2
        2 --> 3
    """
)


def test_write_mermaid_basic():
    fh = io.BytesIO()
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("B", "C")])
    nx.write_mermaid(G, fh)
    fh.seek(0)
    assert fh.read() == b"flowchart\n    A --> B\n    B --> C\n"


def test_write_mermaid_spaces_in_names():
    fh = io.BytesIO()
    G = nx.Graph()
    G.add_edges_from([("start node", "middle node"), ("middle node", "final node")])
    nx.write_mermaid(G, fh)
    fh.seek(0)
    assert (
        fh.read()
        == b'flowchart\n    A["start node"] --> B["middle node"]\n    B["middle node"] --> C["final node"]\n'
    )


def test_read_mermaid_basic():
    bytesIO = io.BytesIO(basic_chart.encode("utf-8"))
    G = nx.read_mermaid(bytesIO)
    assert edges_equal(G.edges(), [("1", "2"), ("2", "3")])
