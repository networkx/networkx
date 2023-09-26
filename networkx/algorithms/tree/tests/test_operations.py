from itertools import chain

import networkx as nx
from networkx.utils import edges_equal, nodes_equal


def _check_custom_label_attribute(
    input_trees, res_tree, label_attribute="custom_label"
):
    res_attr_dict = nx.get_node_attributes(res_tree, label_attribute)
    res_attr_set = set(res_attr_dict.values())
    input_label = (list(tree[0].nodes()) for tree in input_trees)
    input_label_set = set(chain.from_iterable(input_label))
    return res_attr_set == input_label_set


def _check_no_label_attribute(res_tree):
    return all(not data for _, data in res_tree.nodes(data=True))


def test_empty_sequence():
    """Joining the empty sequence results in the tree with one node."""
    T = nx.join_trees([])
    assert len(T) == 1
    assert T.number_of_edges() == 0


def test_single():
    """Joining just one tree yields a tree with one more node."""
    T = nx.empty_graph(1)
    trees = [(T, 0)]
    custom_label_attribute = "custom_label"
    actual_with_label = nx.join_trees(trees, label_attribute=custom_label_attribute)
    actual_without_label = nx.join_trees(trees)
    expected = nx.path_graph(2)
    assert nodes_equal(list(expected), list(actual_with_label))
    assert nodes_equal(list(expected), list(actual_without_label))
    assert edges_equal(list(expected.edges()), list(actual_with_label.edges()))
    assert edges_equal(list(expected.edges()), list(actual_without_label.edges()))
    assert _check_custom_label_attribute(
        trees, actual_with_label, custom_label_attribute
    )
    assert _check_no_label_attribute(actual_without_label)


def test_basic():
    """Joining multiple subtrees at a root node."""
    trees = [(nx.full_rary_tree(2, 2**2 - 1), 0) for i in range(2)]
    label_attribute = "old_values"
    actual = nx.join_trees(trees, label_attribute)
    expected = nx.full_rary_tree(2, 2**3 - 1)
    assert nx.is_isomorphic(actual, expected)


def test_first_label():
    """Test the functionality of the first_label argument."""
    T1 = nx.path_graph(3)
    T2 = nx.path_graph(2)
    actual = nx.join_trees([(T1, 0), (T2, 0)], first_label=10)
    expected_nodes = set(range(10, 16))
    assert set(actual.nodes()) == expected_nodes
    assert set(actual.neighbors(10)) == {11, 14}
