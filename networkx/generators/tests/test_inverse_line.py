import networkx as nx
from nose.tools import *

from networkx.testing.utils import *
# TODO
# JC: What other tests would we like to see here?

class TestGeneratorLine():
    def test_example(self):
        G = nx.Graph()
        G.add_edges_from([[1,2], [1,3], [1,4], [1,5], [2,3], [2,5], [2,6], [2,7],
                      [3,4], [3,5], [6,7], [6,8], [7,8]])
        H = nx.inverse_line_graph(G)
        solution = nx.Graph()
        solution_edges = [('a', 'b'), ('a', 'c'), ('a', 'd'), ('a', 'e'),
                          ('c', 'd'), ('e', 'f'), ('e', 'g'), ('f', 'g')]
        solution.add_edges_from(solution_edges)
        assert_true(nx.is_isomorphic(H, solution))


