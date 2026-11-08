import networkx as nx
from networkx.algorithms.fvs import is_fvs
from networkx.algorithms.fvs.fvs_iterative_compression import feedback_vertex_set


class TestIsFVS:
    """
    Tests for :func:`networkx.algorithms.fvs.is_fvs`
    """

    def test_empty_graph(self):
        G = nx.empty_graph()
        f = set()

        assert is_fvs(G, f)

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(1, 1)
        f = set()
        assert not is_fvs(G, f)

        f = {1}
        assert is_fvs(G, f)
