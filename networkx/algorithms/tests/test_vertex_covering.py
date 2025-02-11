import networkx as nx


class TestIsVertexCover:
    """Tests for :func:`networkx.algorithms.is_vertex_cover`"""

    def test_empty_graph(self):
        G = nx.Graph()
        assert nx.is_vertex_cover(G, set())

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(1, 1)
        assert nx.is_vertex_cover(G, {1})

    def test_graph_double_edge(self):
        G = nx.Graph()
        G.add_edge(0, 1)
        G.add_edge(1, 2)

        assert nx.is_vertex_cover(G, {1})
        assert nx.is_vertex_cover(G, {0, 2})
        assert not nx.is_vertex_cover(G, {0})


class TestParameterizedVertexCover:
    """Tests for :func:`networkx.algorithms.vertex_cover`"""

    def test_empty_graph(self):
        G = nx.Graph()

        k = 0
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

        k = 1
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_isolated_vertices(self):
        G = nx.Graph()
        G.add_node(0)

        k = 0
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

        k = 1
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(0, 0)

        k = 0
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert not is_k_vc_exists
        assert vc == set()

        k = 1
        is_k_vc_exists, vc = nx.vertex_cover(G, 1)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_graph_with_isolated_vertex(self):
        G = nx.Graph()
        G.add_node(1)

        k = 0
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_cycle_graph(self):
        G = nx.cycle_graph(4)

        k = 2
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_complete_graph(self):
        G = nx.complete_graph(4)

        k = 2
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert not is_k_vc_exists
        assert vc == set()

        k = 3
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k
        # assert vc == {0, 1, 2}

    def test_complete_bipartite(self):
        G = nx.complete_bipartite_graph(3, 3)

        k = 2
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert not is_k_vc_exists
        assert vc == set()

        k = 3
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert is_k_vc_exists
        # assert vc == {3, 4, 5}
        assert nx.is_vertex_cover(G, vc)
        assert len(vc) <= k

    def test_crown_decomposition(self):
        """
        NOT YET COMPLETE
        """
        G = nx.random_regular_graph(3, 10, seed=0)

        k = 3
        is_k_vc_exists, vc = nx.vertex_cover(G, k)
        assert not is_k_vc_exists
        assert vc == set()
