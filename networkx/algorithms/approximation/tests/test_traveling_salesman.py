"""Unit tests for the traveling_salesman module."""
from pytest import raises
import random
import networkx as nx


def test_christofides_exception():
    G = nx.complete_graph(10)
    G.remove_edge(0, 1)
    raises(ValueError, nx.approximation.christofides, G)


def test_christofides_hamiltonian():
    random.seed(42)
    G = nx.complete_graph(20)
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.randint(0, 10)

    H = nx.Graph()
    H.add_edges_from(nx.approximation.christofides(G))
    H.remove_edges_from(nx.find_cycle(H))
    assert len(H.edges) == 0

    tree = nx.minimum_spanning_tree(G, weight='weight')
    H = nx.Graph()
    H.add_edges_from(nx.approximation.christofides(G, tree))
    H.remove_edges_from(nx.find_cycle(H))
    assert len(H.edges) == 0


def test_christofides_selfloop():
    G = nx.complete_graph(10)
    G.add_edge(3, 3)
    raises(ValueError, nx.approximation.christofides, G)


def test_TSP_unweighted():
    G = nx.cycle_graph(9)
    path = nx.approximation.traveling_salesman_problem(G, [3, 6], cycle=False)
    assert path in ([3, 4, 5, 6], [6, 5, 4, 3])

    cycle = nx.approximation.traveling_salesman_problem(G, [3, 6])
    assert cycle in ([3, 4, 5, 6, 5, 4, 3], [6, 5, 4, 3, 4, 5, 6])


def test_TSP_weighted():
    G = nx.cycle_graph(9)
    G[0][1]['weight'] = 2
    G[1][2]['weight'] = 2
    G[2][3]['weight'] = 2
    G[3][4]['weight'] = 4
    G[4][5]['weight'] = 5
    G[5][6]['weight'] = 4
    G[6][7]['weight'] = 2
    G[7][8]['weight'] = 2
    G[8][0]['weight'] = 2
    tsp = nx.approximation.traveling_salesman_problem
    path = tsp(G, [3, 6], weight='weight', cycle=False)
    assert path in ([3, 2, 1, 0, 8, 7, 6], [6, 7, 8, 0, 1, 2, 3])

    cycle = tsp(G, [3, 6], weight='weight')
    expected = ([3, 2, 1, 0, 8, 7, 6, 7, 8, 0, 1, 2, 3],
                [6, 7, 8, 0, 1, 2, 3, 2, 1, 0, 8, 7, 6])
    assert cycle in expected
