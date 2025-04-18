import itertools

import pytest

import networkx as nx
from networkx.algorithms import bipartite

pytest.importorskip("scipy")


class TestBipartiteLinkAnalysis:
    @classmethod
    def setup_class(cls):
        cls.davis_southern_women_graph = nx.davis_southern_women_graph()
        cls.women_bipartite_set = {
            node
            for node, bipartite in cls.davis_southern_women_graph.nodes(
                data="bipartite"
            )
            if bipartite == 0
        }

    def test_collaborative_filtering_birank(self):
        elist = [
            ("u1", "p1", 5),
            ("u2", "p1", 5),
            ("u2", "p2", 4),
            ("u3", "p1", 3),
            ("u3", "p3", 2),
        ]
        item_recommendation_graph = nx.DiGraph()
        item_recommendation_graph.add_weighted_edges_from(elist, weight="rating")
        product_nodes = ("p1", "p2", "p3")
        u1_query = {
            product: rating
            for _, product, rating in item_recommendation_graph.edges(
                nbunch="u1", data="rating"
            )
        }
        u1_birank_results = bipartite.birank(
            item_recommendation_graph,
            product_nodes,
            alpha=0.8,
            beta=1.0,
            top_personalization=u1_query,
            weight="rating",
        )

        assert u1_birank_results["p2"] > u1_birank_results["p3"] + 2 * 1e-6

        u1_birank_results_unweighted = bipartite.birank(
            item_recommendation_graph,
            product_nodes,
            alpha=0.8,
            beta=1.0,
            top_personalization=u1_query,
            weight=None,
        )

        assert u1_birank_results_unweighted["p2"] == pytest.approx(
            u1_birank_results_unweighted["p3"], rel=1e-6
        )

    def test_davis_birank(self):
        scores = bipartite.birank(
            self.davis_southern_women_graph, self.women_bipartite_set
        )
        answer = {
            "Nora Fayette": 0.08,
            "Flora Price": 0.04,
            "Helen Lloyd": 0.06,
            "Verne Sanderson": 0.05,
            "Brenda Rogers": 0.07,
            "Myra Liddel": 0.05,
            "Dorothy Murchison": 0.04,
            "Eleanor Nye": 0.05,
            "Theresa Anderson": 0.08,
            "Ruth DeSand": 0.05,
            "Pearl Oglethorpe": 0.05,
            "Charlotte McDowd": 0.05,
            "Laura Mandeville": 0.07,
            "Katherina Rogers": 0.07,
            "Sylvia Avondale": 0.07,
            "Frances Anderson": 0.05,
            "Evelyn Jefferson": 0.08,
            "Olivia Carleton": 0.04,
            "E1": 0.05,
            "E2": 0.05,
            "E13": 0.05,
            "E12": 0.07,
            "E4": 0.05,
            "E14": 0.05,
            "E11": 0.05,
            "E3": 0.07,
            "E7": 0.09,
            "E10": 0.06,
            "E8": 0.1,
            "E9": 0.09,
            "E6": 0.08,
            "E5": 0.08,
        }

        for node, value in answer.items():
            assert scores[node] == pytest.approx(value, abs=1e-2)

    def test_birank_empty_bipartite_set(self):
        G = nx.Graph()
        all_nodes = [1, 2, 3]
        G.add_nodes_from(all_nodes)

        # Test with empty bipartite set
        with pytest.raises(nx.NetworkXAlgorithmError):
            bipartite.birank(G, [1, 2, 3])

    @pytest.mark.parametrize(
        "damping_factor,value", itertools.product(["alpha", "beta"], [-0.1, 1.1])
    )
    def test_birank_invalid_alpha_beta(self, damping_factor, value):
        kwargs = {damping_factor: value}
        with pytest.raises(nx.NetworkXAlgorithmError):
            bipartite.birank(
                self.davis_southern_women_graph, self.women_bipartite_set, **kwargs
            )

    def test_birank_power_iteration_failed_convergence(self):
        with pytest.raises(nx.PowerIterationFailedConvergence):
            bipartite.birank(
                self.davis_southern_women_graph, self.women_bipartite_set, max_iter=1
            )
