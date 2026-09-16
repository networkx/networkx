"""Benchmark for simple_cycles with min_length optimization.

This benchmark compares the performance of simple_cycles with and without
the min_length parameter, demonstrating the optimization from PR #8910
(search-space pruning by skipping small components).
"""

import networkx as nx


class BenchmarkSimpleCyclesMinLength:
    """Benchmark: min_length component-skipping optimization.

    The optimization skips strongly connected components (for directed) or
    biconnected components (for undirected) that have fewer nodes than
    min_length, since such components cannot contain cycles of the required
    minimum length.
    """

    params = [10, 50, 100]

    def setup(self, n):
        # Create a graph with one large component and many small components
        self.graph = nx.complete_graph(n, create_using=nx.DiGraph)
        # Add small 2-node components that would be skipped with min_length=3
        for i in range(n, n + 20):
            self.graph.add_edge(i, i + 1)
            self.graph.add_edge(i + 1, i)

    def time_without_min_length(self, n):
        """Baseline: enumerate all cycles (including small ones)."""
        list(nx.simple_cycles(self.graph))

    def time_with_min_length_pruning(self, n):
        """Optimized: skip components smaller than min_length."""
        list(nx.simple_cycles(self.graph, min_length=n))
