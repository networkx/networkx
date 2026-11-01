import networkx as nx
from benchmarks.utils import fetch_drug_interaction_network

GRAPH_SPECS = [
    ("barabasi_albert_graph", (10_000, 3), ()),
    ("powerlaw_cluster_graph", (5_000, 3, 0.1), ()),
    ("powerlaw_cluster_graph", (5_000, 5, 0.3), ()),
    ("random_geometric_graph", (3_000, 0.025), ()),
    ("gaussian_random_partition_graph", (3_000, 40, 10, 0.1, 0.001), ()),
    ("connected_watts_strogatz_graph", (5_000, 10, 0.05), (("tries", 100),)),
    ("gnp_random_graph", (1_000, 0.01), ()),
    ("gnp_random_graph", (1_000, 0.1), ()),
    ("complete_graph", (300,), ()),
    ("drug_interaction_network", (), ()),
]


def build_graph(name, args, kwargs_items, seed):
    if name == "drug_interaction_network":
        return fetch_drug_interaction_network()

    graph_func = getattr(nx, name)
    kwargs = dict(kwargs_items)
    if name != "complete_graph":
        kwargs["seed"] = seed
    return graph_func(*args, **kwargs)


class Triangles:
    timeout = 120
    seed = 42
    params = (GRAPH_SPECS,)
    param_names = ["graph"]

    def setup_cache(self):
        return {
            graph_spec: build_graph(*graph_spec, seed=self.seed)
            for graph_spec in GRAPH_SPECS
        }

    def setup(self, graphs, graph_spec):
        self.G = graphs[graph_spec]

    def time_triangles(self, graphs, graph_spec):
        _ = nx.triangles(self.G)
