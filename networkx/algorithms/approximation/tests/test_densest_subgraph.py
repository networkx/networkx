import pytest

import networkx as nx
import networkx.algorithms.approximation as approx


def test_greedy_peeling_star():
    G = nx.star_graph(4)
    # The densest subgraph of a star network is the entire graph: 4/5 (4 edges, 5 nodes in total)
    # The peeling algorithm would peel all the vertices with degree 1, and so should discover
    # The densest subgraph in one iteration!
    print(dir(approx))
    d, S = approx.greedy_peeling(G)

    assert d == pytest.approx(0.8)  # The density, 4/5=0.8.
    assert S == {0, 1, 2, 3, 4}  # The entire graph!


def test_greedy_plus_plus_complete_graph():
    G = nx.complete_graph(4)
    # The density of a complete graph network is the entire graph: C(4, 2)/4 where C(n, 2) is n*(n-1)//2.
    # The peeling algorithm would find the densest subgraph in one iteration!
    d, S = approx.greedy_plus_plus(G, iterations=10)

    assert d == pytest.approx(6 / 4)  # The density, 4/5=0.8.
    assert S == {0, 1, 2, 3}  # The entire graph!


def test_greedy_plus_plus_close_cliques():
    assert 1 == 1
