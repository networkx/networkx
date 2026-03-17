"""Benchmarks for a certain set of algorithms"""

import random

import networkx as nx
from benchmarks.utils import (
    benchmark_name_from_func_call,
    fetch_drug_interaction_network,
    weighted_graph,
)
from networkx.algorithms import community


class UndirectedAlgorithmBenchmarks:
    timeout = 120
    nodes = 100
    _graphs = [
        nx.erdos_renyi_graph(nodes, 0.1),
        nx.erdos_renyi_graph(nodes, 0.5),
        nx.erdos_renyi_graph(nodes, 0.9),
        fetch_drug_interaction_network(),
    ]
    params = [
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
        "Drug Interaction network",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_betweenness_centrality(self, graph):
        # timing this should also give us information about
        # underlying shortest path methods
        _ = nx.betweenness_centrality(self.graphs_dict[graph])

    def time_greedy_modularity_communities(self, graph):
        _ = community.greedy_modularity_communities(self.graphs_dict[graph])

    def time_louvain_communities(self, graph):
        _ = community.louvain_communities(self.graphs_dict[graph])

    def time_pagerank(self, graph):
        _ = nx.pagerank(self.graphs_dict[graph])

    def time_connected_components(self, graph):
        _ = list(nx.connected_components(self.graphs_dict[graph]))

    def time_k_core(self, graph):
        _ = nx.k_core(self.graphs_dict[graph])

    def time_average_clustering(self, graph):
        _ = nx.average_clustering(self.graphs_dict[graph])

    def time_minimum_spanning_tree_kruskal(self, graph):
        _ = nx.minimum_spanning_tree(self.graphs_dict[graph], algorithm="kruskal")


class DirectedAlgorithmBenchmarks:
    timeout = 120
    seed = 42
    _graphs = [
        nx.erdos_renyi_graph(100, 0.005, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.01, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.05, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.1, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.5, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.0005, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.001, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.005, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.01, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.05, seed=seed, directed=True),
        nx.erdos_renyi_graph(10000, 0.00005, seed=seed, directed=True),
        nx.erdos_renyi_graph(10000, 0.0001, seed=seed, directed=True),
        nx.erdos_renyi_graph(10000, 0.0005, seed=seed, directed=True),
        nx.empty_graph(100, create_using=nx.DiGraph),
        nx.empty_graph(1000, create_using=nx.DiGraph),
        nx.empty_graph(10000, create_using=nx.DiGraph),
        nx.complete_graph(100, create_using=nx.DiGraph),
        nx.complete_graph(1000, create_using=nx.DiGraph),
    ]
    params = [
        "Erdos Renyi (100, 0.005)",
        "Erdos Renyi (100, 0.01)",
        "Erdos Renyi (100, 0.05)",
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (1000, 0.0005)",
        "Erdos Renyi (1000, 0.001)",
        "Erdos Renyi (1000, 0.005)",
        "Erdos Renyi (1000, 0.01)",
        "Erdos Renyi (1000, 0.05)",
        "Erdos Renyi (10000, 0.00005)",
        "Erdos Renyi (10000, 0.0001)",
        "Erdos Renyi (10000, 0.0005)",
        "Empty (100)",
        "Empty (1000)",
        "Empty (10000)",
        "Complete (100)",
        "Complete (1000)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_tarjan_scc(self, graph):
        _ = list(nx.strongly_connected_components(self.graphs_dict[graph]))

    def time_kosaraju_scc(self, graph):
        _ = list(nx.kosaraju_strongly_connected_components(self.graphs_dict[graph]))


class AlgorithmBenchmarksConnectedGraphsOnly:
    timeout = 120
    nodes = 100
    _graphs = [
        nx.erdos_renyi_graph(nodes, 0.1),
        nx.erdos_renyi_graph(nodes, 0.5),
        nx.erdos_renyi_graph(nodes, 0.9),
    ]
    params = [
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_eigenvector_centrality_numpy(self, graph):
        # Added to ensure the connectivity check doesn't affect
        # performance too much (see gh-6888, gh-7549).
        _ = nx.eigenvector_centrality_numpy(self.graphs_dict[graph])

    def time_square_clustering(self, graph):
        _ = nx.square_clustering(self.graphs_dict[graph])


def _make_tournament_benchmark_graphs(seed):
    number_of_nodes = [10, 100, 1000]
    graphs = {}
    for nodes in number_of_nodes:
        G = nx.tournament.random_tournament(nodes, seed=seed)
        graphs[f"Tournament ({nodes}, seed={seed})"] = G
    return graphs


class ReachabilityBenchmark:
    timeout = 120
    _seed = 42
    param_names = ["graph"]

    _graphs = _make_tournament_benchmark_graphs(_seed)
    params = list(_graphs)

    def setup(self, graph):
        self.G = self._graphs[graph]
        self.nodes = sorted(self.G)
        rng = random.Random(self._seed)
        self.source, self.target = rng.sample(self.nodes, 2)

    def time_is_reachable(self, graph):
        _ = nx.tournament.is_reachable(self.G, self.source, self.target)


def _make_weighted_benchmark_graphs(seed):
    erdos_renyi_graphs = [
        (nx.erdos_renyi_graph, (nodes, p), {"seed": seed})
        for nodes in [10, 100, 1_000]
        for p in [0.1, 0.5, 0.9]
    ]

    path_graphs = [
        (nx.path_graph, (nodes,), {}) for nodes in [100, 1_000, 10_000, 20_000]
    ]

    def dijkstra_relaxation_worst_case(n):
        """
        Build a graph on n nodes that makes Dijkstra relax every edge.

        Idea:
        - Nodes are 0..n-1.
        - For each i < j, add edge (i, j) with weight = 2*(j-1-i)+1.
        - Shortest paths are the chain 0->1->...->k (distance = k).
        - Each predecessor i < j gives a strictly better tentative distance to j,
            so every edge (i, j) is relaxed.

        The graph has Θ(n^2) edges and forces Θ(n^2) relaxations,
        which is the worst case for Dijkstra.
        """
        G = nx.empty_graph(n)
        for i in range(n):
            for j in range(i + 1, n):
                G.add_edge(i, j, weight=2 * (j - 1 - i) + 1)
        return G

    all_graphs = {
        benchmark_name_from_func_call(dijkstra_relaxation_worst_case, n): (
            dijkstra_relaxation_worst_case,
            (n,),
            {},
        )
        for n in [10, 100, 1_000]
    }
    for graph_func, args, kwargs in path_graphs + erdos_renyi_graphs:
        name = benchmark_name_from_func_call(
            weighted_graph, seed, graph_func, *args, **kwargs
        )
        all_graphs[name] = (weighted_graph, (seed, graph_func, *args), dict(**kwargs))
    return all_graphs


class WeightedGraphBenchmark:
    """Benchmark for shortest path algorithms on various weighted graphs."""

    timeout = 120
    _seed = 42
    param_names = ["graph"]

    _graphs = _make_weighted_benchmark_graphs(_seed)
    params = list(_graphs)

    def setup(self, graph):
        f, args, kwargs = self._graphs[graph]
        self.G = f(*args, **kwargs)
        self.nodes = sorted(self.G)

    def time_weighted_single_source_dijkstra(self, graph):
        source = self.nodes[0]
        target = self.nodes[-1]
        try:
            _ = nx.single_source_dijkstra(self.G, source, target)
        except nx.NetworkXNoPath:
            pass

    def time_shortest_path(self, graph):
        source = self.nodes[0]
        target = self.nodes[-1]
        nx.shortest_path(self.G, source, target, weight="weight")
