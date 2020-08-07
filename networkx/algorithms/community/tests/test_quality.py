"""Unit tests for the :mod:`networkx.algorithms.community.quality`
module.

"""

import networkx as nx
from networkx import barbell_graph
from networkx.algorithms.community import coverage
from networkx.algorithms.community import modularity
from networkx.algorithms.community import performance
from networkx.algorithms.community.quality import inter_community_edges
from networkx.testing import almost_equal


class TestPerformance:
    """Unit tests for the :func:`performance` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low performance measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert almost_equal(8 / 15, performance(G, partition))

    def test_good_partition(self):
        """Tests that a good partition has a high performance measure.

        """
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert almost_equal(14 / 15, performance(G, partition))


class TestCoverage:
    """Unit tests for the :func:`coverage` function."""

    def test_bad_partition(self):
        """Tests that a poor partition has a low coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 4}, {2, 3, 5}]
        assert almost_equal(3 / 7, coverage(G, partition))

    def test_good_partition(self):
        """Tests that a good partition has a high coverage measure."""
        G = barbell_graph(3, 0)
        partition = [{0, 1, 2}, {3, 4, 5}]
        assert almost_equal(6 / 7, coverage(G, partition))


def test_modularity():
    G = nx.barbell_graph(3, 0)
    C = [{0, 1, 4}, {2, 3, 5}]
    assert almost_equal(-16 / (14 ** 2), modularity(G, C))
    C = [{0, 1, 2}, {3, 4, 5}]
    assert almost_equal((35 * 2) / (14 ** 2), modularity(G, C))

    n = 1000
    G = nx.erdos_renyi_graph(n, 0.09, seed=42, directed=True)
    C = [set(range(n // 2)), set(range(n // 2, n))]
    assert almost_equal(0.00017154251389292754, modularity(G, C))

    G = nx.margulis_gabber_galil_graph(10)
    mid_value = G.number_of_nodes() // 2
    nodes = list(G.nodes)
    C = [set(nodes[:mid_value]), set(nodes[mid_value:])]
    assert almost_equal(0.13, modularity(G, C))

    G = nx.DiGraph()
    G.add_edges_from([(2, 1), (2, 3), (3, 4)])
    C = [{1, 2}, {3, 4}]
    assert almost_equal(2 / 9, modularity(G, C))


def test_inter_community_edges_with_digraphs():
    G = nx.complete_graph(2, create_using=nx.DiGraph())
    partition = [{0}, {1}]
    assert inter_community_edges(G, partition) == 2

    G = nx.complete_graph(10, create_using=nx.DiGraph())
    partition = [{0}, {1, 2}, {3, 4, 5}, {6, 7, 8, 9}]
    assert inter_community_edges(G, partition) == 70

    G = nx.cycle_graph(4, create_using=nx.DiGraph())
    partition = [{0, 1}, {2, 3}]
    assert inter_community_edges(G, partition) == 2
