import pytest

import networkx as nx
from networkx import NetworkXPointlessConcept

np = pytest.importorskip("numpy")
sp = pytest.importorskip("scipy")


def test_laplacian_centrality_empty_graph_raises_pointless_concept():
    G = nx.Graph()
    with pytest.raises(NetworkXPointlessConcept):
        d = nx.laplacian_centrality(G, normalized=False)


def test_laplacian_centrality_single_node():
    """This test checks if issue #6571 is fixed - laplacian_centrality on a single node graph returned an error.
    In a graph with a single node, the concept of Laplacian centrality becomes trivial, as there are no other nodes
    or edges to consider. However, we can still calculate the Laplacian centrality for the sake of completeness.
    For a single node graph, the adjacency matrix (A) will be a 1x1 matrix with a single entry of 0, as there are no
    connections between nodes. The degree matrix (D) will also be a 1x1 matrix with a single entry of 0, as the single
    node has a degree of 0.
    As a result, the Laplacian matrix (L) will be a 1x1 matrix with a single entry of 0:
    """

    G = nx.Graph()
    G.add_node(0)
    d = nx.laplacian_centrality(G, normalized=False)
    exact = {
        0: 0.0,
    }

    assert d[0] == exact[0]


def test_laplacian_centrality_unconnected_nodes():
    """Checks for an issue similar to #6571 - laplacian_centrality on a unconnected node graph should return 0
    In a graph with two unconnected nodes, the Laplacian centrality can still be calculated, but it may not be
    as informative as in a connected graph. This is because the lack of connections means that the removal of a node
    will not significantly change the graph structure.
    For unconnected nodes, the adjacency matrix (A) will have all zero entries since there are no connections between
    the nodes. The degree matrix (D) will also have all zero entries because both nodes have a degree of zero.
    Consequently, the Laplacian matrix (L) will be a zero matrix, and the Laplacian energy (LE) of the graph will be
    zero as well.
    When you remove either node from the graph, the remaining graph will still have zero Laplacian energy since it is
    essentially the same structure with one node removed. So the Laplacian centrality (LC) for each unconnected node
    will be:

        LC(v) = LE(G) - LE(G - v) = 0 - 0 = 0

    In this case, the Laplacian centrality for both unconnected nodes is 0, indicating that their removal will not
    affect the graph's structure. However, this measure is not as meaningful in this scenario, as the graph itself
    is not connected, and there is no information about the nodes' influence or contribution to the overall network.
    """

    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])
    d = nx.laplacian_centrality(G, normalized=False)

    exact = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
    }

    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)


def test_laplacian_centrality_unconnected_nodes_normalized():
    """Normalizing the Laplacian centrality of a graph without edges raises a NetworkXPointlessConcept."""
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])
    with pytest.raises(NetworkXPointlessConcept):
        d = nx.laplacian_centrality(G, normalized=True)


def test_laplacian_centrality_E():
    E = nx.Graph()
    E.add_weighted_edges_from(
        [(0, 1, 4), (4, 5, 1), (0, 2, 2), (2, 1, 1), (1, 3, 2), (1, 4, 2)]
    )
    d = nx.laplacian_centrality(E)
    exact = {
        0: 0.700000,
        1: 0.900000,
        2: 0.280000,
        3: 0.220000,
        4: 0.260000,
        5: 0.040000,
    }

    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)

    # Check not normalized
    full_energy = 200
    dnn = nx.laplacian_centrality(E, normalized=False)
    for n, dc in dnn.items():
        assert exact[n] * full_energy == pytest.approx(dc, abs=1e-7)

    # Check unweighted not-normalized version
    duw_nn = nx.laplacian_centrality(E, normalized=False, weight=None)
    print(duw_nn)
    exact_uw_nn = {
        0: 18,
        1: 34,
        2: 18,
        3: 10,
        4: 16,
        5: 6,
    }
    for n, dc in duw_nn.items():
        assert exact_uw_nn[n] == pytest.approx(dc, abs=1e-7)

    # Check unweighted version
    duw = nx.laplacian_centrality(E, weight=None)
    full_energy = 42
    for n, dc in duw.items():
        assert exact_uw_nn[n] / full_energy == pytest.approx(dc, abs=1e-7)


def test_laplacian_centrality_KC():
    KC = nx.karate_club_graph()
    d = nx.laplacian_centrality(KC)
    exact = {
        0: 0.2543593,
        1: 0.1724524,
        2: 0.2166053,
        3: 0.0964646,
        4: 0.0350344,
        5: 0.0571109,
        6: 0.0540713,
        7: 0.0788674,
        8: 0.1222204,
        9: 0.0217565,
        10: 0.0308751,
        11: 0.0215965,
        12: 0.0174372,
        13: 0.118861,
        14: 0.0366341,
        15: 0.0548712,
        16: 0.0172772,
        17: 0.0191969,
        18: 0.0225564,
        19: 0.0331147,
        20: 0.0279955,
        21: 0.0246361,
        22: 0.0382339,
        23: 0.1294193,
        24: 0.0227164,
        25: 0.0644697,
        26: 0.0281555,
        27: 0.075188,
        28: 0.0364742,
        29: 0.0707087,
        30: 0.0708687,
        31: 0.131019,
        32: 0.2370821,
        33: 0.3066709,
    }
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)

    # Check not normalized
    full_energy = 12502
    dnn = nx.laplacian_centrality(KC, normalized=False)
    for n, dc in dnn.items():
        assert exact[n] * full_energy == pytest.approx(dc, abs=1e-3)


def test_laplacian_centrality_K():
    K = nx.krackhardt_kite_graph()
    d = nx.laplacian_centrality(K)
    exact = {
        0: 0.3010753,
        1: 0.3010753,
        2: 0.2258065,
        3: 0.483871,
        4: 0.2258065,
        5: 0.3870968,
        6: 0.3870968,
        7: 0.1935484,
        8: 0.0752688,
        9: 0.0322581,
    }
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)

    # Check not normalized
    full_energy = 186
    dnn = nx.laplacian_centrality(K, normalized=False)
    for n, dc in dnn.items():
        assert exact[n] * full_energy == pytest.approx(dc, abs=1e-3)


def test_laplacian_centrality_P3():
    P3 = nx.path_graph(3)
    d = nx.laplacian_centrality(P3)
    exact = {0: 0.6, 1: 1.0, 2: 0.6}
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)


def test_laplacian_centrality_K5():
    K5 = nx.complete_graph(5)
    d = nx.laplacian_centrality(K5)
    exact = {0: 0.52, 1: 0.52, 2: 0.52, 3: 0.52, 4: 0.52}
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)


def test_laplacian_centrality_FF():
    FF = nx.florentine_families_graph()
    d = nx.laplacian_centrality(FF)
    exact = {
        "Acciaiuoli": 0.0804598,
        "Medici": 0.4022989,
        "Castellani": 0.1724138,
        "Peruzzi": 0.183908,
        "Strozzi": 0.2528736,
        "Barbadori": 0.137931,
        "Ridolfi": 0.2183908,
        "Tornabuoni": 0.2183908,
        "Albizzi": 0.1954023,
        "Salviati": 0.1149425,
        "Pazzi": 0.0344828,
        "Bischeri": 0.1954023,
        "Guadagni": 0.2298851,
        "Ginori": 0.045977,
        "Lamberteschi": 0.0574713,
    }
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)


def test_laplacian_centrality_DG():
    DG = nx.DiGraph([(0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 6), (5, 7), (5, 8)])
    d = nx.laplacian_centrality(DG)
    exact = {
        0: 0.2123352,
        5: 0.515391,
        1: 0.2123352,
        2: 0.2123352,
        3: 0.2123352,
        4: 0.2123352,
        6: 0.2952031,
        7: 0.2952031,
        8: 0.2952031,
    }
    for n, dc in d.items():
        assert exact[n] == pytest.approx(dc, abs=1e-7)

    # Check not normalized
    full_energy = 9.50704
    dnn = nx.laplacian_centrality(DG, normalized=False)
    for n, dc in dnn.items():
        assert exact[n] * full_energy == pytest.approx(dc, abs=1e-4)
