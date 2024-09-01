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
    G.add_edges_from([(1, 2), (2, 3)])
    nx.write_mermaid(G, fh)
    fh.seek(0)
    assert fh.read() == b"flowchart\n    1 --> 2\n    2 --> 3\n"


def test_read_mermaid_basic():
    bytesIO = io.BytesIO(basic_chart.encode("utf-8"))
    G = nx.read_mermaid(bytesIO)
    assert edges_equal(G.edges(), [("1", "2"), ("2", "3")])
