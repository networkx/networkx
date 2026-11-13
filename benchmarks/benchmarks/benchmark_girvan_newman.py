"""Girvan-Newman cost on empirical networks and a connected dense graph."""

from typing import ClassVar

import networkx as nx


class GirvanNewman:
    params: ClassVar[list[str]] = [
        "karate",
        "davis",
        "florentine",
        "les_miserables",
        "complete_30",
    ]
    param_names: ClassVar[list[str]] = ["graph"]
    timeout = 120

    def setup(self, graph):
        factories = {
            "karate": nx.karate_club_graph,
            "davis": nx.davis_southern_women_graph,
            "florentine": nx.florentine_families_graph,
            "les_miserables": nx.les_miserables_graph,
            "complete_30": lambda: nx.complete_graph(30),
        }
        self.graph = factories[graph]()

    def time_first_partition(self, graph):
        next(nx.community.girvan_newman(self.graph))

    def time_all_partitions(self, graph):
        for _ in nx.community.girvan_newman(self.graph):
            pass
