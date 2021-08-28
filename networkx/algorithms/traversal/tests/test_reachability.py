import pytest

import networkx as nx
from networkx.utils import edges_equal


class TestReachability:
    def test_descendants(self):
        G = nx.DiGraph()
        descendants = nx.algorithms.dag.descendants
        G.add_edges_from([(1, 2), (1, 3), (4, 2), (4, 3), (4, 5), (2, 6), (5, 6)])
        assert descendants(G, 1) == {2, 3, 6}
        assert descendants(G, 4) == {2, 3, 5, 6}
        assert descendants(G, 3) == set()
        pytest.raises(nx.NetworkXError, descendants, G, 8)

    def test_ancestors(self):
        G = nx.DiGraph()
        ancestors = nx.algorithms.dag.ancestors
        G.add_edges_from([(1, 2), (1, 3), (4, 2), (4, 3), (4, 5), (2, 6), (5, 6)])
        assert ancestors(G, 6) == {1, 2, 4, 5}
        assert ancestors(G, 3) == {1, 4}
        assert ancestors(G, 1) == set()
        pytest.raises(nx.NetworkXError, ancestors, G, 8)

    def test_transitive_closure(self):
        G = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        assert edges_equal(nx.transitive_closure(G).edges(), solution)
        G = nx.DiGraph([(1, 2), (2, 3), (2, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
        assert edges_equal(nx.transitive_closure(G).edges(), solution)
        G = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
        solution = [(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1)]
        soln = sorted(solution + [(n, n) for n in G])
        assert edges_equal(sorted(nx.transitive_closure(G).edges()), soln)
        G = nx.Graph([(1, 2), (2, 3), (3, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        assert edges_equal(sorted(nx.transitive_closure(G).edges()), solution)

        # test if edge data is copied
        G = nx.DiGraph([(1, 2, {"a": 3}), (2, 3, {"b": 0}), (3, 4)])
        H = nx.transitive_closure(G)
        for u, v in G.edges():
            assert G.get_edge_data(u, v) == H.get_edge_data(u, v)

        k = 10
        G = nx.DiGraph((i, i + 1, {"f": "b", "weight": i}) for i in range(k))
        H = nx.transitive_closure(G)
        for u, v in G.edges():
            assert G.get_edge_data(u, v) == H.get_edge_data(u, v)

    def test_reflexive_transitive_closure(self):
        G = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        soln = sorted(solution + [(n, n) for n in G])
        assert edges_equal(nx.transitive_closure(G).edges(), solution)
        assert edges_equal(nx.transitive_closure(G, False).edges(), solution)
        assert edges_equal(nx.transitive_closure(G, True).edges(), soln)
        assert edges_equal(nx.transitive_closure(G, None).edges(), solution)

        G = nx.DiGraph([(1, 2), (2, 3), (2, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
        soln = sorted(solution + [(n, n) for n in G])
        assert edges_equal(nx.transitive_closure(G).edges(), solution)
        assert edges_equal(nx.transitive_closure(G, False).edges(), solution)
        assert edges_equal(nx.transitive_closure(G, True).edges(), soln)
        assert edges_equal(nx.transitive_closure(G, None).edges(), solution)

        G = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
        solution = sorted([(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1)])
        soln = sorted(solution + [(n, n) for n in G])
        assert edges_equal(sorted(nx.transitive_closure(G).edges()), soln)
        assert edges_equal(sorted(nx.transitive_closure(G, False).edges()), soln)
        assert edges_equal(sorted(nx.transitive_closure(G, None).edges()), solution)
        assert edges_equal(sorted(nx.transitive_closure(G, True).edges()), soln)

    def test_descendants_at_distance(self):
        G = nx.Graph([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        for distance, descendants in enumerate([{0}, {1}, {2, 3}, {4}]):
            assert nx.descendants_at_distance(G, 0, distance) == descendants

    def test_descendants_at_distance_missing_source(self):
        G = nx.Graph([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        with pytest.raises(nx.NetworkXError):
            nx.descendants_at_distance(G, "abc", 0)
