from nose.tools import assert_equal
from networkx import asyn_lpa, Graph


def test_empty_graph():
    # empty graph
    test = Graph()

    # ground truth
    ground_truth = set()

    communities = asyn_lpa.asyn_lpa_communities(test)
    result = {frozenset(c) for c in communities}
    assert_equal(result, ground_truth)


def test_single_node():
    test = Graph()

    test.add_node('a')

    # ground truth
    ground_truth = set([frozenset(['a'])])

    communities = asyn_lpa.asyn_lpa_communities(test)
    result = {frozenset(c) for c in communities}
    assert_equal(result, ground_truth)


def test_simple_communities():
    test = Graph()

    # c1
    test.add_edge('a', 'b')
    test.add_edge('a', 'c')
    test.add_edge('b', 'c')

    # c2
    test.add_edge('d', 'e')
    test.add_edge('d', 'f')
    test.add_edge('f', 'e')

    # ground truth
    ground_truth = set([frozenset(['a', 'c', 'b']),
                        frozenset(['e', 'd', 'f'])])

    communities = asyn_lpa.asyn_lpa_communities(test)
    result = {frozenset(c) for c in communities}
    assert_equal(result, ground_truth)


def test_several_communities():
    test = Graph()

    # c1
    test.add_edge('1a', '1b')
    test.add_edge('1a', '1c')
    test.add_edge('1b', '1c')

    # c2
    test.add_edge('2a', '2b')
    test.add_edge('2a', '2c')
    test.add_edge('2b', '2c')

    # c3
    test.add_edge('3a', '3b')
    test.add_edge('3a', '3c')
    test.add_edge('3b', '3c')

    # c4
    test.add_edge('4a', '4b')
    test.add_edge('4a', '4c')
    test.add_edge('4b', '4c')

    # c5
    test.add_edge('5a', '5b')
    test.add_edge('5a', '5c')
    test.add_edge('5b', '5c')

    # ground truth
    ground_truth = set([frozenset(['1a', '1c', '1b']),
                        frozenset(['2a', '2c', '2b']),
                        frozenset(['3a', '3c', '3b']),
                        frozenset(['4a', '4c', '4b']),
                        frozenset(['5a', '5c', '5b'])])

    communities = asyn_lpa.asyn_lpa_communities(test)
    result = {frozenset(c) for c in communities}
    assert_equal(result, ground_truth)
