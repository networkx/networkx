import pytest

np = pytest.importorskip("numpy")
import networkx as nx


def compare_hashed_graphs(*Gs):
    # Should be better implemented already elsewhere...
    last_hash = False
    for G in Gs:
        if last_hash:
            assert last_hash == nx.weisfeiler_lehman_graph_hash(G)
        last_hash = nx.weisfeiler_lehman_graph_hash(G)


def test_max_min_layers():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5)])
    assert nx.max_min_layers(G, max_layer=True) == [0]
    assert nx.max_min_layers(G, max_layer=False) == [3, 4, 5]

    # G = nx.cycle_graph(5, create_using=nx.DiGraph)  # cannot detect cycles with just DAG check...
    # pytest.raises(nx.NetworkXError, nx.max_min_layers, G)


def test_leaf_removal():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5)])

    bottomless_G = nx.DiGraph()
    bottomless_G.add_edges_from([(0, 1), (0, 2)])
    assert nx.leaf_removal(G, top=False).edges() == bottomless_G.edges()
    assert nx.leaf_removal(G, top=False).nodes() == bottomless_G.nodes()

    topless_G = nx.DiGraph()
    topless_G.add_edges_from([(1, 3), (1, 4), (2, 4), (2, 5)])
    assert nx.leaf_removal(G, top=True).edges() == topless_G.edges()
    assert nx.leaf_removal(G, top=True).nodes() == topless_G.nodes()

    G = nx.cycle_graph(5, create_using=nx.DiGraph)
    pytest.raises(nx.NetworkXError, nx.leaf_removal, G)


def test_recursive_leaf_removal():
    diamond_net = [
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 4),
        (2, 5),
        (3, 6),
        (4, 6),
        (4, 7),
        (5, 7),
        (6, 8),
        (7, 8),
    ]
    layer_0 = [(0, 1), (0, 2)]
    layer_1 = [(1, 3), (2, 4), (1, 4), (2, 5)]
    layer_2 = [(3, 6), (4, 6), (4, 7), (5, 7)]
    layer_3 = [(6, 8), (7, 8)]
    G = nx.DiGraph(diamond_net)

    pruned_from_top = nx.recursive_leaf_removal(G, from_top=True)
    pruned_from_bottom = nx.recursive_leaf_removal(G, from_top=False)

    # As the original graph is always the first element
    compare_hashed_graphs(pruned_from_top[0], pruned_from_bottom[0])
    compare_hashed_graphs(pruned_from_top[1], nx.DiGraph(layer_1 + layer_2 + layer_3))
    compare_hashed_graphs(pruned_from_top[2], nx.DiGraph(layer_2 + layer_3))
    compare_hashed_graphs(pruned_from_top[3], nx.DiGraph(layer_3))
    compare_hashed_graphs(
        pruned_from_bottom[1], nx.DiGraph(layer_2 + layer_1 + layer_0)
    )
    compare_hashed_graphs(pruned_from_bottom[2], nx.DiGraph(layer_1 + layer_0))
    compare_hashed_graphs(pruned_from_bottom[3], nx.DiGraph(layer_0))
    # No cycles
    G = nx.cycle_graph(5, create_using=nx.DiGraph)
    pytest.raises(nx.NetworkXError, nx.recursive_leaf_removal, G)


def test_weight_nodes_by_condensation():
    center_cycle = [(0, 1), (1, 2), (2, 3), (3, 1), (3, 4)]
    # unit weights by default
    G = nx.DiGraph(center_cycle)
    # Must be condensed (acyclic)
    pytest.raises(nx.NetworkXError, nx.weight_nodes_by_condensation, G)

    condensed_G = nx.condensation(G)
    nodes_w_cycle_weight = nx.weight_nodes_by_condensation(condensed_G)
    assert nodes_w_cycle_weight.nodes[0]["weight"] == 1
    assert nodes_w_cycle_weight.nodes[1]["weight"] == 3
    assert nodes_w_cycle_weight.nodes[2]["weight"] == 1


def test_node_weighted_condense():
    center_cycle_A = np.array(
        [
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0],
        ]
    )  # this condensation eliminates the smaller, unconnected cycles, e.g. {(5, 6), (6, 5)}
    center_cycle = [(0, 1), (1, 2), (2, 3), (3, 1), (3, 4), (5, 6), (6, 5)]
    # unit weights by default
    G = nx.DiGraph(center_cycle)
    compare_hashed_graphs(
        nx.from_numpy_array(A=center_cycle_A, create_using=nx.DiGraph), G
    )

    condensed_G, original_G = nx.node_weighted_condense(A=center_cycle_A)
    # single threshold for binary graphs
    assert len(condensed_G) == 1 == len(original_G)
    assert condensed_G[0].nodes[0]["weight"] == 1
    assert condensed_G[0].nodes[1]["weight"] == 3
    assert condensed_G[0].nodes[2]["weight"] == 1

    # Weighted network condense: this condensation eliminates the smaller, unconnected cycles, e.g. {(5, 6), (6, 5)}
    weighted_center_cycle_A = np.array(
        [
            [0, 0.9, 0, 0, 0, 0, 0],
            [0, 0, 0.8, 0, 0, 0, 0],
            [0, 0, 0, 0.4, 0, 0, 0],
            [0, 1.7, 0, 0, 0.6, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0.4],
            [0, 0, 0, 0, 0, 0.2, 0],
        ]
    )

    condensed_Gs, binary_Gs = nx.node_weighted_condense(
        A=weighted_center_cycle_A, num_thresholds=5, threshold_distribution=None
    )
    # Not necessarily equal to num thresholds, as empty graphs are dropped
    assert len(condensed_Gs) == len(binary_Gs)
    for binaryG, condensedG in zip(binary_Gs, condensed_Gs):
        # binary checks
        assert np.array_equal(np.unique(nx.to_numpy_array(binaryG)), [0, 1])
        assert np.array_equal(np.unique(nx.to_numpy_array(condensedG)), [0, 1])


def test_orderability():
    center_cycle = [(0, 1), (1, 2), (2, 3), (3, 1), (3, 4)]
    G = nx.DiGraph(center_cycle)
    assert nx.orderability(G) == 2 / 5

    G1 = nx.full_rary_tree(2, 16, create_using=nx.DiGraph())
    assert nx.orderability(G1) == 1.0


def test_feedforwardness():
    infographic_network = [
        (0, 2),
        (1, 2),
        (1, 6),
        (2, 4),
        (3, 2),
        (3, 4),
        (4, 5),
        (5, 3),
        (5, 6),
    ]
    G = nx.weight_nodes_by_condensation(
        nx.condensation(nx.DiGraph(infographic_network))
    )
    assert np.round(nx.feedforwardness(G), 2) == 0.56
    # unit weights by default
    cyclic_G = nx.DiGraph(infographic_network)
    # Must be condensed (acyclic)
    pytest.raises(nx.NetworkXError, nx.feedforwardness, cyclic_G)


def test_graph_entropy():
    b = np.array(
        [
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    condensed_network_layers = nx.recursive_leaf_removal(
        nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph))
    )
    # WIP
    # fwd_graph_entropy = [round(nx.graph_entropy(net, forward_entropy=True), 3) for net in condensed_network_layers]
    # bkwd_graph_entropy = [round(nx.graph_entropy(net), 3) for net in condensed_network_layers]
    # print("graph entropy (forwards | backwards): {0} | {1} [analytic]".format(fwd_graph_entropy, bkwd_graph_entropy))


def test_infographic_graph_entropy():
    b = np.array(
        [
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    condensed_network_layers = nx.recursive_leaf_removal(
        nx.condensation(nx.from_numpy_matrix(b, create_using=nx.DiGraph))
    )
    fwd_graph_entropy = [
        round(nx.infographic_graph_entropy(net, forward_entropy=True), 3)
        for net in condensed_network_layers
    ]
    bkwd_graph_entropy = [
        round(nx.infographic_graph_entropy(net), 3) for net in condensed_network_layers
    ]
    assert fwd_graph_entropy == [0.347, 0.0]
    assert bkwd_graph_entropy == [1.04, 0.0]
    # print("graph entropy (forwards | backwards): {0} | {1} [infographic]".format(fwd_graph_entropy, bkwd_graph_entropy))


def test_treeness():
    infographic_network = [
        (0, 2),
        (1, 2),
        (1, 6),
        (2, 4),
        (3, 2),
        (3, 4),
        (4, 5),
        (5, 3),
        (5, 6),
    ]
    G = nx.weight_nodes_by_condensation(
        nx.condensation(nx.DiGraph(infographic_network))
    )
    assert np.round(nx.feedforwardness(G), 2) == 0.56


def test_hierarchy_coordinate():
    # awaits response from Professor Solé regarding graph entropy evaluation
    pass


# While WIP:
test_treeness()
test_max_min_layers()
test_leaf_removal()
test_recursive_leaf_removal()
test_weight_nodes_by_condensation()
test_node_weighted_condense()
test_orderability()
test_feedforwardness()
test_graph_entropy()
test_infographic_graph_entropy()
test_treeness()
test_hierarchy_coordinate()
