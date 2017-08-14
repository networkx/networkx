
import networkx as nx


class TestEfficiency:

    def __init__(self):
        # G1 is a toy graph
        self.G1 = nx.barbell_graph(10, 3)
        # G2 is a disconnected graph
        self.G2 = nx.Graph()
        self.G2.add_nodes_from([1, 2, 3])

    def test_efficiency(self):
        """
        Returns efficiency of two nodes
        """
        return nx.efficiency(self.G1, 1, 10)

    def test_efficiency_disconnected_nodes(self):
        """
        Returns 0 when nodes are disconnected
        """
        return nx.efficiency(self.G2, 1, 2)

    def test_local_efficiency(self):
        """
        Test local efficiency
        """
        return nx.local_efficiency(self.G1)

    def test_local_efficiency_disconnected_graph(self):
        """
        In a disconnected graph the efficiency is 0
        """
        return nx.local_efficiency(self.G2)

    def test_global_efficiency(self):
        """
        test global efficiency
        """
        return nx.global_efficiency(self.G1)
