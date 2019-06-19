"""
Tests for incremental closeness centrality.
"""
from nose.tools import *
import networkx as nx
from random import sample

import timeit


class TestIncrementalClosenessCentrality:
    def setUp(self):
        # Create random undirected, unweighted graph
        num_nodes = 100
        edge_prob = 0.6
        self.G = nx.fast_gnp_random_graph(num_nodes, edge_prob)
        self.G_cc = nx.closeness_centrality(self.G)

    @staticmethod
    def pick_add_edge(g):
        u = sample(g.nodes(), 1)[0]
        possible_nodes = set(g.nodes())
        neighbors = list(g.neighbors(u)) + [u]
        possible_nodes.difference_update(neighbors)
        v = sample(possible_nodes, 1)[0]
        return (u, v)

    @staticmethod
    def pick_remove_edge(g):
        u = sample(g.nodes(), 1)[0]
        possible_nodes = list(g.neighbors(u))
        v = sample(possible_nodes, 1)[0]
        return (u, v)

    @raises(nx.NetworkXNotImplemented)
    def test_directed_raises(self):
        dir_G = nx.gn_graph(n=5)
        prev_cc = None
        edge = self.pick_add_edge(dir_G)
        insert = True
        nx.incremental_closeness_centrality(dir_G, edge, prev_cc, insert)

    @raises(nx.NetworkXError)
    def test_wrong_size_prev_cc_raises(self):
        G = self.G.copy()
        edge = self.pick_add_edge(G)
        insert = True
        prev_cc = self.G_cc.copy()
        prev_cc.pop(0)
        nx.incremental_closeness_centrality(G, edge, prev_cc, insert)

    @raises(nx.NetworkXError)
    def test_wrong_nodes_prev_cc_raises(self):
        G = self.G.copy()
        edge = self.pick_add_edge(G)
        insert = True
        prev_cc = self.G_cc.copy()
        num_nodes = len(prev_cc)
        prev_cc.pop(0)
        prev_cc[num_nodes] = 0.5
        nx.incremental_closeness_centrality(G, edge, prev_cc, insert)

    def test_zero_centrality(self):
        G = nx.path_graph(3)
        prev_cc = nx.closeness_centrality(G)
        edge = self.pick_remove_edge(G)
        test_cc = nx.incremental_closeness_centrality(
            G, edge, prev_cc, insertion=False)
        G.remove_edges_from([edge])
        real_cc = nx.closeness_centrality(G)
        shared_items = set(test_cc.items()) & set(real_cc.items())
        assert (len(shared_items) == len(real_cc))
        assert 0 in test_cc.values()

    def test_incremental(self):
        # Check that incremental and regular give same output
        G = self.G.copy()
        prev_cc = None
        for i in range(5):
            if i % 2 == 0:
                # Remove an edge
                insert = False
                edge = self.pick_remove_edge(G)
            else:
                # Add an edge
                insert = True
                edge = self.pick_add_edge(G)

            start = timeit.default_timer()
            test_cc = nx.incremental_closeness_centrality(
                G, edge, prev_cc, insert)
            inc_elapsed = (timeit.default_timer() - start)
            print("incremental time: {}".format(inc_elapsed))

            if insert:
                G.add_edges_from([edge])
            else:
                G.remove_edges_from([edge])

            start = timeit.default_timer()
            real_cc = nx.closeness_centrality(G)
            reg_elapsed = (timeit.default_timer() - start)

            print("regular time: {}".format(reg_elapsed))

            shared_items = set(test_cc.items()) & set(real_cc.items())
            assert (len(shared_items) == len(real_cc))

            prev_cc = real_cc
