"""Unit tests for the :mod:`networkx.algorithms.treelet` module."""

import pytest

import networkx as nx


# --- Unlabeled treelets tests ---
def test_treelets_undirected_5_path():
    G = nx.path_graph(5)
    result = nx.treelets(G)
    expected = {"G_0": 5, "G_1": 4, "G_2": 3, "G_3": 2, "G_4": 1}
    assert result == expected


def test_treelets_directed_5_path():
    G = nx.path_graph(5).to_directed()
    result = nx.treelets(G)
    expected = {"G_0": 5, "G_1": 8, "G_2": 6, "G_3": 4, "G_4": 2}
    assert result == expected


def test_treelets_centered_node_1():
    G = nx.path_graph(5)
    result = nx.treelets(G, 1)
    expected = {"G_0": 1, "G_1": 2, "G_2": 1, "G_3": 1}
    assert result == expected


def test_treelets_centered_nodes_1_3():
    G = nx.path_graph(5)
    result = nx.treelets(G, [1, 3])
    expected = {"G_0": 2, "G_1": 4, "G_2": 1, "G_3": 2}
    assert result == expected


def test_treelets_5_star():
    G = nx.star_graph(5)
    result = nx.treelets(G)
    expected = {"G_0": 6, "G_1": 5, "G_2": 10, "G_6": 10, "G_8": 5, "G_13": 1}
    assert result == expected


def test_treelets_two_connected_3_stars():
    G = nx.star_graph(3)
    G.add_edges_from([(3, 4), (3, 5)])
    result = nx.treelets(G)
    expected = {"G_0": 6, "G_1": 5, "G_2": 6, "G_3": 4, "G_6": 2, "G_7": 4, "G_12": 1}
    assert result == expected


def test_treelets_two_connected_3_stars_with_one_pattern_filter():
    G = nx.star_graph(3)
    G.add_edges_from([(3, 4), (3, 5)])
    result = nx.treelets(G, patterns="star-path")
    expected = {"G_7": 4, "G_12": 1}
    assert result == expected


def test_treelets_two_connected_3_stars_with_two_pattern_filters():
    G = nx.star_graph(3)
    G.add_edges_from([(3, 4), (3, 5)])
    result = nx.treelets(G, patterns=["path", "star"])
    expected = {"G_0": 6, "G_1": 5, "G_2": 6, "G_3": 4, "G_6": 2}
    assert result == expected


# --- Labeled treelets tests ---
# Helper function to create the methanal molecule graph
def methanal_graph(directed=False):
    G = nx.DiGraph() if directed else nx.Graph()
    atoms = ["C", "H", "H", "O"]
    for i, atom in enumerate(atoms):
        G.add_node(i, atom_symbol=atom)
    bond_types = ["1", "1", "2"]
    edges = [(0, 1), (0, 2), (0, 3)]
    for (u, v), bond in zip(edges, bond_types):
        G.add_edge(u, v, bond_type=bond)
    return G


@pytest.fixture
def molecule_graph():
    return methanal_graph()


def test_labeled_treelets_simple_molecule(molecule_graph):
    result = nx.labeled_treelets(molecule_graph)
    expected = {
        ("G_0", ("C",)): 1,
        ("G_0", ("H",)): 2,
        ("G_0", ("O",)): 1,
        ("G_1", ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("2",), ("O",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("1",), ("H",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("2",), ("O",)): 2,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("O",)): 1,
    }
    assert result == expected


def test_labeled_treelets_directed_simple_molecule():
    G = methanal_graph(directed=True)
    result = nx.labeled_treelets(
        G, node_attrs=["atom_symbol"], edge_attrs=["bond_type"]
    )
    expected = {
        ("G_0", ("C",)): 1,
        ("G_0", ("H",)): 2,
        ("G_0", ("O",)): 1,
        ("G_1", ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("2",), ("O",)): 1,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("O",)): 1,
    }
    assert result == expected


def test_labeled_treelets_centered_node_0(molecule_graph):
    result = nx.labeled_treelets(molecule_graph, 0)
    expected = {
        ("G_0", ("C",)): 1,
        ("G_1", ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("2",), ("O",)): 1,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("O",)): 1,
    }
    assert result == expected


def test_labeled_treelets_centered_nodes_0_2(molecule_graph):
    result = nx.labeled_treelets(molecule_graph, [0, 2])
    expected = {
        ("G_0", ("C",)): 1,
        ("G_0", ("H",)): 1,
        ("G_1", ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("2",), ("O",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("1",), ("H",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("2",), ("O",)): 1,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("O",)): 1,
    }
    assert result == expected


def test_labeled_treelets_with_star_pattern_filter(molecule_graph):
    result = nx.labeled_treelets(molecule_graph, patterns="star")
    expected = {("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("O",)): 1}
    assert result == expected


def test_labeled_treelets_with_path_list_pattern_filter(molecule_graph):
    result = nx.labeled_treelets(molecule_graph, patterns=["path"])
    expected = {
        ("G_0", ("C",)): 1,
        ("G_0", ("H",)): 2,
        ("G_0", ("O",)): 1,
        ("G_1", ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("2",), ("O",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("1",), ("H",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("2",), ("O",)): 2,
    }
    assert result == expected


def test_labeled_treelets_multiple_attributes():
    G = nx.Graph()
    atoms = ["C", "H", "H", "O"]
    labels = ["l1", "l2", "l3", "l1"]
    for i, attr in enumerate(zip(atoms, labels)):
        G.add_node(i, atom_symbol=attr[0], label=attr[1])
    bond_types = ["1", "1", "2"]
    edges = [(0, 1), (0, 2), (0, 3)]
    for (u, v), bond in zip(edges, bond_types):
        G.add_edge(u, v, bond_type=bond)
    result = nx.labeled_treelets(G)
    expected = {
        ("G_0", ("l1", "C")): 1,
        ("G_0", ("l2", "H")): 1,
        ("G_0", ("l3", "H")): 1,
        ("G_0", ("l1", "O")): 1,
        ("G_1", ("l1", "C"), ("1",), ("l2", "H")): 1,
        ("G_1", ("l1", "C"), ("1",), ("l3", "H")): 1,
        ("G_1", ("l1", "C"), ("2",), ("l1", "O")): 1,
        ("G_2", ("l2", "H"), ("1",), ("l1", "C"), ("1",), ("l3", "H")): 1,
        ("G_2", ("l1", "O"), ("2",), ("l1", "C"), ("1",), ("l2", "H")): 1,
        ("G_2", ("l1", "O"), ("2",), ("l1", "C"), ("1",), ("l3", "H")): 1,
        (
            "G_6",
            ("l1", "C"),
            ("1",),
            ("l2", "H"),
            ("1",),
            ("l3", "H"),
            ("2",),
            ("l1", "O"),
        ): 1,
    }
    expected_inversed_attributes = {
        ("G_0", ("C", "l1")): 1,
        ("G_0", ("H", "l2")): 1,
        ("G_0", ("H", "l3")): 1,
        ("G_0", ("O", "l1")): 1,
        ("G_1", ("C", "l1"), ("1",), ("H", "l2")): 1,
        ("G_1", ("C", "l1"), ("1",), ("H", "l3")): 1,
        ("G_1", ("C", "l1"), ("2",), ("O", "l1")): 1,
        ("G_2", ("H", "l2"), ("1",), ("C", "l1"), ("1",), ("H", "l3")): 1,
        ("G_2", ("H", "l2"), ("1",), ("C", "l1"), ("2",), ("O", "l1")): 1,
        ("G_2", ("H", "l3"), ("1",), ("C", "l1"), ("2",), ("O", "l1")): 1,
        (
            "G_6",
            ("C", "l1"),
            ("1",),
            ("H", "l2"),
            ("1",),
            ("H", "l3"),
            ("2",),
            ("O", "l1"),
        ): 1,
    }
    assert result in (expected, expected_inversed_attributes)


def test_labeled_treelets_double_3_star_graph():
    G = nx.star_graph(3)
    G.add_edges_from([(3, 4), (3, 5)])
    labels = ["C", "H", "H", "C", "H", "C"]
    for i in range(6):
        G.nodes[i]["label"] = labels[i]
    edge_labels = ["1", "1", "2", "1", "1"]
    for i, (u, v) in enumerate(G.edges):
        G.edges[u, v]["edge_label"] = edge_labels[i]
    result = nx.labeled_treelets(G)
    expected = {
        ("G_0", ("C",)): 3,
        ("G_0", ("H",)): 3,
        ("G_1", ("C",), ("1",), ("H",)): 3,
        ("G_1", ("C",), ("2",), ("C",)): 1,
        ("G_2", ("C",), ("2",), ("C",), ("1",), ("H",)): 3,
        ("G_2", ("C",), ("1",), ("C",), ("2",), ("C",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("1",), ("H",)): 1,
        ("G_3", ("H",), ("1",), ("C",), ("2",), ("C",), ("1",), ("H",)): 2,
        ("G_3", ("C",), ("1",), ("C",), ("2",), ("C",), ("1",), ("H",)): 2,
        ("G_1", ("C",), ("1",), ("C",)): 1,
        ("G_2", ("C",), ("1",), ("C",), ("1",), ("H",)): 1,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("C",)): 1,
        (
            "G_7",
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 1,
        (
            "G_7",
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("C",),
        ): 1,
        (
            "G_12",
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
        ): 1,
        ("G_6", ("C",), ("1",), ("C",), ("1",), ("H",), ("2",), ("C",)): 1,
        (
            "G_7",
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 2,
    }
    assert result == expected


def test_labeled_treelets_5_star_graph():
    G = nx.star_graph(5)
    labels = ["C", "H", "H", "C", "H", "C"]
    for i in range(6):
        G.nodes[i]["label"] = labels[i]
    edge_labels = ["1", "1", "2", "1", "1"]
    for i, (u, v) in enumerate(G.edges):
        G.edges[u, v]["edge_label"] = edge_labels[i]
    result = nx.labeled_treelets(G)
    expected = {
        ("G_0", ("C",)): 3,
        ("G_0", ("H",)): 3,
        ("G_1", ("C",), ("1",), ("H",)): 3,
        ("G_1", ("C",), ("2",), ("C",)): 1,
        ("G_1", ("C",), ("1",), ("C",)): 1,
        ("G_2", ("H",), ("1",), ("C",), ("1",), ("H",)): 3,
        ("G_2", ("C",), ("2",), ("C",), ("1",), ("H",)): 3,
        ("G_2", ("C",), ("1",), ("C",), ("1",), ("H",)): 3,
        ("G_2", ("C",), ("1",), ("C",), ("2",), ("C",)): 1,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("2",), ("C",)): 3,
        ("G_6", ("C",), ("1",), ("H",), ("1",), ("H",), ("1",), ("H",)): 1,
        ("G_6", ("C",), ("1",), ("C",), ("1",), ("H",), ("1",), ("H",)): 3,
        ("G_6", ("C",), ("1",), ("C",), ("1",), ("H",), ("2",), ("C",)): 3,
        (
            "G_8",
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
        ): 1,
        (
            "G_8",
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
        ): 3,
        (
            "G_8",
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
        ): 1,
        (
            "G_13",
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
        ): 1,
    }
    assert result == expected


def test_labeled_treelets_big_cross_graph():
    G = nx.path_graph(6)
    G.add_edge(2, 6)
    G.add_edge(2, 7)
    labels = ["C", "H", "H", "C", "H", "C", "C", "C"]
    for i in range(len(labels)):
        G.nodes[i]["label"] = labels[i]
    edge_labels = ["1", "1", "2", "1", "1", "1", "1"]
    for i, (u, v) in enumerate(G.edges):
        G.edges[u, v]["edge_label"] = edge_labels[i]
    result = nx.labeled_treelets(G, patterns="star-path")
    expected = {
        (
            "G_7",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
            ("2",),
            ("C",),
        ): 2,
        (
            "G_7",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 2,
        (
            "G_10",
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
            ("2",),
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
        ): 2,
        (
            "G_9",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 2,
        (
            "G_7",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
        ): 1,
        (
            "G_7",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("C",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 1,
        (
            "G_10",
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
            ("2",),
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("C",),
        ): 1,
        (
            "G_11",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("1",),
            ("C",),
            ("2",),
            ("C",),
        ): 1,
        (
            "G_11",
            ("H",),
            ("1",),
            ("C",),
            ("1",),
            ("C",),
            ("1",),
            ("H",),
            ("2",),
            ("C",),
            ("1",),
            ("H",),
        ): 1,
    }
    assert result == expected
