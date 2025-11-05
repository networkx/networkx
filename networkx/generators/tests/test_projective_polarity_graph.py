import pytest

import networkx as nx
from networkx.generators.projective_polarity_prime import projective_polarity_graph

numpy = pytest.importorskip("numpy")


@pytest.mark.parametrize(
    "m, q",
    [
        (2, 2),  # Minimal binary case
        (2, 3),  # Classic example
        (2, 23),  # Large GF(q)
        (3, 7),  # Mid-size graph
        (4, 5),  # Large m, modest q
    ],
)
def test_projective_polarity_graph_size_and_structure(m, q):
    G = projective_polarity_graph(m, q)

    # size
    assert G.number_of_nodes() == (q ** (m + 1) - 1) / (q - 1)

    # connectivity
    assert nx.is_connected(G)

    # degree and near regularity
    degrees = [deg for _, deg in G.degree()]
    min_deg = min(degrees)
    max_deg = max(degrees)
    assert max_deg == (q ** m - 1) / (q - 1)
    assert min_deg >= max_deg - 1


# Test diameter size for ER polarity graphs (must be 2)
@pytest.mark.parametrize("q", [3, 5, 7, 11, 17, 23, 29])
def test_projective_polarity_m2_has_diameter_2(q):
    G = projective_polarity_graph(2, q)
    d = nx.diameter(G)
    assert d == 2


def test_projective_polarity_invalid_m_raises():
    m, q = 1, 3
    with pytest.raises(ValueError, match="m must be an integer ≥ 2"):
        projective_polarity_graph(m, q)


def test_projective_polarity_invalid_q_raises():
    with pytest.raises(ValueError, match="only supports prime q"):
        projective_polarity_graph(m=2, q=4)  # 4 is not a prime, should raise
