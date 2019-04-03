import networkx as nx
from nose.tools import *


def test_is_at_free():
    cycle = nx.cycle_graph(6)
    path = nx.path_graph(6)
    small_graph = nx.complete_graph(2)
    petersen = nx.petersen_graph()
    clique = nx.complete_graph(6)
    line_clique = nx.line_graph(clique)

    cycle_at_free = nx.asteroidal.is_at_free(cycle)
    path_at_free = nx.asteroidal.is_at_free(path)
    small_graph_at_free = nx.asteroidal.is_at_free(small_graph)
    petersen_at_free = nx.asteroidal.is_at_free(petersen)
    clique_at_free = nx.asteroidal.is_at_free(clique)
    line_clique_at_free = nx.asteroidal.is_at_free(line_clique)

    assert_equal(cycle_at_free, False)
    assert_equal(path_at_free, True)
    assert_equal(small_graph_at_free, True)
    assert_equal(petersen_at_free, False)
    assert_equal(clique_at_free, True)
    assert_equal(line_clique_at_free, False)
