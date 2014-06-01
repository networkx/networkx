import math

from nose.tools import *

import networkx as nx


class TestResourceAllocationIndex():
    def setUp(self):
        self.func = nx.resource_allocation_index

        def test_func(G, ebunch, expected):
            result = self.func(G, ebunch)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_almost_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, [(0, 1)], [(0, 1, 0.75)])

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, [(0, 2)], [(0, 2, 0.5)])

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, [(1, 2)], [(1, 2, 0.25)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_equal_nodes(self):
        G = nx.complete_graph(4)
        self.test(G, [(0, 0)], [(0, 0, 1)])

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        self.test(G, None, [(0, 3, 0.5), (1, 2, 0.5), (1, 3, 0)])


class TestJaccardCoefficient():
    def setUp(self):
        self.func = nx.jaccard_coefficient

        def test_func(G, ebunch, expected):
            result = self.func(G, ebunch)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_almost_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, [(0, 1)], [(0, 1, 0.6)])

    def test_P4(self):
        G = nx.path_graph(4)
        self.test(G, [(0, 2)], [(0, 2, 0.5)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (2, 3)])
        self.test(G, [(0, 2)], [(0, 2, 0)])

    def test_isolated_nodes(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        self.test(G, None, [(0, 3, 0.5), (1, 2, 0.5), (1, 3, 0)])


class TestAdamicAdarIndex():
    def setUp(self):
        self.func = nx.adamic_adar_index

        def test_func(G, ebunch, expected):
            result = self.func(G, ebunch)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_almost_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, [(0, 1)], [(0, 1, 3 / math.log(4))])

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, [(0, 2)], [(0, 2, 1 / math.log(2))])

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, [(1, 2)], [(1, 2, 1 / math.log(4))])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_equal_nodes(self):
        G = nx.complete_graph(4)
        self.test(G, [(0, 0)], [(0, 0, 3 / math.log(3))])

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        self.test(G, None, [(0, 3, 1 / math.log(2)), (1, 2, 1 / math.log(2)),
                  (1, 3, 0)])


class TestPreferentialAttachment():
    def setUp(self):
        self.func = nx.preferential_attachment

        def test_func(G, ebunch, expected):
            result = self.func(G, ebunch)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, [(0, 1)], [(0, 1, 16)])

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, [(0, 1)], [(0, 1, 2)])

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, [(0, 2)], [(0, 2, 4)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, [(0, 2)])

    def test_zero_degrees(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        self.test(G, None, [(0, 3, 2), (1, 2, 2), (1, 3, 1)])


class TestCNSoundarajanHopcroft():
    def setUp(self):
        self.func = nx.cn_soundarajan_hopcroft

        def test_func(G, ebunch, expected, community='community'):
            result = self.func(G, ebunch, community)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, [(0, 1)], [(0, 1, 5)])

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, [(0, 2)], [(0, 2, 1)])

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 2)], [(1, 2, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_equal_nodes(self):
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, [(0, 0)], [(0, 0, 4)])

    def test_different_community(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, [(0, 3)], [(0, 3, 2)])

    @raises(nx.NetworkXAlgorithmError)
    def test_no_community_information(self):
        G = nx.complete_graph(5)
        list(self.func(G, [(0, 1)]))

    @raises(nx.NetworkXAlgorithmError)
    def test_insufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        list(self.func(G, [(0, 3)]))

    def test_sufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 4)], [(1, 4, 4)])

    def test_custom_community_attribute_name(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['cmty'] = 0
        G.node[1]['cmty'] = 0
        G.node[2]['cmty'] = 0
        G.node[3]['cmty'] = 1
        self.test(G, [(0, 3)], [(0, 3, 2)], community='cmty')

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, None, [(0, 3, 2), (1, 2, 1), (1, 3, 0)])


class TestRAIndexSoundarajanHopcroft():
    def setUp(self):
        self.func = nx.ra_index_soundarajan_hopcroft

        def test_func(G, ebunch, expected, community='community'):
            result = self.func(G, ebunch, community)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_almost_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, [(0, 1)], [(0, 1, 0.5)])

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, [(0, 2)], [(0, 2, 0)])

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 2)], [(1, 2, 0.25)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_equal_nodes(self):
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, [(0, 0)], [(0, 0, 1)])

    def test_different_community(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, [(0, 3)], [(0, 3, 0)])

    @raises(nx.NetworkXAlgorithmError)
    def test_no_community_information(self):
        G = nx.complete_graph(5)
        list(self.func(G, [(0, 1)]))

    @raises(nx.NetworkXAlgorithmError)
    def test_insufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        list(self.func(G, [(0, 3)]))

    def test_sufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 4)], [(1, 4, 1)])

    def test_custom_community_attribute_name(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['cmty'] = 0
        G.node[1]['cmty'] = 0
        G.node[2]['cmty'] = 0
        G.node[3]['cmty'] = 1
        self.test(G, [(0, 3)], [(0, 3, 0)], community='cmty')

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, None, [(0, 3, 0.5), (1, 2, 0), (1, 3, 0)])


class TestWithinInterCluster():
    def setUp(self):
        self.delta = 0.001
        self.func = nx.within_inter_cluster

        def test_func(G, ebunch, expected, delta=self.delta,
                      community='community'):
            result = self.func(G, ebunch, delta, community)
            for res, exp in zip(result, expected):
                assert_true(isinstance(res, tuple))
                assert_equal(3, len(res))
                assert_equal(res[0], exp[0])
                assert_equal(res[1], exp[1])
                assert_almost_equal(res[2], exp[2])
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, [(0, 1)], [(0, 1, 2 / (1 + self.delta))])

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, [(0, 2)], [(0, 2, 0)])

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 2)], [(1, 2, 1 / self.delta)])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, [(0, 2)])

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, [(0, 1)], [(0, 1, 0)])

    def test_equal_nodes(self):
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, [(0, 0)], [(0, 0, 2 / self.delta)])

    def test_different_community(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, [(0, 3)], [(0, 3, 0)])

    def test_no_inter_cluster_common_neighbor(self):
        G = nx.complete_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, [(0, 3)], [(0, 3, 2 / self.delta)])

    @raises(nx.NetworkXAlgorithmError)
    def test_no_community_information(self):
        G = nx.complete_graph(5)
        list(self.func(G, [(0, 1)]))

    @raises(nx.NetworkXAlgorithmError)
    def test_insufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        list(self.func(G, [(0, 3)]))

    def test_sufficient_community_information(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, [(1, 4)], [(1, 4, 2 / self.delta)])

    @raises(nx.NetworkXAlgorithmError)
    def test_zero_delta(self):
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        list(self.func(G, [(0, 1)], 0))

    @raises(nx.NetworkXAlgorithmError)
    def test_negative_delta(self):
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        list(self.func(G, [(0, 1)], -0.5))

    def test_custom_community_attribute_name(self):
        G = nx.complete_graph(4)
        G.node[0]['cmty'] = 0
        G.node[1]['cmty'] = 0
        G.node[2]['cmty'] = 0
        G.node[3]['cmty'] = 0
        self.test(G, [(0, 3)], [(0, 3, 2 / self.delta)], community='cmty')

    def test_all_nonexistent_edges(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, None, [(0, 3, 1 / self.delta), (1, 2, 0), (1, 3, 0)])
