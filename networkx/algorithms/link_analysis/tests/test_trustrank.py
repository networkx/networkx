import pytest

import networkx as nx
from networkx.algorithms.link_analysis.pagerank_alg import pagerank
from networkx.algorithms.link_analysis.trustrank_alg import trustrank


class TestTrustRank:
    @classmethod
    def setup_class(cls):
        """Set up a graph and pre-calculate expected values."""
        G = nx.DiGraph()
        edges = [
            (1, 2),
            (1, 3),  # Seed 1 links to 2 and 3
            (2, 4),  # 2 links to 4
            (3, 4),
            (3, 5),  # 3 links to 4 and 5
            (4, 1),  # 4 links back to a seed
            (5, 6),  # 5 links to 6 (a sink)
        ]
        G.add_edges_from(edges)
        cls.G = G
        cls.seed_nodes = {1, 3}

        # Calculate expected values by calling pagerank with personalization
        personalization = {n: 1.0 / len(cls.seed_nodes) for n in cls.seed_nodes}
        cls.expected_tr = pagerank(G, alpha=0.85, personalization=personalization)

    def test_trustrank_calculation(self):
        """Tests if trustrank gives the correct, pre-calculated values."""
        tr = trustrank(self.G, seed_nodes=self.seed_nodes)
        for node, score in self.expected_tr.items():
            assert tr[node] == pytest.approx(score, abs=1e-7)

    def test_trustrank_vs_pagerank_personalization(self):
        """Tests if trustrank is equivalent to pagerank with personalization."""
        tr_via_trustrank = trustrank(self.G, seed_nodes=self.seed_nodes)

        personalization = {n: 1.0 / len(self.seed_nodes) for n in self.seed_nodes}
        tr_via_pagerank = pagerank(self.G, personalization=personalization)

        # The results should be identical
        assert tr_via_trustrank == tr_via_pagerank

    def test_no_seed_nodes_equals_pagerank(self):
        """Tests if trustrank with no seeds is equivalent to standard pagerank."""
        tr = trustrank(self.G, seed_nodes=None)
        pr = pagerank(self.G)
        assert tr == pr

    def test_empty_seed_nodes_raises_error(self):
        """Tests that an empty seed set raises ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            trustrank(self.G, seed_nodes=[])

    def test_seed_not_in_graph_raises_error(self):
        """Tests that a seed node not in the graph raises NetworkXError."""
        bad_seeds = self.seed_nodes.union({99})  # Node 99 is not in G
        with pytest.raises(nx.NetworkXError):
            trustrank(self.G, seed_nodes=bad_seeds)

    def test_logical_trust_distribution(self):
        """Tests that trust score decreases with distance from a seed."""
        # On a path graph, score should decrease with distance
        G_path = nx.path_graph(5, create_using=nx.DiGraph)  # 0->1->2->3->4
        seeds = {0}
        tr = trustrank(G_path, seed_nodes=seeds)
        # Trust should be highest at the seed and decay along the path
        assert tr[0] > tr[1] > tr[2] > tr[3] > tr[4]

    def test_trustrank_on_undirected_graph(self):
        """Tests trustrank on an undirected complete graph."""
        G = nx.complete_graph(5)
        seeds = {0, 1}
        tr = trustrank(G, seed_nodes=seeds)

        # In a complete graph, with seeds 0 and 1, their scores should be equal
        # and higher than the non-seed nodes.
        # The scores for non-seed nodes (2, 3, 4) should also be equal.
        assert tr[0] == pytest.approx(tr[1])
        assert tr[2] == pytest.approx(tr[3])
        assert tr[3] == pytest.approx(tr[4])
        assert tr[0] > tr[2]

    def test_empty_graph(self):
        """Tests trustrank on an empty graph."""
        G = nx.Graph()
        assert trustrank(G, seed_nodes=None) == {}
        # Also test with seeds that don't exist in the empty graph
        with pytest.raises(nx.NetworkXError):
            trustrank(G, seed_nodes={1})
