"""
Unit tests for the :mod:
`networkx.algorithms.community.dendrogram_from_girvan_newman` module.
"""

import networkx as nx
import networkx.algorithms.community.dendrogram_from_girvan_newman as dgn
import pytest

np = pytest.importorskip("numpy")


class TestDendrogram:
    def test_girvan_newman_partition(self):
        G = nx.path_graph(4)
        partitions = dgn.girvan_newman_partitions(G)
        test_part = [[{0, 1}, {2, 3}], [{0}, {1}, {2, 3}], [{0}, {1}, {2}, {3}]]
        assert partitions == test_part

    def test_agglomerative_matrix(self):
        G = nx.path_graph(4)
        partitions = dgn.girvan_newman_partitions(G)
        agglomerative_mat = dgn.agglomerative_matrix(G, partitions)
        test_mat = np.array(
            [[2.0, 3.0, 1.0, 2.0], [0.0, 1.0, 1.0, 2.0], [4.0, 5.0, 2.0, 4.0]]
        )
        np.testing.assert_array_equal(agglomerative_mat, test_mat)

    def test_girvan_newman_best_partition(self):
        G = nx.path_graph(6)
        partitions = dgn.girvan_newman_partitions(G)
        bp_G, index_bp_G = dgn.girvan_newman_best_partition(G, partitions)
        assert bp_G == [{0, 1, 2}, {3, 4, 5}]
        assert index_bp_G == 0

    def test_distance_of_partition(self):
        G = nx.path_graph(6)
        partitions = dgn.girvan_newman_partitions(G)
        agglomerative_mat = dgn.agglomerative_matrix(G, partitions)
        n_communities = 2
        dist_2comm = dgn.distance_of_partition(agglomerative_mat, n_communities)
        assert dist_2comm == 3

    def test_wrong_node_indices(self):
        with pytest.raises(TypeError):
            # graph with 4 nodes, from 1 to 4
            nodes = [1, 2, 3, 4]
            edges = [(1, 2), (1, 3), (2, 4), (3, 4)]
            G = nx.Graph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)

            # try to compute partitions
            partitions = dgn.girvan_newman_partitions(G)

    def test_not_connected_graph(self):
        with pytest.raises(TypeError):
            # graph with 4 nodes and not connected
            nodes = [0, 1, 2, 3]
            edges = [(0, 1), (0, 2), (1, 2)]
            G = nx.Graph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)

            # try to compute partitions
            partitions = dgn.girvan_newman_partitions(G)

    def test_bad_number_of_communities(self):
        with pytest.raises(TypeError):
            # graph and agglomerative matrix
            G = nx.path_graph(6)
            partitions = dgn.girvan_newman_partitions(G)
            agglomerative_mat = dgn.agglomerative_matrix(G, partitions)

            # bad number of communities
            bad_n_communities_big = 999
            bad_n_communities_small = 0
            dist_big = dgn.distance_of_partition(
                agglomerative_mat, bad_n_communities_big
            )
            dist_small = dgn.distance_of_partition(
                agglomerative_mat, bad_n_communities_small
            )
