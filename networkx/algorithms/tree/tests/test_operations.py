"""Unit tests for the :mod:`networkx.algorithms.tree.operations` module.

"""

from itertools import chain

import networkx as nx
from networkx.utils import edges_equal, nodes_equal


def _check_label_attribute(input_trees, res_tree, label_attribute="_old"):
    res_attr_dict = nx.get_node_attributes(res_tree, label_attribute)
    res_attr_set = set(res_attr_dict.values())
    input_label = (list(tree[0].nodes()) for tree in input_trees)
    input_label_set = set(chain.from_iterable(input_label))
    return res_attr_set == input_label_set


class TestJoin:
    """Unit tests for the :func:`networkx.tree.join` function."""

    def test_empty_sequence(self):
        """Tests that joining the empty sequence results in the tree
        with one node.

        """
        T = nx.join([])
        assert len(T) == 1
        assert T.number_of_edges() == 0

    def test_single(self):
        """Tests that joining just one tree yields a tree with one more
        node.

        """
        T = nx.empty_graph(1)
        trees = [(T, 0)]
        actual = nx.join(trees)
        expected = nx.path_graph(2)
        assert nodes_equal(list(expected), list(actual))
        assert edges_equal(list(expected.edges()), list(actual.edges()))
        assert _check_label_attribute(trees, actual)

    def test_basic(self):
        """Tests for joining multiple subtrees at a root node."""
        trees = [(nx.full_rary_tree(2, 2**2 - 1), 0) for i in range(2)]
        label_attribute = "old_values"
        actual = nx.join(trees, label_attribute)
        expected = nx.full_rary_tree(2, 2**3 - 1)
        assert nx.is_isomorphic(actual, expected)
        assert _check_label_attribute(trees, actual, label_attribute)
