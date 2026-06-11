"""Benchmarks for distance measure functions."""

import networkx as nx


class RandomUnlabeledTree:
    seed = 42
    number_of_trees = 1000
    params = [10, 20, 50, 100, 200]
    param_names = ["n"]

    def setup(self, n):
        self.trees = nx.random_unlabeled_tree(
            n, number_of_trees=self.number_of_trees, seed=self.seed
        )

    def time_center(self, n):
        for T in self.trees:
            _ = nx.center(T)

    def time_tree_center(self, n):
        for T in self.trees:
            _ = nx.tree.center(T)
