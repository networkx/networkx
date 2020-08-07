import networkx as nx
import numpy as np


def test_randomized_2_approx():
    G = nx.generators.complete_graph(5)
    _, (cut, _) = nx.algorithms.maxcut.randomized_2_approx(G)
    for node in cut:
        assert node in G.nodes()


def test_one_exchange():
    G = nx.generators.complete_graph(5)
    for (u, v, w) in G.edges(data=True):
        w['weight'] = np.random.random_sample() * 2 - 1

    initial_cut = np.random.choice(G.nodes(), 5)
    cut_size, (cut, _) = nx.algorithms.maxcut.one_exchange(G, initial_cut, weight='weight')

    # make sure it is a valid cut
    for node in cut:
        assert node in G.nodes()

    # test if cut can be locally improved
    for i, node in enumerate(cut):
        cut_size_without_node = nx.algorithms.cut_size(G, cut - {node}, weight='weight')
        assert cut_size_without_node <= cut_size
