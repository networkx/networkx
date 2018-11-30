#!/usr/bin/env python
from nose.tools import *
from networkx import *
from networkx.convert import *
from networkx.algorithms.operators import *
from networkx.generators.classic import barbell_graph, cycle_graph
from networkx.testing import *
from networkx.algorithms.community import modularity, greedy_modularity_communities, _naive_greedy_modularity_communities

class TestGeneralizedModularity():
    def test_modularity(self):
        # test if the genealized modularity maximization algorithm works fine 
        # by comparing results 
        G = karate_club_graph()
        c1 = list(greedy_modularity_communities(G, 1.8))
        c2 = list(_naive_greedy_modularity_communities(G, 1.8))
        assert_equal(len(c1), len(c2))
        for i in range(len(c1)):
          assert_equal(sorted(c1[i]), sorted(c2[i]))
