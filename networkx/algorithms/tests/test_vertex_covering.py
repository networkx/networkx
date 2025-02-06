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
        is_k_vc_exists, vc = nx.vertex_cover(G, 0)
        assert is_k_vc_exists
        assert vc == set()

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(0, 0)

        is_k_vc_exists, vc = nx.vertex_cover(G, 0)
        assert not is_k_vc_exists
        assert vc == set()

        is_k_vc_exists, vc = nx.vertex_cover(G, 1)
        assert is_k_vc_exists
        assert vc == set({0})

    def test_graph_with_isolated_vertex(self):
        G = nx.Graph()
        G.add_node(1)

        is_k_vc_exists, vc = nx.vertex_cover(G, 0)
        assert is_k_vc_exists
        assert vc == set()
