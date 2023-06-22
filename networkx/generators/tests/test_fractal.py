"""Tests for generators defined in fractal.py"""

import numpy as np
import pytest

import networkx as nx


@pytest.mark.parametrize(
    "create_using", (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)
)
def test_laakso_graph(create_using):
    """Tests for the :func:`laakso_graph` function."""
    G = nx.laakso_graph(1, create_using)
    H = nx.from_edgelist([(0, 1)], create_using)
    assert nx.is_isomorphic(G, H)
    returned_pos = {tuple(arr) for arr in nx.get_node_attributes(G, "pos").values()}
    expected_pos = {(0, 0), (0, 1)}
    assert returned_pos == expected_pos

    G = nx.laakso_graph(2, create_using)
    H = nx.from_edgelist(
        [
            (0, 1),
            (1, 2),
            (1, 3),
            (2, 4),
            (3, 4),
            (4, 5),
        ],
        create_using,
    )
    assert nx.is_isomorphic(G, H)
    returned_pos = {tuple(arr) for arr in nx.get_node_attributes(G, "pos").values()}
    expected_pos = {
        (-0.25, 0.5),
        (0.0, 0.0),
        (0.0, 0.25),
        (0.0, 0.75),
        (0.0, 1.0),
        (0.25, 0.5),
    }
    assert returned_pos == expected_pos


@pytest.mark.parametrize(
    "create_using", (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)
)
def test_sierpinski_gasket_graph(create_using):
    """Tests for the :func:`sierpinski_gasket_graph` function."""
    G = nx.sierpinski_gasket_graph(1, create_using)
    H = nx.from_edgelist([(0, 1), (1, 2), (2, 0)], create_using)
    assert nx.is_isomorphic(G, H)
    returned_pos = {tuple(arr) for arr in nx.get_node_attributes(G, "pos").values()}
    expected_pos = {(0.0, 0.0), (1.0, 0.0), (0.5, np.sqrt(3) / 2)}
    assert returned_pos == expected_pos

    G = nx.sierpinski_gasket_graph(2, create_using)
    H = nx.from_edgelist(
        [
            (0, 1),
            (1, 2),
            (2, 0),
            (0, 3),
            (3, 4),
            (4, 0),
            (1, 4),
            (4, 5),
            (5, 1),
        ],
        create_using,
    )
    assert nx.is_isomorphic(G, H)
    returned_pos = {tuple(arr) for arr in nx.get_node_attributes(G, "pos").values()}
    expected_pos = {
        (0.0, 0.0),
        (1.0, 0.0),
        (0.5, np.sqrt(3) / 2),
        (-0.5, -np.sqrt(3) / 2),
        (0.5, -np.sqrt(3) / 2),
        (1.5, -np.sqrt(3) / 2),
    }
    # normalize
    expected_pos = {(x / 2, (y + np.sqrt(3) / 2) / 2) for (x, y) in expected_pos}
    assert returned_pos == expected_pos
