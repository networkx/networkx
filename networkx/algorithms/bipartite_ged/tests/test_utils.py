"""
Function making tests code simple
"""

from typing import Any

import pytest

import networkx as nx

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


def load_test_graphs() -> tuple[nx.Graph, nx.Graph]:
    """Creates 2 graphs for the tests"""
    g1, g2 = nx.Graph(), nx.Graph()

    g1.add_nodes_from(
        [
            ("u1", {"Label": 1}),
            ("u2", {"Label": 2}),
            ("u3", {"Label": 1}),
            ("u4", {"Label": 3}),
        ]
    )
    g1.add_edges_from(
        [
            ("u1", "u2", {"edge_attr": 1}),
            ("u2", "u3", {"edge_attr": 2}),
            ("u2", "u4", {"edge_attr": 1}),
            ("u3", "u4", {"edge_attr": 1}),
        ]
    )

    g2.add_nodes_from(
        [("v1", {"Label": 3}), ("v2", {"Label": 2}), ("v3", {"Label": 3})]
    )
    g2.add_edges_from([("v1", "v2", {"edge_attr": 1}), ("v2", "v3", {"edge_attr": 1})])

    return g1, g2


def comp_nodes(u: Any, v: Any, g1: nx.Graph, g2: nx.Graph) -> bool:
    """`True` if nodes `u` from `g1` & `v` from `g2` are identical"""
    return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]


def comp_edges(
    e1: tuple[Any, Any], e2: tuple[Any, Any], g1: nx.Graph, g2: nx.Graph
) -> bool:
    """`True` if edges `e1` from `g1` & `e2` from `g2` are identical"""
    return g1[e1[0]][e1[1]]["edge_attr"] == g2[e2[0]][e2[1]]["edge_attr"]


def constant_cost_matrix():
    """Cost matrix for `ConstantCostFunction`"""
    return np.array(
        [
            [1, 1, 1, 1, np.inf, np.inf, np.inf],
            [1, 0, 1, np.inf, 1, np.inf, np.inf],
            [1, 1, 1, np.inf, np.inf, 1, np.inf],
            [0, 1, 0, np.inf, np.inf, np.inf, 1],
            [1, np.inf, np.inf, 0, 0, 0, 0],
            [np.inf, 1, np.inf, 0, 0, 0, 0],
            [np.inf, np.inf, 1, 0, 0, 0, 0],
        ]
    )


def riesen_cost_matrix():
    """Cost matrix for `RiesenCostFunction`"""
    return np.array(
        [
            [1, 2, 1, 2, np.inf, np.inf, np.inf],
            [3, 1, 3, np.inf, 4, np.inf, np.inf],
            [2, 2, 2, np.inf, np.inf, 3, np.inf],
            [1, 1, 1, np.inf, np.inf, np.inf, 3],
            [2, np.inf, np.inf, 0, 0, 0, 0],
            [np.inf, 3, np.inf, 0, 0, 0, 0],
            [np.inf, np.inf, 2, 0, 0, 0, 0],
        ]
    )


def neighborhood_cost_matrix():
    """Cost matrix for `NeighborhoodCostFunction`"""
    return np.array(
        [
            [1, 4, 1, 2, np.inf, np.inf, np.inf],
            [6, 3, 6, np.inf, 4, np.inf, np.inf],
            [4, 3, 4, np.inf, np.inf, 3, np.inf],
            [2, 3, 2, np.inf, np.inf, np.inf, 3],
            [2, np.inf, np.inf, 0, 0, 0, 0],
            [np.inf, 3, np.inf, 0, 0, 0, 0],
            [np.inf, np.inf, 2, 0, 0, 0, 0],
        ]
    )
