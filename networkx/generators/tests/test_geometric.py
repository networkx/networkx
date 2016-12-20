from itertools import combinations
from math import sqrt

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true

import networkx as nx


class TestRandomGeometricGraph(object):
    """Unit tests for the :func:`~networkx.random_geometric_graph`
    function.

    """

    def test_number_of_nodes(self):
        G = nx.random_geometric_graph(50, 0.25)
        assert_equal(len(G), 50)
        G = nx.random_geometric_graph(range(50), 0.25)
        assert_equal(len(G), 50)

    def test_distances(self):
        """Tests that pairs of vertices adjacent if and only if they are
        within the prescribed radius.

        """
        # Use the Euclidean metric, the default according to the
        # documentation.
        dist = lambda x, y: sqrt(sum((a - b) ** 2 for a, b in zip(x, y)))
        G = nx.random_geometric_graph(50, 0.25)
        for u, v in combinations(G, 2):
            # Adjacent vertices must be within the given distance.
            if v in G[u]:
                assert_true(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)
            # Nonadjacent vertices must be at greater distance.
            else:
                assert_false(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)

    def test_p(self):
        """Tests for providing an alternate distance metric to the
        generator.

        """
        # Use the L1 metric.
        dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
        G = nx.random_geometric_graph(50, 0.25, p=1)
        for u, v in combinations(G, 2):
            # Adjacent vertices must be within the given distance.
            if v in G[u]:
                assert_true(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)
            # Nonadjacent vertices must be at greater distance.
            else:
                assert_false(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)

    def test_node_names(self):
        """Tests using values other than sequential numbers as node IDs.

        """
        import string
        nodes = list(string.ascii_lowercase)
        G = nx.random_geometric_graph(nodes, 0.25)
        assert_equal(len(G), len(nodes))

        dist = lambda x, y: sqrt(sum((a - b) ** 2 for a, b in zip(x, y)))
        for u, v in combinations(G, 2):
            # Adjacent vertices must be within the given distance.
            if v in G[u]:
                assert_true(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)
            # Nonadjacent vertices must be at greater distance.
            else:
                assert_false(dist(G.node[u]['pos'], G.node[v]['pos']) <= 0.25)


def join(G, u, v, theta, alpha, metric):
    """Returns ``True`` if and only if the nodes whose attributes are
    ``du`` and ``dv`` should be joined, according to the threshold
    condition for geographical threshold graphs.

    ``G`` is an undirected NetworkX graph, and ``u`` and ``v`` are nodes
    in that graph. The nodes must have node attributes ``'pos'`` and
    ``'weight'``.

    ``metric`` is a distance metric.

    """
    du, dv = G.node[u], G.node[v]
    u_pos, v_pos = du['pos'], dv['pos']
    u_weight, v_weight = du['weight'], dv['weight']
    return theta * metric(u_pos, v_pos) ** alpha <= u_weight + v_weight


class TestGeographicalThresholdGraph(object):
    """Unit tests for the :func:`~networkx.geographical_threshold_graph`
    function.

    """

    def test_number_of_nodes(self):
        G = nx.geographical_threshold_graph(50, 100)
        assert_equal(len(G), 50)
        G = nx.geographical_threshold_graph(range(50), 100)
        assert_equal(len(G), 50)

    def test_distances(self):
        """Tests that pairs of vertices adjacent if and only if their
        distances meet the given threshold.

        """
        # Use the Euclidean metric, the default according to the
        # documentation.
        dist = lambda x, y: sqrt(sum((a - b) ** 2 for a, b in zip(x, y)))
        G = nx.geographical_threshold_graph(50, 100)
        for u, v in combinations(G, 2):
            # Adjacent vertices must not exceed the threshold.
            if v in G[u]:
                assert_true(join(G, u, v, 100, 2, dist))
            # Nonadjacent vertices must exceed the threshold.
            else:
                assert_false(join(G, u, v, 100, 2, dist))

    def test_metric(self):
        """Tests for providing an alternate distance metric to the
        generator.

        """
        # Use the L1 metric.
        dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
        G = nx.geographical_threshold_graph(50, 100, metric=dist)
        for u, v in combinations(G, 2):
            # Adjacent vertices must not exceed the threshold.
            if v in G[u]:
                assert_true(join(G, u, v, 100, 2, dist))
            # Nonadjacent vertices must exceed the threshold.
            else:
                assert_false(join(G, u, v, 100, 2, dist))


class TestWaxmanGraph(object):
    """Unit tests for the :func:`~networkx.waxman_graph` function."""

    def test_number_of_nodes_1(self):
        G = nx.waxman_graph(50, 0.5, 0.1)
        assert_equal(len(G), 50)
        G = nx.waxman_graph(range(50), 0.5, 0.1)
        assert_equal(len(G), 50)

    def test_number_of_nodes_2(self):
        G = nx.waxman_graph(50, 0.5, 0.1, L=1)
        assert_equal(len(G), 50)
        G = nx.waxman_graph(range(50), 0.5, 0.1, L=1)
        assert_equal(len(G), 50)

    def test_metric(self):
        """Tests for providing an alternate distance metric to the
        generator.

        """
        dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
        G = nx.waxman_graph(50, 0.5, 0.1, metric=dist)
        assert_equal(len(G), 50)


class TestNavigableSmallWorldGraph(object):

    def test_navigable_small_world(self):
        G = nx.navigable_small_world_graph(5, p=1, q=0)
        gg = nx.grid_2d_graph(5, 5).to_directed()
        assert_true(nx.is_isomorphic(G, gg))

        G = nx.navigable_small_world_graph(5, p=1, q=0, dim=3)
        gg = nx.grid_graph([5, 5, 5]).to_directed()
        assert_true(nx.is_isomorphic(G, gg))

        G = nx.navigable_small_world_graph(5, p=1, q=0, dim=1)
        gg = nx.grid_graph([5]).to_directed()
        assert_true(nx.is_isomorphic(G, gg))
