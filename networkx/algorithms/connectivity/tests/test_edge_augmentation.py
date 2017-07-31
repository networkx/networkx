# -*- coding: utf-8 -*-
import networkx as nx
from networkx.utils import arbitrary_element, pairwise, flatten


def test_one_aug():
    G = nx.Graph()
    G.add_nodes_from([
        1, 2, 3, 4, 5, 6, 7, 8, 9])
    G.add_edges_from([(3, 8), (1, 2), (2, 3)])
    impossible = {(6, 3), (3, 9)}
    rng = np.random.RandomState(0)
    avail = list(set(complement_edges(G)) - impossible)
    avail_uvd = [(u, v, {'weight': rng.rand()}) for u, v in avail]
    aug_edges1 = list(one_connected_augmentation(G))
    aug_edges2 = list(one_connected_augmentation(G, avail))
    aug_edges3 = list(one_connected_augmentation(G, avail_uvd))


def test_bridge_aug():
    G = demodata_tarjan_bridge()
    bridge_edges = bridge_connected_augmentation(G)

    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4])
    bridge_edges = bridge_connected_augmentation(G)


def test_weighted_bridge_augment():
    G = demodata_tarjan_bridge()
    avail = [(9, 7), (8, 5), (2, 10), (6, 13), (11, 18), (1, 17), (2, 3),
             (16, 17), (18, 14), (15, 14)]
    ut.assert_raises(ValueError, weighted_bridge_augmentation, G, [])
    weighted_bridge_augmentation(G, [(9, 7)], return_anyway=True)
    aug_edges = set(weighted_bridge_augmentation(G, avail))
    assert aug_edges == {(6, 13), (2, 10), (1, 17)}
    # test2
    G = nx.Graph([(1, 2), (1, 3), (1, 4), (4, 2), (2, 5)])
    avail = [(4, 5)]
    ut.assert_raises(ValueError, weighted_bridge_augmentation, G, avail)
    aug_edges = weighted_bridge_augmentation(G, avail, True)
    avail = [(3, 5), (4, 5)]
    aug_edges = weighted_bridge_augmentation(G, avail)


def test_aug():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4, 5, 6])
    k = 4
    aug_edges = edge_connected_augmentation(G, k)
    G.add_edges_from(aug_edges)
    print(nx.edge_connectivity(G))

    G = nx.Graph()
    G.add_nodes_from([
        1, 2, 3, 4, 5, 6, 7, 8, 9])
    G.add_edges_from([(3, 8)])
    impossible = {(6, 3), (3, 9)}
    avail = list(set(complement_edges(G)) - impossible)
    aug_edges = edge_connected_augmentation(G, k=1)
    aug_edges = edge_connected_augmentation(G, 1, avail)
