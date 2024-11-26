import pytest

import networkx as nx
import networkx.algorithms.approximation as approx


def test_greedy_plus_plus_star():
    G = nx.star_graph(4)
    # The densest subgraph of a star network is the entire graph: 4/5 (4 edges, 5 nodes in total)
    # The peeling algorithm would peel all the vertices with degree 1, and so should discover
    # The densest subgraph in one iteration!
    d, S = approx.greedy_plus_plus(G, iterations=1)

    assert d == pytest.approx(0.8)  # The density, 4/5=0.8.
    assert S == {0, 1, 2, 3, 4}  # The entire graph!


def test_greedy_plus_plus_complete_graph():
    G = nx.complete_graph(4)
    # The density of a complete graph network is the entire graph: C(4, 2)/4 where C(n, 2) is n*(n-1)//2.
    # The peeling algorithm would find the densest subgraph in one iteration!
    d, S = approx.greedy_plus_plus(G, iterations=1)

    assert d == pytest.approx(6 / 4)  # The density, 4/5=0.8.
    assert S == {0, 1, 2, 3}  # The entire graph!


def test_greedy_plus_plus_close_cliques():
    """
    Hard example from Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri.
        "Faster and scalable algorithms for densest subgraph and decomposition."
        Advances in Neural Information Processing Systems 35 (2022): 26966-26979.
    """
    d = 12
    D = 300
    h = 24
    k = 2
    Kh = nx.complete_graph(h)
    KdD = nx.complete_bipartite_graph(d, D)
    G = nx.disjoint_union_all([KdD] + [Kh for _ in range(k)])
    best_density = d * D / (d + D)  # of the complete bipartite graph

    greedy_pp, S_pp = approx.greedy_plus_plus(G, iterations=190)

    assert greedy_pp == pytest.approx(best_density)
    assert S_pp == set(KdD.nodes)


def test_greedy_plus_plus_bipartite_and_clique():
    """
    Hard example from: Boob, Digvijay, Yu Gao, Richard Peng, Saurabh Sawlani, Charalampos Tsourakakis, Di Wang,
        and Junxing Wang. "Flowless: Extracting densest subgraphs without flow computations."
        In Proceedings of The Web Conference 2020, pp. 573-583. 2020.
    """
    d = 5
    D = 200
    k = 2
    B = nx.complete_bipartite_graph(d, D)
    H = [nx.complete_graph(d + 2) for _ in range(k)]
    G = nx.disjoint_union_all([B] + H)

    best_density = d * D / (d + D)  # of the complete bipartite graph
    correct_one_round_density = (2 * d * D + (d + 1) * (d + 2) * k) / (
        2 * d + 2 * D + 2 * k * (d + 2)
    )

    one_round_density, S_one = approx.greedy_plus_plus(G, iterations=1)
    assert one_round_density == pytest.approx(correct_one_round_density)
    assert S_one == set(G.nodes)

    ten_round_density, S_ten = approx.greedy_plus_plus(G, iterations=10)
    assert ten_round_density == pytest.approx(best_density)
    assert S_ten == set(B.nodes)
