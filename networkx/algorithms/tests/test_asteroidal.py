import networkx as nx
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import assert_equal


def test_is_at_free():

    is_at_free = nx.asteroidal.is_at_free

    cycle = nx.cycle_graph(6)
    assert_false(is_at_free(cycle))

    path = nx.path_graph(6)
    assert_true(is_at_free(path))

    small_graph = nx.complete_graph(2)
    assert_true(is_at_free(small_graph))

    petersen = nx.petersen_graph()
    assert_false(is_at_free(petersen))

    clique = nx.complete_graph(6)
    assert_true(is_at_free(clique))

    line_clique = nx.line_graph(clique)
    assert_false(is_at_free(line_clique))
