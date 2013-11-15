#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import networkx.algorithms.approximation as apxa
import networkx.algorithms.approximation.densest_k as densk


class TestDenseK:

    def setUp(self):
        # wikiG is the
        # [graph](http://en.wikipedia.org/wiki/File:Dense_subgraph.png) I found
        # in [wikipedia](http://en.wikipedia.org/wiki/Dense_subgraph).
        # Converting its alphabetic nodes into integers, a --> 1, b --> 2, etc.
        # This is supposed to be a ground truth for k = 5.
        self.wikiG = nx.Graph()
        self.wikiG.add_edges_from([(1, 2), (2, 3), (2, 8), (3, 4), (3, 5),
                                  (3, 8), (4, 5), (4, 8), (5, 6), (6, 7),
                                  (7, 8)])
        self.wikiG_ground_truth = [2, 3, 4, 5, 8]
        self.wiki_k = len(self.wikiG_ground_truth)

        self.wheelG = nx.wheel_graph(100)
        self.wheel_k = 5
        self.wheel_ground_truth = range(self.wheel_k)

    def test_find_densest_ground_truth(self):
        # brute-force
        densest_k = apxa.densest_k_nodes_brute_force(
            self.wikiG, self.wiki_k)
        assert_equal(sorted(densest_k), sorted(self.wikiG_ground_truth))

    def test_find_densest(self):
        # approximated

        # As proven in the paper [1], algorithm_A has the approximation
        # ratio of O(n^\frac{-1}{3}).
        bound_A = average_degree(self.wikiG, self.wikiG_ground_truth)
        bound_A /= 2*(len(self.wikiG)**(1./3))
        densest_k = apxa.densest_k_nodes(
            self.wikiG, self.wiki_k)
        assert_greater_equal(average_degree(self.wikiG, densest_k), bound_A)

        densest_k = apxa.densest_k_nodes(self.wheelG, self.wheel_k)
        assert_equal(average_degree(self.wheelG, densest_k),
                     average_degree(self.wheelG, self.wheel_ground_truth))

    def test_find_densest_subgraph(self):
        # approximated

        # As proven in the paper [1], algorithm_A has the approximation
        # ratio of O(n^\frac{-1}{3}).
        bound_A = average_degree(self.wikiG, self.wikiG_ground_truth)
        bound_A /= 2*(len(self.wikiG)**(1./3))
        sub_G = apxa.densest_k_subgraph(
            self.wikiG, self.wiki_k)
        assert_greater_equal(average_degree(self.wikiG, sub_G.nodes()),
                             bound_A)

    def test_find_densest_trival(self):
        # approximated

        # As proven in the paper [1], This algorithm guarantee result density
        # >= 1.

        trivial = eval('__trivial', densk.__dict__)
        densest_k = trivial(self.wikiG, self.wiki_k)
        assert_greater_equal(average_degree(self.wikiG, densest_k), 1.)

    def test_find_densest_greedy(self):
        # approximated

        # As proven in the paper [1], This algorithm guarantee result density
        # >= k*d_H / (2*n), where d_H denote average degree of k/2 vertices
        # with highest degrees in G.
        nodes_by_degree = sorted(
            self.wikiG.nodes(), key=lambda x: self.wikiG.degree(x),
            reverse=True)
        H = nodes_by_degree[:self.wiki_k/2]
        bound = float(sum(self.wikiG.degree(__) for __ in H)) / len(H)
        bound *= self.wiki_k
        bound /= 2*len(self.wikiG)

        greedy = eval('__greedy', densk.__dict__)
        densest_k = greedy(self.wikiG, self.wiki_k)
        densest_k = greedy(self.wikiG, self.wiki_k)
        assert_greater_equal(average_degree(self.wikiG, densest_k), bound)

    def test_find_densest_walks2(self):
        # approximated

        # As proven in the paper [1], This algorithm guarantee result density
        # >= (d*)^2 / (2*max(k, 2*\deltaG)), where d* denote average degree of
        # the optimum solution, and \deltaG is the highest degree of vertices
        # in G.
        deltaG = max(__[1] for __ in self.wikiG.degree_iter())
        bound = average_degree(self.wikiG, self.wikiG_ground_truth)
        bound **= 2
        bound /= 2*max(deltaG, self.wiki_k)

        walks2 = eval('__walks2', densk.__dict__)
        densest_k = walks2(self.wikiG, self.wiki_k)
        densest_k = walks2(self.wikiG, self.wiki_k)
        assert_greater_equal(average_degree(self.wikiG, densest_k), bound)

    @raises(nx.NetworkXNotImplemented)
    def test_find_densest_not_implemented(self):
        apxa.densest_k_nodes(nx.DiGraph(), 1)

    def test_find_densest_smoke(self):
        # smoke test
        G = nx.Graph()
        assert_equal(len(apxa.densest_k_nodes(G, 8)), 0)

        G.add_node(1)
        G.add_node(2)
        assert_equal(len(apxa.densest_k_nodes(G, len(G))), len(G))


def average_degree(G, nodes):
    if nodes:
        return (2.*sum(1 for __ in G.edges_iter(nodes) if __[1] in nodes)
                / len(nodes))
    else:
        return 0
