"""
Unit tests for mermaid flowcharts.
"""

import io

import networkx as nx


def test_write_mermaid_basic():
    fh = io.BytesIO()
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    nx.write_mermaid(G, fh)
    fh.seek(0)
    assert fh.read() == b"flowchart\n    1 --> 2\n    2 --> 3\n"
