"""
    Unit tests for ete.
"""

import os
import tempfile

import pytest

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal

ete3 = pytest.importorskip("ete3")

dg_path_graph = nx.path_graph(42, create_using=nx.DiGraph)

dg_tree_with_int_nodes = nx.DiGraph(
    [
        (1, 2),
        (1, 3),
        (2, 4),
        (3, 5),
    ]
)

dg_tree_with_str_nodes = nx.DiGraph(
    [
        ("a", "b"),
        ("a", "c"),
        ("b", "d"),
        ("b", "e"),
    ]
)


@pytest.mark.parametrize(
    ("graph",),
    (
        (dg_path_graph,),
        (dg_tree_with_int_nodes,),
        (dg_tree_with_str_nodes,),
    ),
)
def test_transform_without_features(graph):
    tree = nx.parse_ete(nx.generate_ete(graph))

    assert nx.is_arborescence(graph)
    assert nx.is_arborescence(tree)

    assert_nodes_equal(graph.nodes, tree.nodes)
    assert_edges_equal(graph.edges, tree.edges)


@pytest.mark.parametrize(
    ("graph",),
    (
        (dg_path_graph,),
        (dg_tree_with_int_nodes,),
        (dg_tree_with_str_nodes,),
    ),
)
def test_transform_with_features(graph):
    for node in graph.nodes:
        graph.nodes[node]["feature"] = "test"

    tree = nx.parse_ete(nx.generate_ete(graph))

    assert nx.is_arborescence(graph)
    assert nx.is_arborescence(tree)

    def _setup_nodes(nodes):
        res = dict(nodes)
        for feature in ("name", "dist", "support"):
            res.pop(feature, None)
        return res

    assert_nodes_equal(
        _setup_nodes(graph.nodes(data=True)), _setup_nodes(tree.nodes(data=True))
    )
    assert_edges_equal(graph.edges(data=True), tree.edges(data=True))
