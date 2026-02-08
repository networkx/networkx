import networkx as nx


class ChordalBenchmarks:
    param_names = ["num_nodes"]
    params = [5, 10, 50, 100]

    def setup(self, num_nodes):
        self.star_graph = nx.star_graph(num_nodes)
        self.wheel_graph = nx.wheel_graph(num_nodes)
        self.complete_graph = nx.complete_graph(num_nodes)
        self.path_graph = nx.path_graph(num_nodes)
        self.cycle_graph = nx.cycle_graph(num_nodes)

    def time_is_chordal_complete(self, num_nodes):
        """complete graphs are chordal"""
        nx.is_chordal(self.complete_graph)

    def time_is_chordal_star(self, num_nodes):
        """star graph -> no cycles -> trivially chordal"""
        nx.is_chordal(self.star_graph)

    def time_is_chordal_path(self, num_nodes):
        """Same with path: no cycles, therefore trivially chordal"""
        nx.is_chordal(self.path_graph)

    def time_is_chordal_wheel(self, num_nodes):
        """Like star graph, except all triangles"""
        nx.is_chordal(self.wheel_graph)

    def time_is_chordal_cycle_graph(self, num_nodes):
        """Not chordal, finding chordality breaker requires querying whole graph"""
        nx.is_chordal(self.cycle_graph)
