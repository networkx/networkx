import pytest

import networkx as nx
from networkx.algorithms import bipartite


class TestAlphaBetaCore:
    @classmethod
    def setup_class(cls):
        cls.B1 = nx.Graph()
        cls.B1.add_edges_from([(1, "a"), (1, "b"), (2, "b"), (2, "c"), (3, "c")])

        cls.B2 = nx.complete_bipartite_graph(3, 3)

        cls.B3 = nx.Graph()
        cls.B3.add_edges_from(
            [(1, "x"), (1, "y"), (2, "y"), (2, "z"), (3, "z"), (3, "x")]
        )

        cls.B4 = nx.Graph()
        cls.B4.add_edges_from([(1, "a"), (1, "b"), ("a", "b")])

    def test_alpha_beta_core_basic(self):
        G_ab_core = bipartite.alpha_beta_core(self.B1, alpha=1, beta=2)
        normalized_edges = {tuple(sorted(map(str, edge))) for edge in G_ab_core.edges}
        expected_edges = {
            tuple(sorted(map(str, edge)))
            for edge in [(1, "b"), (2, "b"), (2, "c"), (3, "c")]
        }
        assert (
            normalized_edges == expected_edges
        ), f"Expected edges {expected_edges}, but got {normalized_edges}"

    def test_alpha_beta_core_complete(self):
        G_ab_core = bipartite.alpha_beta_core(self.B2, alpha=1, beta=1)
        assert set(G_ab_core.edges) == set(self.B2.edges)

        G_ab_core = bipartite.alpha_beta_core(self.B2, alpha=3, beta=3)
        assert set(G_ab_core.edges) == set(self.B2.edges)

    def test_alpha_beta_core_no_nodes_left(self):
        G_ab_core = bipartite.alpha_beta_core(self.B1, alpha=4, beta=4)
        assert set(G_ab_core.edges) == set()

    def test_alpha_beta_core_invalid_input(self):
        with pytest.raises(nx.NetworkXError, match="Graph is not bipartite"):
            bipartite.alpha_beta_core(self.B4, alpha=2, beta=2)

        with pytest.raises(
            nx.NetworkXError, match="alpha and beta must be greater than 0"
        ):
            bipartite.alpha_beta_core(self.B1, alpha=0, beta=2)

        with pytest.raises(
            nx.NetworkXError, match="alpha and beta must be greater than 0"
        ):
            bipartite.alpha_beta_core(self.B1, alpha=1, beta=-1)

    def test_alpha_beta_core_complex_structure(self):
        G_ab_core = bipartite.alpha_beta_core(self.B3, alpha=2, beta=2)
        assert set(G_ab_core.edges) == set(self.B3.edges)
