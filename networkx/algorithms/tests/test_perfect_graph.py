import pytest

import networkx as nx
from networkx.algorithms.perfect_graph import is_perfect_graph


def test_chordal_graph():
    G = nx.complete_graph(5)
    assert is_perfect_graph(G) is True


def test_odd_cycle():
    G = nx.cycle_graph(5)  # Induced odd cycle
    assert is_perfect_graph(G) is False


def test_even_cycle():
    G = nx.cycle_graph(6)  # Even cycle is perfect
    assert is_perfect_graph(G) is True


def test_complement_of_odd_cycle():
    G = nx.cycle_graph(7)
    GC = nx.complement(G)
    assert is_perfect_graph(GC) is False


def test_disconnected_union_of_cliques():
    G = nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(4))
    assert is_perfect_graph(G) is True


def test_large_cycle_warning():
    G = nx.cycle_graph(13)
    with pytest.warns(RuntimeWarning):
        is_perfect_graph(G, max_cycle_length=13)
