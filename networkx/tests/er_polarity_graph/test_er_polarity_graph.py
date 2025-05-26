import pytest
import networkx as nx
from er_polarity_graph import er_polarity_graph

# Test size for multiple (m, q)
@pytest.mark.parametrize(
    "m, q",
    [
        (2, 2), # Minimal binary case
        (2, 3), # Classic example
        (2, 27), # Large GF(q), prime power
        (3, 7), # Mid-size graph
        (4, 4), # Large m, modest q
    ],
)
def test_er_polarity_graph_size(m, q):
    G = er_polarity_graph(m, q)
    assert G.number_of_nodes() == (q**(m+1) - 1)/(q - 1)

# Test connectivity for multiple (m, q)
@pytest.mark.parametrize(
    "m, q",
    [
        (2, 2), # Minimal binary case
        (2, 3), # Classic example
        (2, 27), # Large GF(q), prime power
        (3, 7), # Mid-size graph
        (4, 4), # Large m, modest q
    ],
)
def test_er_polarity_connectivity(m, q):
    G = er_polarity_graph(m, q)
    assert nx.is_connected(G)

# Test degree size and regularity
@pytest.mark.parametrize(
    "m, q",
    [
        (2, 2), # Minimal binary case
        (2, 3), # Classic example
        (2, 27), # Large GF(q), prime power
        (3, 7), # Mid-size graph
        (4, 4), # Large m, modest q
    ],
)
def test_er_polarity_degree_and_regularity(m, q):
    G = er_polarity_graph(m, q)
    degrees = [deg for _, deg in G.degree()]
    min_deg = min(degrees)
    max_deg = max(degrees)
    assert max_deg == (q**m - 1)/(q - 1)
    assert min_deg >= max_deg - 1

# Test diameter size (must be 2)
@pytest.mark.parametrize(
    "m, q",
    [
        (2, 2), # Minimal binary case
        (2, 3), # Classic example
        (2, 27), # Large GF(q), prime power
        (3, 7), # Mid-size graph
        (4, 4), # Large m, modest q
    ],
)
def test_er_polarity_diameter(m, q):
    G = er_polarity_graph(m, q)
    d = nx.diameter(G)
    assert d == 2

# Specific test for failure behavior (m=1)
def test_disconnected_lift_raises():
    m, q = 1,3
    with pytest.raises(ValueError, match="not connected"):
        er_polarity_graph(m, q)
