import networkx as nx


class BaseTestAttributeMixing:
    @classmethod
    def setup_class(cls):
        G = nx.Graph()
        G.add_nodes_from([0, 1], fish="one")
        G.add_nodes_from([2, 3], fish="two")
        G.add_nodes_from([4], fish="red")
        G.add_nodes_from([5], fish="blue")
        G.add_edges_from([(0, 1), (2, 3), (0, 4), (2, 5)])
        cls.G = G

        D = nx.DiGraph()
        D.add_nodes_from([0, 1], fish="one")
        D.add_nodes_from([2, 3], fish="two")
        D.add_nodes_from([4], fish="red")
        D.add_nodes_from([5], fish="blue")
        D.add_edges_from([(0, 1), (2, 3), (0, 4), (2, 5)])
        cls.D = D

        M = nx.MultiGraph()
        M.add_nodes_from([0, 1], fish="one")
        M.add_nodes_from([2, 3], fish="two")
        M.add_nodes_from([4], fish="red")
        M.add_nodes_from([5], fish="blue")
        M.add_edges_from([(0, 1), (0, 1), (2, 3)])
        cls.M = M

        S = nx.Graph()
        S.add_nodes_from([0, 1], fish="one")
        S.add_nodes_from([2, 3], fish="two")
        S.add_nodes_from([4], fish="red")
        S.add_nodes_from([5], fish="blue")
        S.add_edge(0, 0)
        S.add_edge(2, 2)
        cls.S = S


class BaseTestDegreeMixing:
    @classmethod
    def setup_class(cls):
        cls.P4 = nx.path_graph(4)
        cls.D = nx.DiGraph()
        cls.D.add_edges_from([(0, 2), (0, 3), (1, 3), (2, 3)])
        cls.M = nx.MultiGraph()
        nx.add_path(cls.M, range(4))
        cls.M.add_edge(0, 1)
        cls.S = nx.Graph()
        cls.S.add_edges_from([(0, 0), (1, 1)])
