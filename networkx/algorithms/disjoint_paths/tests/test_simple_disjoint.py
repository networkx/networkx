from nose.tools import assert_equal, assert_true, assert_false, assert_raises

import networkx as nx
        
class TestSimpleDisjoint:
    def setup(self):
        """Creates some graphs for use in the unit tests."""
        self.G = nx.Graph()
        self.G.add_weighted_edges_from([('A', 'B', 1), ('A', 'D', 1.5),
                                        ('A', 'F', 3), ('A', 'G', 7),
                                        ('B', 'C', 1), ('B', 'D', 1),
                                        ('B', 'G', 1), ('C', 'D', 1),
                                        ('C', 'E', 1), ('C', 'Z', 1),
                                        ('D', 'E', 3), ('D', 'F', 1),
                                        ('E', 'F', 2), ('E', 'Z', 1),
                                        ('F', 'Z', 9), ('G', 'Z', 4)])
                                        
        self.Gneg = nx.DiGraph(self.G)
        self.Gneg['B']['C']['weight'] = -1
        del self.Gneg['C']['B']
        
    def test_unweighted(self):
        dists, paths = nx.simple_disjoint(self.G, 'A', 'Z')
        assert_equal(sorted(dists), [2, 2])
        assert_equal(sorted(paths), [['A', 'F', 'Z'], ['A', 'G', 'Z']])
    
    def test_weighted(self):
        dists, paths = nx.simple_disjoint(self.G, 'A', 'Z', weight="weight")
        assert_equal(sorted(dists), [3, 4.5])
        assert_equal(sorted(paths), [['A', 'B', 'C', 'Z'], ['A', 'D', 'C', 'E', 'Z']])
        
    def test_negative_weight(self):
        dists, paths = nx.simple_disjoint(self.Gneg, 'A', 'Z', weight="weight")
        assert_equal(sorted(dists), [1, 4.5])
        assert_equal(sorted(paths), [['A', 'B', 'C', 'Z'], ['A', 'D', 'C', 'E', 'Z']])
        
    def test_k_toohigh(self):
        assert_raises(nx.NetworkXNoPath, nx.simple_disjoint, self.G, 'A', 'Z', weight="weight", k=4)
        
    def test_nodedisjoint(self):
        dists, paths = nx.simple_disjoint(self.G, 'A', 'Z', weight="weight", node_disjoint=True)
        assert_equal(sorted(dists), [3, 5.5])
        assert_equal(sorted(paths), [['A', 'B', 'C', 'Z'], ['A', 'D', 'E', 'Z']])
