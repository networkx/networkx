import networkx as nx
from networkx.algorithms.fvs import is_fvs
from networkx.algorithms.fvs.fvs_iterative_compression import feedback_vertex_set


class TestParameterizedFVS:
    """
    Tests for :func:`networkx.algorithms.fvs.fvs_iterative_compression.feedback_vertex_set`
    """

    def test_empty_graph(self):
        G = nx.empty_graph()
        k = 0
        is_k_fvs_exists, fvs = feedback_vertex_set(G, k)
        assert is_k_fvs_exists
        assert is_fvs(G, fvs)
        assert len(fvs) <= k

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(1, 1)
        k = 0
        is_k_fvs_exists, fvs = feedback_vertex_set(G, k)
        assert not is_k_fvs_exists
        assert fvs == set()

        k = 1
        is_k_fvs_exists, fvs = feedback_vertex_set(G, k)
        assert is_k_fvs_exists
        assert len(fvs) <= k
        assert is_fvs(G, fvs)

    def test_graph(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (0, 1),
                (0, 2),
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (2, 5),
                (2, 6),
                (3, 4),
                (4, 5),
                (5, 6),
            ]
        )

        k = 1
        is_k_fvs_exists, fvs = feedback_vertex_set(G, k)

        assert not is_k_fvs_exists
        assert fvs == set()

        k = 4
        is_k_fvs_exists, fvs = feedback_vertex_set(G, k)

        assert is_k_fvs_exists
