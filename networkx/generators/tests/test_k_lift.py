import pytest
from networkx.generators.k_lift import k_lift

import networkx as nx


# Test structure and connectivity for multiple (d, n, k) combinations
@pytest.mark.parametrize(
    "d, n, k",
    [
        (4, 8, 4),  # Balanced
        (3, 6, 5),  # Stress test on k
        (1, 2, 1),  # Tiny graph
        (6, 20, 3),  # Higher n with moderate d
        (80, 100, 10),  # Large-scale performance & correctness
    ],
)
def test_k_lift_size_and_structure(d, n, k):
    G = nx.random_regular_graph(d, n, seed=42)
    H = k_lift(G, k)
    degrees = [deg for _, deg in H.degree()]
    assert all(d - 1 <= deg <= d + 1 for deg in degrees)
    assert H.number_of_nodes() == n * k
    assert nx.is_connected(H)


# Specific test for failure behavior
def test_k_lift_non_regular_graph():
    """Create a non-regular graph: node 0 has degree 2,
    node 1 has degree 1, node 2 has degree 1
    """
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2)])  # degrees: 0→2, 1→1, 2→1

    with pytest.raises(ValueError, match="must be d-regular"):
        k_lift(G, k=2, seed=1)


# Specific test for failure behavior
def test_disconnected_lift_raises():
    """Create graph G with two connected nodes (0, 1).
    The 2-lift H is guaranteed to produce two disconnected pairs
    """
    G = nx.Graph()
    G.add_edge(0, 1)  # d = 1, n = 2
    with pytest.raises(ValueError, match="not connected"):
        k_lift(G, k=2, seed=2)
