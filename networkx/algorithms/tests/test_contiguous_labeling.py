import networkx as nx
from networkx.algorithms.contiguous_labeling import (
    contiguous_oriented_labeling,
    is_bridgeless,
    is_almost_bridgeless,
    verify_contiguous_labeling
)



def show_labeling(labeling):
    for label, i_minus, i_plus in labeling:
        print(f"Edge {label}: {i_minus}⁻ → {i_plus}⁺")


def test_cycle_graph():
    G = nx.cycle_graph(4)
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == G.number_of_edges()
    assert verify_contiguous_labeling(G, result)


def test_path_graph():
    G = nx.path_graph(4)
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == G.number_of_edges()
    assert verify_contiguous_labeling(G, result)


def test_disconnected_graph():
    G = nx.Graph()
    G.add_edges_from([(0, 1), (2, 3)])
    result = contiguous_oriented_labeling(G)
    assert result is None


def test_bridgeless():
    G = nx.cycle_graph(5)
    assert is_bridgeless(G)


def test_not_bridgeless():
    G = nx.path_graph(4)
    assert not is_bridgeless(G)


def test_almost_bridgeless():
    G = nx.path_graph(4)
    assert is_almost_bridgeless(G)


def test_named_cycle_graph():
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == 4
    assert verify_contiguous_labeling(G, result)


def test_triangle_with_tail():
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")])
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == 4
    assert verify_contiguous_labeling(G, result)


def test_star_with_center():
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == 5
    assert verify_contiguous_labeling(G, result)


def test_diamond_with_tail():
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D"), ("D", "E")])
    result = contiguous_oriented_labeling(G)
    assert result is not None
    assert len(result) == 6
    assert verify_contiguous_labeling(G, result)


if __name__ == "__main__":
    test_cycle_graph()
    test_path_graph()
    test_disconnected_graph()
    test_bridgeless()
    test_not_bridgeless()
    test_almost_bridgeless()
    test_named_cycle_graph()
    test_triangle_with_tail()
    test_star_with_center()
    test_diamond_with_tail()
    print("✅ All tests passed.")
