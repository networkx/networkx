import networkx as nx
from networkx.utils.pll_reachability import pll_has_path, pll_preprocess


def test_pll_no_path():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2)])
    labels_in, labels_out = pll_preprocess(G)
    assert not pll_has_path(G, 0, 3, labels_in, labels_out)  # No path to node 3


def test_pll_self_loop():
    G = nx.DiGraph()
    G.add_edges_from([(0, 0), (0, 1)])
    labels_in, labels_out = pll_preprocess(G)
    assert pll_has_path(G, 0, 0, labels_in, labels_out)  # Path exists to itself
    assert pll_has_path(G, 0, 1, labels_in, labels_out)  # Path exists to node 1


def test_pll_disjoint_graphs():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2)])  # First component
    G.add_edges_from([(3, 4)])  # Second component
    labels_in, labels_out = pll_preprocess(G)
    assert not pll_has_path(
        G, 0, 3, labels_in, labels_out
    )  # No path between components


def test_pll_empty_graph():
    G = nx.DiGraph()  # Empty graph
    labels_in, labels_out = pll_preprocess(G)
    # Since the graph is empty, we shouldn't try to check for paths
    # Instead, assert that the labels are empty
    assert labels_in == {}
    assert labels_out == {}
