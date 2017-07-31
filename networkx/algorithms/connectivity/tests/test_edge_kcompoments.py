# -*- coding: utf-8 -*-
import networkx as nx
from networkx.utils import arbitrary_element, pairwise, flatten
import networkx as nx


def demodata_bridge():
    # define 2-connected compoments and bridges
    cc2 = [(1, 2, 4, 3, 1, 4), (8, 9, 10, 8), (11, 12, 13, 11)]
    bridges = [(4, 8), (3, 5), (20, 21), (22, 23, 24)]
    G = nx.Graph(flatten(pairwise(path) for path in cc2 + bridges))
    return G


def demodata_tarjan_bridge():
    """ graph from tarjan paper """
    # define 2-connected compoments and bridges
    ccs = [(1, 2, 4, 3, 1, 4), (5, 6, 7, 5), (8, 9, 10, 8),
             (17, 18, 16, 15, 17), (11, 12, 14, 13, 11, 14)]
    bridges = [(4, 8), (3, 5), (3, 17)]
    G = nx.Graph(flatten(pairwise(path) for path in ccs + bridges))
    return G


def test_k_edge():
    G = demodata_tarjan_bridge()
    print(list(k_edge_components(G, k=1)))
    print(list(k_edge_components(G, k=2)))
    print(list(k_edge_components(G, k=3)))
    print(list(k_edge_components(G, k=4)))


def test_bridge_cc():
    G = demodata_bridge()
    bridge_ccs = bridge_connected_compoments(G)
    assert bridge_ccs == [
        {1, 2, 3, 4}, {5}, {8, 9, 10}, {11, 12, 13}, {20},
        {21}, {22}, {23}, {24}
    ]
