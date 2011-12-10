#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from itertools import combinations
from networkx import k_clique_communities

def test_overlaping_K5():
    G = nx.Graph()
    G.add_edges_from(combinations(range(5), 2)) # Add a five clique
    G.add_edges_from(combinations(range(2,7), 2)) # Add another five clique
    c = list(nx.k_clique_communities(G, 4))
    assert_equal(c,[frozenset([0, 1, 2, 3, 4, 5, 6])])
    c= list(nx.k_clique_communities(G, 5))
    assert_equal(set(c),set([frozenset([0,1,2,3,4]),frozenset([2,3,4,5,6])]))

def test_isolated_K5():
    G = nx.Graph()
    G.add_edges_from(combinations(range(0,5), 2)) # Add a five clique
    G.add_edges_from(combinations(range(5,10), 2)) # Add another five clique
    c= list(nx.k_clique_communities(G, 5))
    assert_equal(set(c),set([frozenset([0,1,2,3,4]),frozenset([5,6,7,8,9])]))

def test_zachary():
    z = nx.karate_club_graph()
    # clique percolation with k=2 is just connected components
    zachary_k2_ground_truth = set([frozenset(z.nodes())])
    zachary_k3_ground_truth = set([frozenset([0, 1, 2, 3, 7, 8, 12, 13, 14, 
                                              15, 17, 18, 19, 20, 21, 22, 23, 
                                              26, 27, 28, 29, 30, 31, 32, 33]),
                                   frozenset([0, 4, 5, 6, 10, 16]),
                                   frozenset([24, 25, 31])])
    zachary_k4_ground_truth = set([frozenset([0, 1, 2, 3, 7, 13]),
                                   frozenset([8, 32, 30, 33]),
                                   frozenset([32, 33, 29, 23])])
    zachary_k5_ground_truth = set([frozenset([0, 1, 2, 3, 7, 13])])
    zachary_k6_ground_truth = set([])

    assert set(k_clique_communities(z, 2)) == zachary_k2_ground_truth
    assert set(k_clique_communities(z, 3)) == zachary_k3_ground_truth
    assert set(k_clique_communities(z, 4)) == zachary_k4_ground_truth
    assert set(k_clique_communities(z, 5)) == zachary_k5_ground_truth
    assert set(k_clique_communities(z, 6)) == zachary_k6_ground_truth

@raises(nx.NetworkXError)
def test_bad_k():
    c = list(k_clique_communities(nx.Graph(),1))
