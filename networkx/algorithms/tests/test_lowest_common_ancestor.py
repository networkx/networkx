#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import itertools

def get_pair(dictionary, n1, n2):
  if (n1, n2) in dictionary:
    return dictionary[n1, n2]
  else:
    return dictionary[n2, n1]

def has_same_pairs(d1, d2):
  for (a, b) in set(((min(pair), max(pair))
                     for pair in d1.keys() + d2.keys())):
    assert_equal(get_pair(d1, a, b), get_pair(d2, a, b))

class TestTreeLCA:

  def setUp(self):
    self.DG = nx.DiGraph()
    self.DG.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    self.ans = dict(nx.tree_all_pairs_lowest_common_ancestor(self.DG, 0))
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

    self.gold = gold


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

  def test_tree_all_pairs_lowest_common_ancestor5(self):
    """Handles invalid input correctly."""
    empty_digraph = nx.tree_all_pairs_lowest_common_ancestor(nx.DiGraph())
    assert_raises(nx.NetworkXPointlessConcept, list, empty_digraph)

    empty_graph = nx.tree_all_pairs_lowest_common_ancestor(nx.Graph())
    assert_raises(nx.NetworkXNotImplemented, list, empty_graph)

    nonempty_graph = nx.tree_all_pairs_lowest_common_ancestor(self.DG.to_undirected())
    assert_raises(nx.NetworkXNotImplemented, list, nonempty_graph)

    bad_pairs_digraph = nx.tree_all_pairs_lowest_common_ancestor(self.DG,
                                                             pairs=[(-1, -2)])
    assert_raises(nx.NetworkXError, list, bad_pairs_digraph)

  def test_tree_all_pairs_lowest_common_ancestor6(self):
    """Works on subtrees."""
    ans = dict(nx.tree_all_pairs_lowest_common_ancestor(self.DG, 1))
    gold = dict(((pair, lca) for (pair, lca) in self.gold.iteritems()
                 if all((n in (1, 3, 4) for n in pair))))
    has_same_pairs(gold, ans)

  def test_tree_all_pairs_lowest_common_ancestor7(self):
    """Works on disconnected nodes."""
    G = nx.DiGraph()
    G.add_node(1)
    assert_equal({(1, 1): 1}, dict(nx.tree_all_pairs_lowest_common_ancestor(G)))

    G.add_node(0)
    assert_equal({(1, 1): 1}, dict(nx.tree_all_pairs_lowest_common_ancestor(G, 1)))
    assert_equal({(0, 0): 0}, dict(nx.tree_all_pairs_lowest_common_ancestor(G, 0)))
    
    assert_raises(nx.NetworkXError, list,
                  nx.tree_all_pairs_lowest_common_ancestor(G))
