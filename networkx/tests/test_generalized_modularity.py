#!/usr/bin/env python
from nose.tools import *
from networkx import *
from networkx.convert import *
from networkx.algorithms.operators import *
from networkx.generators.classic import barbell_graph, cycle_graph
from networkx.testing import *
from networkx.algorithms.community import modularity, greedy_modularity_communities

class TestGeneralizedModularity():
    def test_modularity(self):
        # test that empty graph converts fine for all options
        G = barbell_graph(3, 0)
        m = modularity(G, [{0, 1, 2}, {3, 4, 5}])

        G = karate_club_graph()
        c = list(greedy_modularity_communities(G, gamma=1.8))
        print(sorted(c[0]))

