import networkx as nx


class ConvertCompleteGraph:
    params = [("Graph", "DiGraph", "MultiGraph", "MultiDiGraph"), (10, 100)]
    param_names = ["graph_type", "n"]

    def setup(self, graph_type, n):
        self.create_using = getattr(nx, graph_type)
        self.G = nx.complete_graph(n, create_using=self.create_using)
        if self.G.is_multigraph():
            self.G.add_edges_from(self.G.edges)
        self.dol = nx.to_dict_of_lists(self.G)
        self.dod = nx.to_dict_of_dicts(self.G)

    def time_to_dict_of_lists(self, graph_type, n):
        _ = nx.to_dict_of_lists(self.G)

    def time_from_dict_of_lists(self, graph_type, n):
        _ = nx.from_dict_of_lists(self.dol, create_using=self.create_using)

    def time_to_dict_of_dicts(self, graph_type, n):
        for nodelist in [None, self.G.nodes]:
            for edge_data in [None, 1]:
                _ = nx.to_dict_of_dicts(self.G, nodelist=nodelist, edge_data=edge_data)

    def time_from_dict_of_dicts(self, graph_type, n):
        for multigraph_input in [True, False]:
            _ = nx.from_dict_of_dicts(
                self.dod,
                create_using=self.create_using,
                multigraph_input=multigraph_input,
            )
