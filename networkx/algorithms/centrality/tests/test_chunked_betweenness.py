import tracemalloc

import pytest

import networkx as nx


class TestChunkedBetweennessCentrality:
    def test_chunked_matches_standard_path_graph(self):
        G = nx.path_graph(10)
        standard = nx.betweenness_centrality(G, normalized=False)
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=3)
        assert standard == chunked

    def test_chunked_matches_standard_complete_graph(self):
        G = nx.complete_graph(8)
        standard = nx.betweenness_centrality(G, normalized=True)
        chunked = nx.betweenness_centrality(G, normalized=True, chunk_size=2)
        assert standard == chunked

    def test_chunked_matches_standard_directed(self):
        G = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
        standard = nx.betweenness_centrality(G, normalized=False)
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=2)
        assert standard == chunked

    def test_chunked_with_endpoints(self):
        G = nx.path_graph(5)
        standard = nx.betweenness_centrality(G, normalized=True, endpoints=True)
        chunked = nx.betweenness_centrality(
            G, normalized=True, endpoints=True, chunk_size=2
        )
        assert standard == chunked

    def test_chunked_weighted_graph(self):
        G = nx.Graph()
        G.add_weighted_edges_from([(0, 1, 1.0), (1, 2, 2.0), (2, 3, 1.0), (0, 3, 4.0)])
        standard = nx.betweenness_centrality(G, weight="weight", normalized=False)
        chunked = nx.betweenness_centrality(
            G, weight="weight", normalized=False, chunk_size=2
        )
        assert standard == chunked

    def test_chunked_with_k_sampling(self):
        G = nx.erdos_renyi_graph(20, 0.2, seed=42)
        standard = nx.betweenness_centrality(G, k=10, seed=42, normalized=False)
        chunked = nx.betweenness_centrality(
            G, k=10, seed=42, normalized=False, chunk_size=3
        )
        assert standard == chunked

    def test_chunk_size_larger_than_nodes(self):
        G = nx.path_graph(5)
        standard = nx.betweenness_centrality(G, normalized=False)
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=100)
        assert standard == chunked

    def test_chunk_size_one(self):
        G = nx.cycle_graph(6)
        standard = nx.betweenness_centrality(G, normalized=True)
        chunked = nx.betweenness_centrality(G, normalized=True, chunk_size=1)
        assert standard == chunked

    def test_chunked_disconnected_graph(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_edges_from([(3, 4), (4, 5)])
        standard = nx.betweenness_centrality(G, normalized=False)
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=2)
        assert standard == chunked

    def test_chunked_krackhardt_kite(self):
        G = nx.krackhardt_kite_graph()
        standard = nx.betweenness_centrality(G, normalized=True)
        chunked = nx.betweenness_centrality(G, normalized=True, chunk_size=3)
        for node in G:
            assert abs(standard[node] - chunked[node]) < 1e-10

    def test_chunked_barabasi_albert(self):
        G = nx.barabasi_albert_graph(30, 2, seed=42)
        standard = nx.betweenness_centrality(G, normalized=False)
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=5)
        for node in G:
            assert abs(standard[node] - chunked[node]) < 1e-10

    def test_chunked_memory_reduction(self):
        G = nx.erdos_renyi_graph(100, 0.05, seed=42)

        tracemalloc.start()
        standard = nx.betweenness_centrality(G, normalized=False)
        standard_peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        tracemalloc.start()
        chunked = nx.betweenness_centrality(G, normalized=False, chunk_size=10)
        chunked_peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        assert standard == chunked
        print(f"Standard peak: {standard_peak / 1024 / 1024:.2f} MB")
        print(f"Chunked peak: {chunked_peak / 1024 / 1024:.2f} MB")
        print(f"Reduction: {(1 - chunked_peak / standard_peak) * 100:.1f}%")
