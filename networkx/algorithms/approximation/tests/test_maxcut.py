import networkx as nx
import numpy as np


def _is_valid_cut(G, set1, set2):
    union = set1.union(set2)
    assert union == set(G.nodes)
    assert len(set1) + len(set2) == G.number_of_nodes()


def test_random_partitioning():
    G = nx.generators.complete_graph(5)
    _, (set1, set2) = nx.algorithms.approximation.maxcut.randomized_partitioning(G)
    _is_valid_cut(G, set1, set2)


def test_one_exchange():
    G = nx.generators.complete_graph(5)
    for (u, v, w) in G.edges(data=True):
        w['weight'] = np.random.random_sample() * 2 - 1

    initial_cut = np.random.choice(G.nodes(), 5)
    cut_size, (set1, set2) = nx.algorithms.approximation.maxcut.one_exchange(G, initial_cut, weight='weight')

    # make sure it is a valid cut
    _is_valid_cut(G, set1, set2)

    # test if cut can be locally improved
    for i, node in enumerate(set1):
        cut_size_without_node = nx.algorithms.cut_size(G, set1 - {node}, weight='weight')
        assert cut_size_without_node <= cut_size
