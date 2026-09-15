import pytest

import networkx as nx
import networkx.algorithms.bipartite.rank_maximal_matching as rmm


class TestRankMaximalMatching:
    def test_rank_maximal_matching_empty_graph(self):
        G = nx.Graph()
        M = rmm.rank_maximal_matching(G)
        assert M == {}

    def test_rank_maximal_matching_no_edges(self):
        G = nx.Graph()
        G.add_nodes_from(["a1"], bipartite=0)
        G.add_nodes_from(["p1"], bipartite=1)
        M = rmm.rank_maximal_matching(G)
        assert M == {}

    def test_rank_maximal_matching_small_graph(self):
        G = nx.Graph()
        matching = {"a1": "p2", "p2": "a1"}
        G.add_nodes_from(["a1", "a2"], bipartite=0)
        G.add_nodes_from(["p1", "p2"], bipartite=1)
        G.add_weighted_edges_from([("a1", "p1", 2), ("a1", "p2", 1), ("a2", "p2", 2)])
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M == matching

    # the edge of the initial matching is not apart of the final rank maximal matching
    def test_rank_maximal_matching_simple_graph(self):
        G = nx.Graph()
        matching = {"a1": "p1", "a2": "p2", "p1": "a1", "p2": "a2"}
        G.add_nodes_from(["a1", "a2"], bipartite=0)
        G.add_nodes_from(["p1", "p2"], bipartite=1)
        G.add_weighted_edges_from([("a1", "p2", 1), ("a1", "p1", 1), ("a2", "p2", 2)])
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M == matching

    def test_rank_maximal_matching_bigger_left(self):
        G = nx.Graph()
        # there are two valid solutions
        matching = [
            {"a1": "p1", "a2": "p2", "p1": "a1", "p2": "a2"},
            {"a1": "p1", "a3": "p2", "p1": "a1", "p2": "a3"},
        ]
        G.add_nodes_from(["a1", "a2", "a3"], bipartite=0)
        G.add_nodes_from(["p1", "p2"], bipartite=1)
        G.add_weighted_edges_from(
            [("a1", "p1", 1), ("a1", "p2", 2), ("a2", "p2", 1), ("a3", "p2", 1)]
        )
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M in matching

    def test_rank_maximal_matching_bigger_right(self):
        matching = {
            "a1": "p1",
            "a3": "p4",
            "a2": "p2",
            "p1": "a1",
            "p4": "a3",
            "p2": "a2",
        }
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"], bipartite=0)
        G.add_nodes_from(["p1", "p2", "p3", "p4"], bipartite=1)
        G.add_weighted_edges_from(
            [
                ("a1", "p1", 1),
                ("a1", "p2", 1),
                ("a2", "p2", 1),
                ("a2", "p3", 2),
                ("a3", "p4", 1),
            ]
        )
        M = rmm.rank_maximal_matching(G, rank="weight", top_nodes=["a1", "a2", "a3"])
        assert M == matching

    def test_rank_maximal_matching_same_size(self):
        matching = {"a1": "p2", "a3": "p1", "p2": "a1", "p1": "a3"}
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"], bipartite=0)
        G.add_nodes_from(["p1", "p2", "p3"], bipartite=1)
        G.add_weighted_edges_from(
            [
                ("a1", "p2", 1),
                ("a1", "p3", 2),
                ("a2", "p2", 2),
                ("a3", "p1", 1),
                ("a3", "p2", 2),
            ]
        )
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M == matching

    def test_rank_maximal_matching_disconnected_graph(self):
        matching = {
            "a1": "p2",
            "a2": "p1",
            "a3": "p5",
            "a4": "p3",
            "p2": "a1",
            "p1": "a2",
            "p5": "a3",
            "p3": "a4",
        }
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3", "a4", "a5"], bipartite=0)
        G.add_nodes_from(["p1", "p2", "p3", "p4", "p5"], bipartite=1)
        G.add_weighted_edges_from(
            [
                ("a1", "p1", 1),
                ("a1", "p2", 1),
                ("a1", "p5", 2),
                ("a2", "p1", 1),
                ("a2", "p2", 2),
                ("a2", "p3", 2),
                ("a3", "p2", 1),
                ("a3", "p4", 2),
                ("a3", "p5", 1),
                ("a4", "p3", 2),
                ("a4", "p4", 3),
                ("a4", "p5", 2),
            ]
        )
        M = rmm.rank_maximal_matching(
            G, rank="weight", top_nodes=["a1", "a2", "a3", "a4", "a5"]
        )
        assert M == matching

    def test_rank_maximal_matching_perfect_matching(self):
        matching = {
            "a1": "p2",
            "a3": "p1",
            "a2": "p3",
            "p2": "a1",
            "p1": "a3",
            "p3": "a2",
        }
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"], bipartite=0)
        G.add_nodes_from(["p1", "p2", "p3"], bipartite=1)
        G.add_weighted_edges_from(
            [
                ("a1", "p2", 1),
                ("a1", "p3", 2),
                ("a2", "p2", 2),
                ("a3", "p1", 1),
                ("a3", "p2", 2),
                ("a2", "p3", 1),
            ]
        )
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M == matching

    def test_rank_maximal_matching_unordered_ranks(self):
        matching = {"a1": "p2", "a3": "p1", "p2": "a1", "p1": "a3"}
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"], bipartite=0)
        G.add_nodes_from(["p1", "p2", "p3"], bipartite=1)
        G.add_weighted_edges_from(
            [
                ("a1", "p2", 1),
                ("a1", "p3", 3),
                ("a2", "p2", 4),
                ("a3", "p1", 2),
                ("a3", "p2", 3),
            ]
        )
        M = rmm.rank_maximal_matching(G, rank="weight")
        assert M == matching

    def test_rank_maximal_matching_raises_ambiguous_solution(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "p2", 1)])
        with pytest.raises(nx.AmbiguousSolution):
            M = rmm.rank_maximal_matching(G, rank="weight")

    def test_rank_maximal_matching_weight_argument(self):
        matching = {"a1": "p1", "p1": "a1"}
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"], bipartite=0)
        G.add_nodes_from(["p1"], bipartite=1)

        # add edges without attribute
        G.add_edge("a1", "p1")
        G.add_edge("a2", "p1")
        with pytest.raises(KeyError):
            M = rmm.rank_maximal_matching(G)
        G.remove_edges_from([("a1", "p1"), ("a2", "p1")])

        # add edges with rank attribute
        G.add_edge("a1", "p1", rank=1)
        G.add_edge("a2", "p1", rank=1)
        # but rank argument = "length"
        with pytest.raises(KeyError):
            M = rmm.rank_maximal_matching(G, rank="length")
        G.remove_edges_from([("a1", "p1"), ("a2", "p1")])

        # only one edge with rank attribute
        G.add_edge("a1", "p1", rank=1)
        G.add_edge("a2", "p1")
        with pytest.raises(KeyError):
            M = rmm.rank_maximal_matching(G)
        G.remove_edges_from([("a1", "p1"), ("a2", "p1")])

        # edges with another name of attribute ("length")
        G.add_edge("a1", "p1", length=1)
        G.add_edge("a2", "p1", length=2)
        M = rmm.rank_maximal_matching(G, rank="length")
        assert M == matching
