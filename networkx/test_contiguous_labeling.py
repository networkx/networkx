import networkx as nx
import pytest
from networkx.algorithms.contiguous_labeling import (
   contiguous_oriented_labeling,
   find_uv_to_make_bridgeless,
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
   assert not nx.has_bridges(G)

def test_not_bridgeless():
   G = nx.path_graph(4)
   assert nx.has_bridges(G)

def test_almost_bridgeless():
   G = nx.path_graph(4)
   assert find_uv_to_make_bridgeless(G) is not None or not nx.has_bridges(G)

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

# === Section G: Edge and Failure Tests ===

def test_empty_graph():
   G = nx.Graph()
   result = contiguous_oriented_labeling(G)
   assert result is None

def test_single_node_graph():
   G = nx.Graph()
   G.add_node("A")
   result = contiguous_oriented_labeling(G)
   assert result is None

def test_two_nodes_one_edge():
   G = nx.Graph()
   G.add_edge("A", "B")
   result = contiguous_oriented_labeling(G)
   assert result is not None
   assert len(result) == 1
   assert verify_contiguous_labeling(G, result)

def test_disconnected_components():
   G = nx.Graph()
   G.add_edges_from([("A", "B"), ("C", "D")])
   result = contiguous_oriented_labeling(G)
   assert result is None

def test_long_path_graph_conditions_only():
   G = nx.path_graph(100)
   result = contiguous_oriented_labeling(G)
   assert result is not None
   labels = set((i_minus, i_plus) for _, i_minus, i_plus in result)
   for u, v in G.edges:
       assert (u, v) in labels or (v, u) in labels
   assert verify_contiguous_labeling(G, result)

def test_fail_contiguous_property():
   G = nx.path_graph(4)
   incorrect_labeling = [
       (1, 0, 1),
       (2, 2, 3),  # disconnected from previous
       (3, 1, 2)
   ]
   assert not verify_contiguous_labeling(G, incorrect_labeling)

def test_big_cycle_graph():
   G = nx.cycle_graph(50)
   result = contiguous_oriented_labeling(G)
   assert result is not None
   assert len(result) == G.number_of_edges()
   assert verify_contiguous_labeling(G, result)

def test_big_path_graph():
   G = nx.path_graph(75)
   result = contiguous_oriented_labeling(G)
   assert result is not None
   assert len(result) == G.number_of_edges()
   assert verify_contiguous_labeling(G, result)

def test_big_star_graph():
   G = nx.star_graph(100)
   # Star graph is not almost bridgeless - has too many bridges
   assert find_uv_to_make_bridgeless(G) is None and nx.has_bridges(G)
   result = contiguous_oriented_labeling(G)
   assert result is None

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
   test_empty_graph()
   test_single_node_graph()
   test_two_nodes_one_edge()
   test_disconnected_components()
   test_long_path_graph_conditions_only()
   test_fail_contiguous_property()
   test_big_cycle_graph()
   test_big_path_graph()
   test_big_star_graph()
   print("✅ All tests including failures and edge cases ran.")
