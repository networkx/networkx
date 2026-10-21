"""Benchmarks for networkx/algorithms/core.py"""

import random

from asv_runner.benchmarks.mark import SkipNotImplemented

import networkx as nx


class CoreBenchmarks:
    seed = 42
    param_names = ["nk", "precomputed"]
    nks = (
        [100, None],
        [100, 10],
        [100, 50],
        [100, 99],
        [300, None],
        [300, 10],
        [300, 100],
        [300, 200],
    )
    precomputed = (True, False)
    params = (nks, precomputed)

    def setup(self, nk, precomputed):
        n, k = nk
        random.seed(self.seed)
        degree_sequence = [
            random.randint(0, n) for _ in range(n)
        ]  # TODO: Use a more realistic degree sequence.
        self.G = nx.expected_degree_graph(
            degree_sequence, seed=self.seed, selfloops=False
        )
        self.k = k
        self.core = nx.core_number(self.G) if precomputed else None

    def time_k_core(self, nk, precomputed):
        _ = nx.k_core(self.G, self.k, core_number=self.core)

    def time_k_shell(self, nk, precomputed):
        _ = nx.k_shell(self.G, self.k, core_number=self.core)

    def time_k_crust(self, nk, precomputed):
        _ = nx.k_crust(self.G, self.k, core_number=self.core)

    def time_k_corona(self, nk, precomputed):
        _ = nx.k_corona(self.G, self.k, core_number=self.core)

    def time_k_truss(self, nk, precomputed):
        if precomputed:
            raise SkipNotImplemented(
                f"`precomputed` not relevant for `k_truss`; skipped"
            )
        if self.k is None:
            raise SkipNotImplemented(f"`k` must be specified for `k_truss`; skipped")
        _ = nx.k_truss(self.G, self.k)
