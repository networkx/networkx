# -*- coding: utf-8 -*-
import random
import networkx as nx
import itertools as it
from networkx.utils import pairwise
from nose.tools import (assert_equal, assert_raises)
from networkx.algorithms.connectivity import (
    k_edge_augmentation,
)
from networkx.algorithms.connectivity.edge_augmentation import (
    one_edge_augmentation,
    complement_edges,
    bridge_augmentation
)


def fset(list_of_sets):
    """ allows == to be used for list of sets """
    return set(map(frozenset, list_of_sets))


def demodata_tarjan_bridge():
    # graph from tarjan paper
    # RE Tarjan - "A note on finding the bridges of a graph"
    # Information Processing Letters, 1974 - Elsevier
    # doi:10.1016/0020-0190(74)90003-9.
    # define 2-connected components and bridges
    ccs = [(1, 2, 4, 3, 1, 4), (5, 6, 7, 5), (8, 9, 10, 8),
             (17, 18, 16, 15, 17), (11, 12, 14, 13, 11, 14)]
    bridges = [(4, 8), (3, 5), (3, 17)]
    G = nx.Graph(it.chain(*(pairwise(path) for path in ccs + bridges)))
    return G


def test_one_aug():
    G = nx.Graph()
    G.add_nodes_from([
        1, 2, 3, 4, 5, 6, 7, 8, 9])
    G.add_edges_from([(3, 8), (1, 2), (2, 3)])
    impossible = {(6, 3), (3, 9)}
    rng = random.Random(0)
    avail = list(set(complement_edges(G)) - impossible)
    avail_uvd = [(u, v, {'weight': rng.random()}) for u, v in avail]
    aug_edges1 = list(one_edge_augmentation(G))
    aug_edges2 = list(one_edge_augmentation(G, avail))
    aug_edges3 = list(one_edge_augmentation(G, avail_uvd))


def test_bridge_aug():
    G = demodata_tarjan_bridge()
    bridge_edges = bridge_augmentation(G)

    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4])
    bridge_edges = bridge_augmentation(G)


def test_weighted_bridge_augment():
    G = demodata_tarjan_bridge()
    avail = [(9, 7), (8, 5), (2, 10), (6, 13), (11, 18), (1, 17), (2, 3),
             (16, 17), (18, 14), (15, 14)]
    assert_raises(nx.NetworkXUnfeasible, k_edge_augmentation, G, k=2, avail=[])
    k_edge_augmentation(G, k=2, avail=[(9, 7)], partial=True)
    aug_edges = set(k_edge_augmentation(G, k=2, avail=avail))

    # assert_equal(fset(aug_edges), fset({(6, 13), (2, 10), (1, 17)}))

    # test2
    G = nx.Graph([(1, 2), (1, 3), (1, 4), (4, 2), (2, 5)])
    avail = [(4, 5)]
    # assert_raises(nx.NetworkXUnfeasible, k_edge_augmentation, G, 2, avail)
    aug_edges = k_edge_augmentation(G, k=2, avail=avail, partial=True)
    avail = [(3, 5), (4, 5)]
    aug_edges = k_edge_augmentation(G, k=2, avail=avail)


def test_aug():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4, 5, 6])

    k = 2
    aug_edges = k_edge_augmentation(G, k)

    G.add_edges_from(aug_edges)
    print(nx.edge_connectivity(G))

    G = nx.Graph()
    G.add_nodes_from([
        1, 2, 3, 4, 5, 6, 7, 8, 9])
    G.add_edges_from([(3, 8)])
    impossible = {(6, 3), (3, 9)}
    avail = list(set(complement_edges(G)) - impossible)
    aug_edges = k_edge_augmentation(G, k=1)
    aug_edges = k_edge_augmentation(G, k=1, avail=avail)


def test_bridge():
    G = nx.Graph([(2393, 2257), (2393, 2685), (2685, 2257), (1758, 2257)])
    bridge_edges = list(bridge_augmentation(G))
    assert not any([G.has_edge(*e) for e in bridge_edges])


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/networkx/networkx/algorithms/connectivity/tests/test_edge_augmentation.py
        nosetests ~/code/networkx/networkx/algorithms/connectivity --match=edge_augmentation --with-doctest --verbosity=3
        nosetests ~/code/networkx/networkx/algorithms/connectivity/tests/test_edge_augmentation.py --with-doctest --verbosity=3
    """
    # TODO: remove after development is complete
    import utool as ut
    ut.cprint('--- TEST EDGE AUG ---', 'blue')

    test_names = sorted([k for k in vars().keys() if k.startswith('test_')])
    # test_names = [
    #     'test_zero_k_exception',
    #     # 'test_tarjan_bridge',
    #     'test_karate',
    #     'test_random_gnp_directed',
    # ]
    times = {}
    for key in test_names:
        import ubelt as ub
        ut.cprint('Testing func = {!r}'.format(key), 'blue')
        func = vars()[key]
        with ub.Timer(label=key, verbose=True) as t:
            func()
        times[key] = t.ellapsed
        print(ut.repr4(ut.sort_dict(times, 'vals')))
