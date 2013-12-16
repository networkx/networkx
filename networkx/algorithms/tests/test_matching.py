#!/usr/bin/env python
import math
from nose.tools import *
import networkx as nx

class TestMatching:

    def setUp(self):
        pass

    def test_trivial1(self):
        """Empty graph"""
        G = nx.Graph()
        assert_equal(nx.max_weight_matching(G),{})

    def test_trivial2(self):
        """Self loop"""
        G = nx.Graph()
        G.add_edge(0, 0, weight=100)
        assert_equal(nx.max_weight_matching(G),{})

    def test_trivial3(self):
        """Single edge"""
        G = nx.Graph()
        G.add_edge(0, 1)
        assert_equal(nx.max_weight_matching(G),
                     {0: 1, 1: 0})

    def test_trivial4(self):
        """Small graph"""
        G = nx.Graph()
        G.add_edge('one', 'two', weight=10)
        G.add_edge('two', 'three', weight=11)
        assert_equal(nx.max_weight_matching(G),
                     {'three': 'two', 'two': 'three'})

    def test_trivial5(self):
        """Path"""
        G = nx.Graph()
        G.add_edge(1, 2, weight=5)
        G.add_edge(2, 3, weight=11)
        G.add_edge(3, 4, weight=5)
        assert_equal(nx.max_weight_matching(G),
                     {2: 3, 3: 2})
        assert_equal(nx.max_weight_matching(G, 1),
                     {1: 2, 2: 1, 3: 4, 4: 3})


    def test_floating_point_weights(self):
        """Floating point weights"""
        G = nx.Graph()
        G.add_edge(1, 2, weight=math.pi)
        G.add_edge(2, 3, weight=math.exp(1))
        G.add_edge(1, 3, weight=3.0)
        G.add_edge(1, 4, weight=math.sqrt(2.0))
        assert_equal(nx.max_weight_matching(G),
                     {1: 4, 2: 3, 3: 2, 4: 1})

    def test_negative_weights(self):
        """Negative weights"""
        G = nx.Graph()
        G.add_edge(1, 2, weight=2)
        G.add_edge(1, 3, weight=-2)
        G.add_edge(2, 3, weight=1)
        G.add_edge(2, 4, weight=-1)
        G.add_edge(3, 4, weight=-6)
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1})
        assert_equal(nx.max_weight_matching(G, 1),
                     {1: 3, 2: 4, 3: 1, 4: 2})

    def test_s_blossom(self):
        """Create S-blossom and use it for augmentation:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 8), (1, 3, 9), 
                                    (2, 3, 10), (3, 4, 7) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1, 3: 4, 4: 3})

        G.add_weighted_edges_from([ (1, 6, 5), (4, 5, 6) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 5, 5: 4, 6: 1})

    def test_s_t_blossom(self):
        """Create S-blossom, relabel as T-blossom, use for augmentation:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 9), (1, 3, 8), (2, 3, 10), 
                                    (1, 4, 5), (4, 5, 4), (1, 6, 3) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 5, 5: 4, 6: 1})
        G.add_edge(4, 5, weight=3)
        G.add_edge(1, 6, weight=4)
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 5, 5: 4, 6: 1})
        G.remove_edge(1, 6)
        G.add_edge(3, 6, weight=4)
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1, 3: 6, 4: 5, 5: 4, 6: 3})

    def test_nested_s_blossom(self):
        """Create nested S-blossom, use for augmentation:"""

        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 9), (1, 3, 9), (2, 3, 10), 
                                    (2, 4, 8), (3, 5, 8), (4, 5, 10), 
                                    (5, 6, 6) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 3, 2: 4, 3: 1, 4: 2, 5: 6, 6: 5})

    def test_nested_s_blossom_relabel(self):
        """Create S-blossom, relabel as S, include in nested S-blossom:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 10), (1, 7, 10), (2, 3, 12), 
                                    (3, 4, 20), (3, 5, 20), (4, 5, 25), 
                                    (5, 6, 10), (6, 7, 10), (7, 8, 8) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5, 7: 8, 8: 7})

    def test_nested_s_blossom_expand(self):
        """Create nested S-blossom, augment, expand recursively:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 8), (1, 3, 8), (2, 3, 10), 
                                    (2, 4, 12),(3, 5, 12), (4, 5, 14), 
                                    (4, 6, 12), (5, 7, 12), (6, 7, 14), 
                                    (7, 8, 12) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1, 3: 5, 4: 6, 5: 3, 6: 4, 7: 8, 8: 7})


    def test_s_blossom_relabel_expand(self):
        """Create S-blossom, relabel as T, expand:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 23), (1, 5, 22), (1, 6, 15), 
                                    (2, 3, 25), (3, 4, 22), (4, 5, 25), 
                                    (4, 8, 14), (5, 7, 13) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 6: 1, 7: 5, 8: 4})

    def test_nested_s_blossom_relabel_expand(self):
        """Create nested S-blossom, relabel as T, expand:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 19), (1, 3, 20), (1, 8, 8), 
                                    (2, 3, 25), (2, 4, 18), (3, 5, 18), 
                                    (4, 5, 13), (4, 7, 7), (5, 6, 7) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 8, 2: 3, 3: 2, 4: 7, 5: 6, 6: 5, 7: 4, 8: 1})


    def test_nasty_blossom1(self):
        """Create blossom, relabel as T in more than one way, expand, 
        augment:
        """
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 45), (1, 5, 45), (2, 3, 50), 
                                    (3, 4, 45), (4, 5, 50), (1, 6, 30), 
                                    (3, 9, 35), (4, 8, 35), (5, 7, 26), 
                                    (9, 10, 5) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 8, 5: 7,
                      6: 1, 7: 5, 8: 4, 9: 10, 10: 9})

    def test_nasty_blossom2(self):
        """Again but slightly different:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 45), (1, 5, 45), (2, 3, 50), 
                                    (3, 4, 45), (4, 5, 50), (1, 6, 30), 
                                    (3, 9, 35), (4, 8, 26), (5, 7, 40), 
                                    (9, 10, 5) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 
                      6: 1, 7: 5, 8: 4, 9: 10, 10: 9})

    def test_nasty_blossom_least_slack(self):
        """Create blossom, relabel as T, expand such that a new 
        least-slack S-to-free dge is produced, augment:
        """
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 45), (1, 5, 45), (2, 3, 50), 
                                    (3, 4, 45), (4, 5, 50), (1, 6, 30), 
                                    (3, 9, 35), (4, 8, 28), (5, 7, 26), 
                                    (9, 10, 5) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 6, 2: 3, 3: 2, 4: 8, 5: 7, 
                      6: 1, 7: 5, 8: 4, 9: 10, 10: 9})

    def test_nasty_blossom_augmenting(self):
        """Create nested blossom, relabel as T in more than one way""" 
        # expand outer blossom such that inner blossom ends up on an 
        # augmenting path:
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 45), (1, 7, 45), (2, 3, 50), 
                                    (3, 4, 45), (4, 5, 95), (4, 6, 94), 
                                    (5, 6, 94), (6, 7, 50), (1, 8, 30), 
                                    (3, 11, 35), (5, 9, 36), (7, 10, 26),
                                    (11, 12, 5) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 8, 2: 3, 3: 2, 4: 6, 5: 9, 6: 4, 
                      7: 10, 8: 1, 9: 5, 10: 7, 11: 12, 12: 11})

    def test_nasty_blossom_expand_recursively(self):
        """Create nested S-blossom, relabel as S, expand recursively:"""
        G = nx.Graph()
        G.add_weighted_edges_from([ (1, 2, 40), (1, 3, 40), (2, 3, 60), 
                                    (2, 4, 55), (3, 5, 55), (4, 5, 50), 
                                    (1, 8, 15), (5, 7, 30), (7, 6, 10), 
                                    (8, 10, 10), (4, 9, 30) ])
        assert_equal(nx.max_weight_matching(G),
                     {1: 2, 2: 1, 3: 5, 4: 9, 5: 3, 
                      6: 7, 7: 6, 8: 10, 9: 4, 10: 8})

def test_maximal_matching():
    graph = nx.Graph()
    graph.add_edge(0, 1)
    graph.add_edge(0, 2)
    graph.add_edge(0, 3)
    graph.add_edge(0, 4)
    graph.add_edge(0, 5)
    graph.add_edge(1, 2)
    matching = nx.maximal_matching(graph)

    vset = set(u for u, v in matching)
    vset = vset | set(v for u, v in matching)

    for edge in graph.edges_iter():
        u, v = edge
        ok_(len(set([v]) & vset) > 0 or len(set([u]) & vset) > 0, \
                "not a proper matching!")

    eq_(1, len(matching), "matching not length 1!")
    graph = nx.Graph()
    graph.add_edge(1, 2)
    graph.add_edge(1, 5)
    graph.add_edge(2, 3)
    graph.add_edge(2, 5)
    graph.add_edge(3, 4)
    graph.add_edge(3, 6)
    graph.add_edge(5, 6)

    matching = nx.maximal_matching(graph)
    vset = set(u for u, v in matching)
    vset = vset | set(v for u, v in matching)

    for edge in graph.edges_iter():
        u, v = edge
        ok_(len(set([v]) & vset) > 0 or len(set([u]) & vset) > 0, \
                "not a proper matching!")

def test_maximal_matching_ordering():
    # check edge ordering
    G = nx.Graph()
    G.add_nodes_from([100,200,300])
    G.add_edges_from([(100,200),(100,300)])
    matching = nx.maximal_matching(G)
    assert_equal(len(matching), 1)
    G = nx.Graph()
    G.add_nodes_from([200,100,300])
    G.add_edges_from([(100,200),(100,300)])
    matching = nx.maximal_matching(G)
    assert_equal(len(matching), 1)
    G = nx.Graph()
    G.add_nodes_from([300,200,100])
    G.add_edges_from([(100,200),(100,300)])
    matching = nx.maximal_matching(G)
    assert_equal(len(matching), 1)
