#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from itertools import combinations

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
