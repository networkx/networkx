import networkx as nx
from networkx.testing import almost_equal

import pytest
np = pytest.importorskip('numpy')


def small_undir_G():
    """Sample network from https://doi.org/10.1371/journal.pone.0233276"""
    G = nx.Graph()
    G.add_edge("A", "E", weight=5)
    G.add_edge("A", "B", weight=2)
    G.add_edge("B", "F", weight=5)
    G.add_edge("B", "C", weight=2)
    G.add_edge("B", "D", weight=2)
    G.add_edge("C", "D", weight=5)

    return G


def small_dir_G():
    """Sample network from https://doi.org/10.1371/journal.pone.0233276"""
    G = nx.DiGraph()
    G.add_edge("A", "E", weight=5)
    G.add_edge("A", "B", weight=6)
    G.add_edge("B", "A", weight=2)
    G.add_edge("B", "F", weight=5)
    G.add_edge("B", "C", weight=2)
    G.add_edge("B", "D", weight=2)
    G.add_edge("C", "D", weight=3)
    G.add_edge("D", "C", weight=5)

    return G


class TestDistinctiveness:

    def test_undirected(self):
        G = small_undir_G()
        DC1 = nx.distinctiveness(G, normalize=False, alpha=1,
                                 measures=["D1", "D2", "D3", "D4", "D5"])
        DC2 = nx.distinctiveness(G, normalize=False, alpha=2,
                                 measures=["D1", "D2", "D3", "D4", "D5"])
        assert almost_equal(round(DC1["D1"]["A"], 3), 3.689)
        assert almost_equal(round(DC1["D1"]["B"], 3), 5.882)
        assert almost_equal(round(DC1["D2"]["A"], 3), 0.796)
        assert almost_equal(round(DC1["D2"]["C"], 3), 0.495)
        assert almost_equal(round(DC1["D3"]["A"], 3), 7.256)
        assert almost_equal(round(DC1["D3"]["D"], 3), 4.870)
        assert almost_equal(round(DC1["D4"]["A"], 3), 5.364)
        assert almost_equal(round(DC1["D4"]["E"], 3), 3.571)
        assert almost_equal(round(DC1["D5"]["A"], 3), 1.250)
        assert almost_equal(round(DC1["D5"]["F"], 3), 0.250)

        assert almost_equal(round(DC2["D1"]["A"], 3), 2.485)
        assert almost_equal(round(DC2["D1"]["B"], 3), 4.076)
        assert almost_equal(round(DC2["D2"]["A"], 3), 0.194)
        assert almost_equal(round(DC2["D2"]["C"], 3), -0.408)
        assert almost_equal(round(DC2["D3"]["A"], 3), 6.193)
        assert almost_equal(round(DC2["D3"]["D"], 3), 2.698)
        assert almost_equal(round(DC2["D4"]["A"], 3), 5.216)
        assert almost_equal(round(DC2["D4"]["E"], 3), 4.310)
        assert almost_equal(round(DC2["D5"]["A"], 3), 1.062)
        assert almost_equal(round(DC2["D5"]["F"], 3), 0.062)

    def test_directed(self):
        G = small_dir_G()
        DC1dir = nx.distinctiveness(G, normalize=False, alpha=1,
                                    measures=["D1", "D2", "D3", "D4", "D5"])
        DC2dir = nx.distinctiveness(G, normalize=False, alpha=2,
                                    measures=["D1", "D2", "D3", "D4", "D5"])

        assert almost_equal(round(DC1dir["D1_in"]["A"], 3), 0.194)
        assert almost_equal(round(DC1dir["D1_out"]["A"], 3), 7.689)
        assert almost_equal(round(DC1dir["D2_in"]["B"], 3), 0.398)
        assert almost_equal(round(DC1dir["D2_out"]["B"], 3), 2.194)
        assert almost_equal(round(DC1dir["D3_in"]["C"], 3), 8.340)
        assert almost_equal(round(DC1dir["D3_out"]["C"], 3), 3.000)
        assert almost_equal(round(DC1dir["D4_in"]["D"], 3), 3.364)
        assert almost_equal(round(DC1dir["D4_out"]["D"], 3), 3.571)
        assert almost_equal(round(DC1dir["D5_in"]["E"], 3), 0.500)
        assert almost_equal(round(DC1dir["D5_out"]["E"], 3), 0.000)

        assert almost_equal(round(DC2dir["D1_in"]["F"], 3), -2.526)
        assert almost_equal(round(DC2dir["D1_out"]["F"], 3), 0.000)
        assert almost_equal(round(DC2dir["D2_in"]["A"], 3), -0.505)
        assert almost_equal(round(DC2dir["D2_out"]["A"], 3), 1.398)
        assert almost_equal(round(DC2dir["D3_in"]["B"], 3), 0.373)
        assert almost_equal(round(DC2dir["D3_out"]["B"], 3), 11.418)
        assert almost_equal(round(DC2dir["D4_in"]["C"], 3), 5.216)
        assert almost_equal(round(DC2dir["D4_out"]["C"], 3), 2.077)
        assert almost_equal(round(DC2dir["D5_in"]["D"], 3), 1.062)
        assert almost_equal(round(DC2dir["D5_out"]["D"], 3), 0.250)
