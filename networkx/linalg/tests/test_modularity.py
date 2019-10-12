import pytest
numpy = pytest.importorskip('numpy')
npt = pytest.importorskip('numpy.testing')
scipy = pytest.importorskip('scipy')

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph


class TestModularity(object):

    @classmethod
    def setup_class(cls):
        deg = [3, 2, 2, 1, 0]
        cls.G = havel_hakimi_graph(deg)
        # Graph used as an example in Sec. 4.1 of Langville and Meyer,
        # "Google's PageRank and Beyond". (Used for test_directed_laplacian)
        cls.DG = nx.DiGraph()
        cls.DG.add_edges_from(((1, 2), (1, 3), (3, 1), (3, 2), (3, 5), (4, 5), (4, 6),
                               (5, 4), (5, 6), (6, 4)))

    def test_modularity(self):
        "Modularity matrix"
        B = numpy.matrix([[-1.125,  0.25,  0.25,  0.625,  0.],
                          [0.25, -0.5,  0.5, -0.25,  0.],
                          [0.25,  0.5, -0.5, -0.25,  0.],
                          [0.625, -0.25, -0.25, -0.125,  0.],
                          [0.,  0.,  0.,  0.,  0.]])

        permutation = [4, 0, 1, 2, 3]
        npt.assert_equal(nx.modularity_matrix(self.G), B)
        npt.assert_equal(nx.modularity_matrix(self.G, nodelist=permutation),
                     B[numpy.ix_(permutation, permutation)])

    def test_modularity_weight(self):
        "Modularity matrix with weights"
        B = numpy.matrix([[-1.125,  0.25,  0.25,  0.625,  0.],
                          [0.25, -0.5,  0.5, -0.25,  0.],
                          [0.25,  0.5, -0.5, -0.25,  0.],
                          [0.625, -0.25, -0.25, -0.125,  0.],
                          [0.,  0.,  0.,  0.,  0.]])

        G_weighted = self.G.copy()
        for n1, n2 in G_weighted.edges():
            G_weighted.edges[n1, n2]["weight"] = 0.5
        # The following test would fail in networkx 1.1
        npt.assert_equal(nx.modularity_matrix(G_weighted), B)
        # The following test that the modularity matrix get rescaled accordingly
        npt.assert_equal(nx.modularity_matrix(G_weighted, weight="weight"), 0.5 * B)

    def test_directed_modularity(self):
        "Directed Modularity matrix"
        B = numpy.matrix([[-0.2,  0.6,  0.8, -0.4, -0.4, -0.4],
                          [0.,  0.,  0.,  0.,  0.,  0.],
                          [0.7,  0.4, -0.3, -0.6,  0.4, -0.6],
                          [-0.2, -0.4, -0.2, -0.4,  0.6,  0.6],
                          [-0.2, -0.4, -0.2,  0.6, -0.4,  0.6],
                          [-0.1, -0.2, -0.1,  0.8, -0.2, -0.2]])
        node_permutation = [5, 1, 2, 3, 4, 6]
        idx_permutation = [4, 0, 1, 2, 3, 5]
        mm = nx.directed_modularity_matrix(self.DG,  nodelist=sorted(self.DG))
        npt.assert_equal(mm, B)
        npt.assert_equal(nx.directed_modularity_matrix(self.DG,
                                                   nodelist=node_permutation),
                     B[numpy.ix_(idx_permutation, idx_permutation)])
