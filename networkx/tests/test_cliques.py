#!/usr/bin/env python

"""Cliques
=======
"""

from nose.tools import *
from networkx import *
from networkx.algorithms.clique import get_all_cliques

class TestCliques():
    def test_paper_figure_4(self):
        # Same graph as given in Fig. 4 of paper get_all_cliques is
        # based on.
        # http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1559964&isnumber=33129
        G = Graph()
        edges_fig_4 = [('a','b'),('a','c'),('a','d'),('a','e'),
                       ('b','c'),('b','d'),('b','e'),
                       ('c','d'),('c','e'),
                       ('d','e'),
                       ('f','b'),('f','c'),('f','g'),
                       ('g','f'),('g','c'),('g','d'),('g','e')]
        G.add_edges_from(edges_fig_4)

        cliques = list(get_all_cliques(G))
        expected_cliques = [['a'],
                            ['b'],
                            ['c'],
                            ['d'],
                            ['e'],
                            ['f'],
                            ['g'],
                            ['a', 'b'],
                            ['a', 'b', 'd'],
                            ['a', 'b', 'd', 'e'],
                            ['a', 'b', 'e'],
                            ['a', 'c'],
                            ['a', 'c', 'd'],
                            ['a', 'c', 'd', 'e'],
                            ['a', 'c', 'e'],
                            ['a', 'd'],
                            ['a', 'd', 'e'],
                            ['a', 'e'],
                            ['b', 'c'],
                            ['b', 'c', 'd'],
                            ['b', 'c', 'd', 'e'],
                            ['b', 'c', 'e'],
                            ['b', 'c', 'f'],
                            ['b', 'd'],
                            ['b', 'd', 'e'],
                            ['b', 'e'],
                            ['b', 'f'],
                            ['c', 'd'],
                            ['c', 'd', 'e'],
                            ['c', 'd', 'e', 'g'],
                            ['c', 'd', 'g'],
                            ['c', 'e'],
                            ['c', 'e', 'g'],
                            ['c', 'f'],
                            ['c', 'f', 'g'],
                            ['c', 'g'],
                            ['d', 'e'],
                            ['d', 'e', 'g'],
                            ['d', 'g'],
                            ['e', 'g'],
                            ['f', 'g'],
                            ['a', 'b', 'c', 'd'],
                            ['a', 'b', 'c', 'd', 'e'],
                            ['a', 'b', 'c', 'e']]
        
        assert_equal(cliques, expected_cliques)
