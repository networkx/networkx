import pytest
import networkx as nx
from k_lift import k_lift

# Test structure and connectivity for multiple (d, n, k) combinations
@pytest.mark.parametrize(
    "d, n, k",
    [
        (2, 5, 2), # Edge case
        (4, 8, 4), # Balanced
        (3, 6, 5), # Stress test on k
        (1, 2, 1), # Tiny graph
        (6, 20, 3), # Higher n with moderate d
        (80,100,10) #Large-scale performance & correctness
    ],
)
def test_k_lift_size_and_structure(d, n, k):
    G = nx.random_regular_graph(d, n, seed = 42)
    H = k_lift(G, k)
    assert H.number_of_nodes() == n * k
    assert nx.is_connected(H)

# Test that degrees stay close to expected range across various graphs
@pytest.mark.parametrize(
    "d, n, k",
    [
        (2, 5, 2), # Edge case
        (4, 8, 4), # Balanced
        (3, 6, 5), # Stress test on k
        (1, 2, 1), # Tiny graph
        (6, 20, 3), # Higher n with moderate d
        (80,100,10) #Large-scale performance & correctness
    ],
)
def test_degrees_near_regular(d, n, k):
    G = nx.random_regular_graph(d, n, seed=1)
    H = k_lift(G, k)
    degrees = [deg for _, deg in H.degree()]
    assert all(d - 1 <= deg <= d + 1 for deg in degrees)

# Specific test for failure behavior
def test_disconnected_lift_raises():
    d, n, k = 1, 2, 2
    G = nx.random_regular_graph(d, n)
    with pytest.raises(ValueError, match="not connected"):
        k_lift(G, k)
