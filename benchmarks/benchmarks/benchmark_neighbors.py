import networkx as nx


# NOTE: explicit set construction in benchmarks is required for meaningful
# comparisons due to change in return type from generator -> set. See gh-7244.
class NonNeighbors:
    param_names = ["num_nodes"]
    params = [10, 100, 1000]

    def setup(self, num_nodes):
        self.star_graph = nx.star_graph(num_nodes)
        self.complete_graph = nx.complete_graph(num_nodes)
        self.path_graph = nx.path_graph(num_nodes)

    def time_star_center(self, num_nodes):
        set(nx.non_neighbors(self.star_graph, 0))

    def time_star_rim(self, num_nodes):
        set(nx.non_neighbors(self.star_graph, 5))

    def time_complete(self, num_nodes):
        set(nx.non_neighbors(self.complete_graph, 0))

    def time_path_first(self, num_nodes):
        set(nx.non_neighbors(self.path_graph, 0))

    def time_path_last(self, num_nodes):
        set(nx.non_neighbors(self.path_graph, num_nodes - 1))

    def time_path_center(self, num_nodes):
        set(nx.non_neighbors(self.path_graph, num_nodes // 2))


# NOTE: explicit set construction in benchmarks is required for meaningful
# comparisons due to change in return type from generator -> set. See gh-7244.
class CommonNeighbors:
    param_names = ["num_nodes"]
    params = [10, 100, 1000]

    def setup(self, num_nodes):
        self.star_graph = nx.star_graph(num_nodes)
        self.complete_graph = nx.complete_graph(num_nodes)

    def time_star_center_rim(self, num_nodes):
        set(nx.common_neighbors(self.star_graph, 0, num_nodes // 2))

    def time_star_rim_rim(self, num_nodes):
        set(nx.common_neighbors(self.star_graph, 4, 5))

    def time_complete(self, num_nodes):
        set(nx.common_neighbors(self.complete_graph, 0, num_nodes // 2))
