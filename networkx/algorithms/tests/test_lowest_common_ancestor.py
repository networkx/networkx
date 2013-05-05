#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import itertools

class TestLCA:

  def setUp(self):
    self.DG = nx.DiGraph()
    self.DG.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    self.ans = dict(nx.tree_all_pairs_lowest_common_ancestor(self.DG, 0))

  def test_tree_all_pairs_lowest_common_ancestor1(self):
    """Specifying the root is optional."""
    assert_equal(self.ans, dict(nx.tree_all_pairs_lowest_common_ancestor(self.DG)))

  def test_tree_all_pairs_lowest_common_ancestor2(self):
    """Specifying only some pairs gives only those pairs."""
    some_pairs = dict(nx.tree_all_pairs_lowest_common_ancestor(self.DG, 0, [(0, 1), (0, 1), (1, 0)]))
    assert_true((0, 1) in some_pairs or (1, 0) in some_pairs)
    assert_equal(len(some_pairs), 1)

  def test_tree_all_pairs_lowest_common_ancestor3(self):
    """Specifying no pairs same as specifying all."""
    all_pairs = itertools.chain(itertools.combinations(self.DG.nodes(), 2),
                                ((node, node) for node in self.DG.nodes_iter()))
    for (a, b), lca in nx.tree_all_pairs_lowest_common_ancestor(self.DG, 0,
                                                                all_pairs):
      if (a, b) in self.ans:
        assert_equal(self.ans[a, b], lca)
      else:
        assert_equal(self.ans[b, a], lca)

  def test_tree_all_pairs_lowest_common_ancestor4(self):
    """Gives the right answer."""
    gold = dict([((n, n), n) for n in self.DG])
    gold.update(dict(((0, i), 0) for i in range(1, 7)))
    gold.update({(1, 2): 0,
                 (1, 3): 1,
                 (1, 4): 1,
                 (1, 5): 0,
                 (1, 6): 0,
                 (2, 3): 0,
                 (2, 4): 0,
                 (2, 5): 2,
                 (2, 6): 2,
                 (3, 4): 1,
                 (3, 5): 0,
                 (3, 6): 0,
                 (4, 5): 0,
                 (4, 6): 0,
                 (5, 6): 2})
    for (a, b) in gold.iterkeys():
      if (a, b) in self.ans:
        assert_equal(self.ans[a, b], gold[a, b])
      else:
        assert_equal(self.ans[b, a], gold[a, b])
