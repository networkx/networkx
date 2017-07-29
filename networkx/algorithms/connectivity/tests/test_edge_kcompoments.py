# -*- coding: utf-8 -*-
import networkx as nx
import itertools as it
from nose.tools import assert_equal, assert_greater_equal, assert_raises
from networkx.utils import pairwise
from networkx.algorithms.connectivity import (
    k_edge_components,
    k_edge_subgraphs,
    bridge_compoments,
    general_k_edge_subgraphs,
    EdgeComponentAuxGraph,
)


# ----------------
# Helper functions
# ----------------

def fset(list_of_sets):
    """ allows == to be used for list of sets """
    return set(map(frozenset, list_of_sets))


def _assert_cc_subgraph_edge_connectivity(G, ccs_subgraph, k):
    """
    tests properties of k-edge-connected subgraphs

    the actual edge connectivity should be no less than k unless the cc is a
    single node.
    """
    for cc in ccs_subgraph:
        C = G.subgraph(cc)
        if len(cc) > 1:
            connectivity = nx.edge_connectivity(C)
            assert_greater_equal(connectivity, k)


def _assert_cc_local_edge_conectivity(G, ccs_local, k):
    """
    tests properties of k-edge-connected components

    the local edge connectivity between each pair of nodes in the the original
    graph should be no less than k unless the cc is a single node.
    """
    for cc in ccs_local:
        if len(cc) > 1:
            for u, v in it.combinations(cc, 2):
                connectivity = nx.edge_connectivity(G, u, v)
                assert_greater_equal(connectivity, k)
                if G.is_directed():
                    connectivity2 = nx.edge_connectivity(G, v, u)
                    assert_greater_equal(connectivity2, k)


# Helper function
def _check_edge_connectivity(G):
    """
    Helper - generates all k-edge-components using the aux graph.  Checks the
    both local and subgraph edge connectivity of each cc. Also checks that
    alternate methods of computing the k-edge-ccs generate the same result.
    """
    # Construct the auxillary graph that can be used to make each k-cc or k-sub
    aux_graph = EdgeComponentAuxGraph.construct(G)

    for k in it.count(1):
        # Test "local" k-edge-components and k-edge-subgraphs
        ccs_local = fset(aux_graph.k_edge_components(k))
        ccs_subgraph = fset(aux_graph.k_edge_subgraphs(k))

        # Check connectivity properties that should be garuenteed by the
        # algorithms.
        _assert_cc_local_edge_conectivity(G, ccs_local, k)
        _assert_cc_subgraph_edge_connectivity(G, ccs_subgraph, k)

        if k == 1 or k == 2 and not G.is_directed():
            assert_equal(ccs_local, ccs_subgraph,
                         'Subgraphs and components should be the same '
                         'when k == 1 or (k == 2 and not G.directed())')

        if G.is_directed():
            # Test special case methods are the same as the aux graph
            if k == 1:
                alt_sccs = fset(nx.strongly_connected_components(G))
                assert_equal(alt_sccs, ccs_local, 'k=1 failed alt')
                assert_equal(alt_sccs, ccs_subgraph, 'k=1 failed alt')
        else:
            # Test special case methods are the same as the aux graph
            if k == 1:
                alt_ccs = fset(nx.connected_components(G))
                assert_equal(alt_ccs, ccs_local, 'k=1 failed alt')
                assert_equal(alt_ccs, ccs_subgraph, 'k=1 failed alt')
            elif k == 2:
                alt_bridge_ccs = fset(bridge_compoments(G))
                assert_equal(alt_bridge_ccs, ccs_local, 'k=2 failed alt')
                assert_equal(alt_bridge_ccs, ccs_subgraph, 'k=2 failed alt')
            # if new methods for k == 3 or k == 4 are implemented add them here

        # Check the general subgraph method works by itself
        alt_subgraph_ccs = fset([set(C.nodes()) for C in
                                 general_k_edge_subgraphs(G, k=k)])
        assert_equal(alt_subgraph_ccs, ccs_subgraph,
                     'alt subgraph method failed')

        # Stop once k is larger than all special case methods
        # and we cannot break down ccs any further.
        if k > 2 and all(len(cc) == 1 for cc in ccs_local):
            break


# ----------------
# Misc tests
# ----------------

def test_zero_k_exception():
    G = nx.Graph()
    # functions that return generators error immediately
    assert_raises(ValueError, k_edge_components, G, k=0)
    assert_raises(ValueError, k_edge_subgraphs, G, k=0)

    # actual generators only error when you get the first item
    aux_graph = EdgeComponentAuxGraph.construct(G)
    assert_raises(ValueError, list, aux_graph.k_edge_components(k=0))
    assert_raises(ValueError, list, aux_graph.k_edge_subgraphs(k=0))


def test_empty_input():
    G = nx.Graph()
    assert_equal([], list(k_edge_components(G, k=5)))
    assert_equal([], list(k_edge_subgraphs(G, k=5)))

    G = nx.DiGraph()
    assert_equal([], list(k_edge_components(G, k=5)))
    assert_equal([], list(k_edge_subgraphs(G, k=5)))


# ----------------
# Undirected tests
# ----------------

def test_random_gnp():
    seeds = [1550709854, 1309423156, 4208992358, 2785630813, 1915069929]

    for seed in seeds:
        G = nx.gnp_random_graph(20, 0.2, seed=seed)
        _check_edge_connectivity(G)


def test_configuration():
    seeds = [2718183590, 2470619828, 1694705158, 3001036531, 2401251497]
    for seed in seeds:
        deg_seq = nx.random_powerlaw_tree_sequence(20, seed=seed, tries=5000)
        G = nx.Graph(nx.configuration_model(deg_seq, seed=seed))
        G.remove_edges_from(G.selfloop_edges())
        _check_edge_connectivity(G)


def test_shell():
    # seeds = [2057382236, 3331169846, 1840105863, 476020778, 2247498425]
    seeds = [2057382236, 3331169846]
    for seed in seeds:
        constructor = [(12, 70, 0.8), (15, 40, 0.6)]
        G = nx.random_shell_graph(constructor, seed=seed)
        _check_edge_connectivity(G)


def test_karate():
    G = nx.karate_club_graph()
    _check_edge_connectivity(G)


def test_tarjan_bridge():
    # graph from tarjan paper
    # RE Tarjan - "A note on finding the bridges of a graph"
    # Information Processing Letters, 1974 - Elsevier
    # doi:10.1016/0020-0190(74)90003-9.
    # define 2-connected compoments and bridges
    ccs = [(1, 2, 4, 3, 1, 4), (5, 6, 7, 5), (8, 9, 10, 8),
             (17, 18, 16, 15, 17), (11, 12, 14, 13, 11, 14)]
    bridges = [(4, 8), (3, 5), (3, 17)]
    G = nx.Graph(it.chain(*(pairwise(path) for path in ccs + bridges)))
    _check_edge_connectivity(G)


def test_bridge_cc():
    # define 2-connected compoments and bridges
    cc2 = [(1, 2, 4, 3, 1, 4), (8, 9, 10, 8), (11, 12, 13, 11)]
    bridges = [(4, 8), (3, 5), (20, 21), (22, 23, 24)]
    G = nx.Graph(it.chain(*(pairwise(path) for path in cc2 + bridges)))
    bridge_ccs = fset(bridge_compoments(G))
    target_ccs = fset([
        {1, 2, 3, 4}, {5}, {8, 9, 10}, {11, 12, 13}, {20},
        {21}, {22}, {23}, {24}
    ])
    assert_equal(bridge_ccs, target_ccs)
    _check_edge_connectivity(G)


def test_undirected_aux_graph():
    # Graph similar to the one in
    # http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0136264
    a, b, c, d, e, f, g, h, i = 'abcdefghi'
    paths = [
        (a, d, b, f, c),
        (a, e, b),
        (a, e, b, c, g, b, a),
        (c, b),
        (f, g, f),
        (h, i)
    ]
    G = nx.Graph(it.chain.from_iterable(pairwise(path) for path in paths))
    aux_graph = EdgeComponentAuxGraph.construct(G)

    components_1 = fset(aux_graph.k_edge_subgraphs(k=1))
    target_1 = fset([{a, b, c, d, e, f, g}, {h, i}])
    assert_equal(target_1, components_1)

    # Check that the undirected case for k=1 agrees with CCs
    alt_1 = fset(k_edge_subgraphs(G, k=1))
    assert_equal(alt_1, components_1)

    components_2 = fset(aux_graph.k_edge_subgraphs(k=2))
    target_2 = fset([{a, b, c, d, e, f, g}, {h}, {i}])
    assert_equal(target_2, components_2)

    # Check that the undirected case for k=2 agrees with bridge components
    alt_2 = fset(k_edge_subgraphs(G, k=2))
    assert_equal(alt_2, components_2)

    components_3 = fset(aux_graph.k_edge_subgraphs(k=3))
    target_3 = fset([{a}, {b, c, f, g}, {d}, {e}, {h}, {i}])
    assert_equal(target_3, components_3)

    components_4 = fset(aux_graph.k_edge_subgraphs(k=4))
    target_4 = fset([{a}, {b}, {c}, {d}, {e}, {f}, {g}, {h}, {i}])
    assert_equal(target_4, components_4)

    _check_edge_connectivity(G)


def test_local_subgraph_difference():
    paths = [
        (11, 12, 13, 14, 11, 13, 14, 12),  # a 4-clique
        (21, 22, 23, 24, 21, 23, 24, 22),  # another 4-clique
        # paths connecting each vertex of the 4 cliques
        (11, 101, 21),
        (12, 102, 22),
        (13, 103, 23),
        (14, 104, 24),
    ]
    G = nx.Graph(it.chain.from_iterable(pairwise(path) for path in paths))
    aux_graph = EdgeComponentAuxGraph.construct(G)

    # Each clique is returned separately in k-edge-subgraphs
    subgraph_ccs = fset(aux_graph.k_edge_subgraphs(3))
    subgraph_target = fset([{101}, {102}, {103}, {104},
                            {21, 22, 23, 24}, {11, 12, 13, 14}])
    assert_equal(subgraph_ccs, subgraph_target)

    # But in k-edge-ccs they are returned together
    # because they are locally 3-edge-connected
    local_ccs = fset(aux_graph.k_edge_components(3))
    local_target = fset([{101}, {102}, {103}, {104},
                         {11, 12, 13, 14, 21, 22, 23, 24}])
    assert_equal(local_ccs, local_target)


def test_triangles():
    paths = [
        (11, 12, 13, 11),  # a 3-clique
        (21, 22, 23, 21),  # another 3-clique
        (11, 21),  # connected by an edge
    ]
    G = nx.Graph(it.chain.from_iterable(pairwise(path) for path in paths))
    _check_edge_connectivity(G)

    # aux_graph = EdgeComponentAuxGraph.construct(G)
    # components_2 = fset(aux_graph.k_edge_subgraphs(k=2))


def test_four_clique():
    paths = [
        (11, 12, 13, 14, 11, 13, 14, 12),  # a 4-clique
        (21, 22, 23, 24, 21, 23, 24, 22),  # another 4-clique
        # paths connecting the 4 cliques such that they are
        # 3-connected in G, but not in the subgraph.
        # Case where the nodes bridging them do not have degree less than 3.
        (50, 13),
        (12, 50, 22),
        (13, 102, 23),
        (14, 101, 24),
    ]

    G = nx.Graph(it.chain.from_iterable(pairwise(path) for path in paths))
    _check_edge_connectivity(G)


# ----------------
# Undirected tests
# ----------------

def test_directed_aux_graph():
    # Graph similar to the one in
    # http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0136264
    a, b, c, d, e, f, g, h, i = 'abcdefghi'
    dipaths = [
        (a, d, b, f, c),
        (a, e, b),
        (a, e, b, c, g, b, a),
        (c, b),
        (f, g, f),
        (h, i)
    ]
    G = nx.DiGraph(it.chain.from_iterable(pairwise(path) for path in dipaths))
    aux_graph = EdgeComponentAuxGraph.construct(G)

    components_1 = fset(aux_graph.k_edge_subgraphs(k=1))
    target_1 = fset([{a, b, c, d, e, f, g}, {h}, {i}])
    assert_equal(target_1, components_1)

    # Check that the directed case for k=1 agrees with SCCs
    alt_1 = fset(nx.strongly_connected_components(G))
    assert_equal(alt_1, components_1)

    components_2 = fset(aux_graph.k_edge_subgraphs(k=2))
    target_2 = fset([{i}, {e}, {d}, {b, c, f, g}, {h}, {a}])
    assert_equal(target_2, components_2)

    components_3 = fset(aux_graph.k_edge_subgraphs(k=3))
    target_3 = fset([{a}, {b}, {c}, {d}, {e}, {f}, {g}, {h}, {i}])
    assert_equal(target_3, components_3)


def test_random_gnp_directed():
    seeds = [3894723670, 500186844, 267231174, 2181982262, 1116750056]
    for seed in seeds:
        G = nx.gnp_random_graph(20, 0.2, directed=True, seed=seed)
        _check_edge_connectivity(G)


def test_configuration_directed():
    seeds = [671221681, 2403749451, 124433910, 672335939, 1193127215]
    for seed in seeds:
        deg_seq = nx.random_powerlaw_tree_sequence(20, seed=seed, tries=5000)
        G = nx.DiGraph(nx.configuration_model(deg_seq, seed=seed))
        G.remove_edges_from(G.selfloop_edges())
        _check_edge_connectivity(G)


def test_shell_directed():
    # seeds = [3134027055, 4079264063, 1350769518, 1405643020, 530038094]
    seeds = [3134027055, 4079264063]
    for seed in seeds:
        constructor = [(12, 70, 0.8), (15, 40, 0.6)]
        G = nx.random_shell_graph(constructor, seed=seed).to_directed()
        _check_edge_connectivity(G)


def test_karate_directed():
    G = nx.karate_club_graph().to_directed()
    _check_edge_connectivity(G)


def timing():
    seed = 3894723670

    constructor = [
        (50, 300, .99),
        (50, 300, .99),
        (50, 300, .99),
        (50, 300, .99),
    ]
    G = nx.random_shell_graph(constructor, seed=seed)

    # Check which method is faster
    import ubelt
    for timer in ubelt.Timerit(10, 'direct subgraph'):
        with timer:
            len(list(k_edge_subgraphs(G, k=4)))

    for timer in ubelt.Timerit(10, 'aux-subgraph'):
        with timer:
            aux_graph = EdgeComponentAuxGraph.construct(G)
            len(list(aux_graph.k_edge_subgraphs(k=4)))

    aux_graph = EdgeComponentAuxGraph.construct(G)
    for timer in ubelt.Timerit(10, 'pre-aux-subgraph'):
        with timer:
            len(list(aux_graph.k_edge_subgraphs(k=4)))

    # Timing complete for: direct subgraph, 10 loops, best of 3
    #     time per loop : 339.0 ms seconds
    # Timing complete for: aux-subgraph, 10 loops, best of 3
    #     time per loop : 2.872 s seconds
    # Timing complete for: pre-aux-subgraph, 10 loops, best of 3
    #     time per loop : 60.36 ms seconds


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/networkx/networkx/algorithms/connectivity/tests/test_edge_kcompoments.py

        nosetests ~/code/networkx/networkx/algorithms/connectivity --with-doctest --verbose
        nosetests ~/code/networkx/networkx/algorithms/connectivity/tests/test_edge_kcompoments.py --with-doctest --verbose
    """
    # TODO: remove after development is complete
    import utool as ut
    ut.cprint('--- TEST EDGE KCOMP ---', 'blue')

    test_names = sorted([k for k in vars().keys() if k.startswith('test_')])
    # test_names = [
    #     'test_zero_k_exception',
    #     # 'test_tarjan_bridge',
    #     # 'test_karate',
    #     'test_random_gnp_directed',
    # ]
    for key in test_names:
        func = vars()[key]
        ut.cprint('Testing func = {!r}'.format(key), 'blue')
        func()

    if False:
        # debugging
        aux_graph = EdgeComponentAuxGraph.construct(G)
        ccs = fset(aux_graph.k_edge_subgraphs(k=3))
        print('ccs = {!r}'.format(ccs))

        import plottool as pt

        nx.set_node_attributes(G, 'ccid', ut.dzip(G.nodes(), G.nodes()))
        nx.set_node_attributes(G, 'ccid', ut.dzip(paths[0], [1]))
        nx.set_node_attributes(G, 'ccid', ut.dzip(paths[0], [2]))
        nx.set_edge_attributes(aux_graph.A, 'label', ut.map_vals(str, nx.get_edge_attributes(aux_graph.A, 'weight')))
        _ = pt.show_nx(G, pnum=(1, 2, 1), fnum=1, groupby='ccid', layoutkw={'prog': 'neato'})  # NOQA
        _ = pt.show_nx(aux_graph.A, pnum=(1, 2, 2), fnum=1)  # NOQA
        print('ccs = {!r}'.format(ccs))
