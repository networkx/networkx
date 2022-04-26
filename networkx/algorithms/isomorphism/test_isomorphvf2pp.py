import unittest
import isomorphvf2pp as vf
import networkx as nx


class TestConnectivity(unittest.TestCase):
    def test_connectivity1(self):
        G = nx.path_graph(7)
        H = [1, 2, 3, 4]
        u = 3
        self.assertEqual(vf.connectivity(G, u, H), 2, 'Connectivity error in path graph')

    def test_connectivity2(self):
        G = nx.path_graph(7)
        H = [1, 2, 3, 4]
        u = 4
        self.assertEqual(vf.connectivity(G, u, H), 1, 'Connectivity error in path graph')

    def test_connectivity3(self):
        G = nx.path_graph(7)
        H = [1, 2, 3, 4]
        u = 0
        self.assertEqual(vf.connectivity(G, u, H), 1, 'Connectivity error in path graph')

    def test_connectivity4(self):
        G = nx.path_graph(7)
        H = [1, 2, 3, 4]
        u = 6
        self.assertEqual(vf.connectivity(G, u, H), 0, 'Connectivity error in path graph')

    def test_connectivity5(self):
        G = nx.barbell_graph(15, 8)
        H = [i for i in range(10)]
        u = 5
        self.assertEqual(vf.connectivity(G, u, H), 9, 'Connectivity error in barbell graph')