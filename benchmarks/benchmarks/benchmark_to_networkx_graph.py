import networkx as nx


class ToNetworkXGraphBenchmark:
    params = [nx.Graph, nx.DiGraph]
    param_names = ["graph_type"]

    def setup(self, graph_type):
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]

    def time_to_networkx_graph_direct(self, graph_type):
        _ = nx.to_networkx_graph(self.edges, create_using=graph_type)

    def time_to_networkx_graph_via_constructor(self, graph_type):
        _ = graph_type(self.edges)

    ### NOTE: Multi-instance checks are explicitly included to cover the case
    # where many graph instances are created, which is not uncommon in graph
    # analysis. The reason why multi-instance is explicitly probed (rather than
    # relying solely on the number of repeats/runs from `timeit` in the benchmark
    # suite) is to capture/amplify any distinctions from potential import
    # caching of the try-excepts in the *same* run

    def time_to_networkx_graph_direct_multi_instance(self, graph_type):
        for _ in range(500):  # Creating many graph instances
            _ = nx.to_networkx_graph(self.edges, create_using=graph_type)

    def time_to_networkx_graph_via_constructor_multi_instance(self, graph_type):
        for _ in range(500):  # Creating many graph instances
            _ = graph_type(self.edges)
