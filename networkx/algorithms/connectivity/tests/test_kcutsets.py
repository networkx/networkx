# Jordi Torrents
# Test for k-cutsets
from operator import itemgetter
from nose.tools import assert_equal, assert_false, assert_true, assert_raises
import networkx as nx
from networkx.algorithms.connectivity.kcutsets import _is_separating_set

from networkx.algorithms.flow import (
    edmonds_karp,
    shortest_augmenting_path,
    preflow_push,
)


##
## Some nice synthetic graphs
##
def graph_example_1():
    G = nx.convert_node_labels_to_integers(nx.grid_graph([5,5]),
                                            label_attribute='labels')
    rlabels = nx.get_node_attributes(G, 'labels')
    labels = dict((v, k) for k, v in rlabels.items())

    for nodes in [(labels[(0,0)], labels[(1,0)]),
                    (labels[(0,4)], labels[(1,4)]),
                    (labels[(3,0)], labels[(4,0)]),
                    (labels[(3,4)], labels[(4,4)]) ]:
        new_node = G.order()+1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G,P)
        # Add two edges between the grid and P
        G.add_edge(new_node+1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G,K)
        # Add three edges between P and K5
        G.add_edge(new_node+2,new_node+11)
        G.add_edge(new_node+3,new_node+12)
        G.add_edge(new_node+4,new_node+13)
        # Add another K5 sharing a node
        G = nx.disjoint_union(G,K)
        nbrs = G[new_node+10]
        G.remove_node(new_node+10)
        for nbr in nbrs:
            G.add_edge(new_node+17, nbr)
        G.add_edge(new_node+16, new_node+5)

    G.name = 'Example graph for connectivity'
    return G


def torrents_and_ferraro_graph():
    G = nx.convert_node_labels_to_integers(nx.grid_graph([5,5]),
                                            label_attribute='labels')
    rlabels = nx.get_node_attributes(G, 'labels')
    labels = dict((v, k) for k, v in rlabels.items())

    for nodes in [ (labels[(0,4)], labels[(1,4)]),
                    (labels[(3,4)], labels[(4,4)]) ]:
        new_node = G.order()+1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G,P)
        # Add two edges between the grid and P
        G.add_edge(new_node+1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G,K)
        # Add three edges between P and K5
        G.add_edge(new_node+2,new_node+11)
        G.add_edge(new_node+3,new_node+12)
        G.add_edge(new_node+4,new_node+13)
        # Add another K5 sharing a node
        G = nx.disjoint_union(G,K)
        nbrs = G[new_node+10]
        G.remove_node(new_node+10)
        for nbr in nbrs:
            G.add_edge(new_node+17, nbr)
        # Commenting this makes the graph not biconnected !!
        # This stupid mistake make one reviewer very angry :P
        G.add_edge(new_node+16, new_node+8)

    for nodes in [(labels[(0,0)], labels[(1,0)]),
                    (labels[(3,0)], labels[(4,0)])]:
        new_node = G.order()+1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G,P)
        # Add two edges between the grid and P
        G.add_edge(new_node+1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G,K)
        # Add three edges between P and K5
        G.add_edge(new_node+2,new_node+11)
        G.add_edge(new_node+3,new_node+12)
        G.add_edge(new_node+4,new_node+13)
        # Add another K5 sharing two nodes
        G = nx.disjoint_union(G,K)
        nbrs = G[new_node+10]
        G.remove_node(new_node+10)
        for nbr in nbrs:
            G.add_edge(new_node+17, nbr)
        nbrs2 = G[new_node+9]
        G.remove_node(new_node+9)
        for nbr in nbrs2:
            G.add_edge(new_node+18, nbr)

    G.name = 'Example graph for connectivity'
    return G


# Helper function
def _check_separating_sets(G):
    for Gc in nx.connected_component_subgraphs(G):
        if len(Gc) < 3:
            continue
        for cut in nx.all_node_cuts(Gc):
            assert_equal(nx.node_connectivity(Gc), len(cut))
            H = Gc.copy()
            H.remove_nodes_from(cut)
            assert_false(nx.is_connected(H))


def test_torrents_and_ferraro_graph():
    G = torrents_and_ferraro_graph()
    _check_separating_sets(G)


def test_example_1():
    G = graph_example_1()
    _check_separating_sets(G)

def test_random_gnp():
    G = nx.gnp_random_graph(100, 0.1)
    _check_separating_sets(G)


def test_shell():
    constructor=[(20,80,0.8),(80,180,0.6)]
    G = nx.random_shell_graph(constructor)
    _check_separating_sets(G)


def test_configuration():
    deg_seq = nx.utils.create_degree_sequence(100,nx.utils.powerlaw_sequence)
    G = nx.Graph(nx.configuration_model(deg_seq))
    G.remove_edges_from(G.selfloop_edges())
    _check_separating_sets(G)


def test_karate():
    G = nx.karate_club_graph()
    _check_separating_sets(G)


def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100,0.0575)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = "Tried %d times: no suitable Graph."%attempts
                raise Exception(msg % max_attempts)
            else:
                attempts += 1


def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for i in range(2):
        G = next(Ggen)
        articulation_points = list({a} for a in nx.articulation_points(G))
        for cut in nx.all_node_cuts(G):
            assert_true(cut in articulation_points)


def test_grid_2d_graph():
    # All minimum node cuts of a 2d grid
    # are the four pairs of nodes that are
    # neighbors of the four corner nodes.
    G = nx.grid_2d_graph(5, 5)
    solution = [
        set([(0, 1), (1, 0)]),
        set([(3, 0), (4, 1)]),
        set([(3, 4), (4, 3)]),
        set([(0, 3), (1, 4)]),
    ]
    for cut in nx.all_node_cuts(G):
        assert_true(cut in solution)


def test_disconnected_graph():
    G = nx.fast_gnp_random_graph(100, 0.01)
    cuts = nx.all_node_cuts(G)
    assert_raises(nx.NetworkXError, next, cuts)


def test_alternative_flow_functions():
    flow_funcs = [edmonds_karp, shortest_augmenting_path, preflow_push]
    graph_funcs = [graph_example_1, nx.davis_southern_women_graph]
    for graph_func in graph_funcs:
        G = graph_func()
        for flow_func in flow_funcs:
            for cut in nx.all_node_cuts(G, flow_func=flow_func):
                assert_equal(nx.node_connectivity(G), len(cut))
                H = G.copy()
                H.remove_nodes_from(cut)
                assert_false(nx.is_connected(H))

def test_is_separating_set_complete_graph():
    G = nx.complete_graph(5)
    assert_true(_is_separating_set(G, {0, 1, 2, 3}))


def test_is_separating_set():
    for i in [5, 10, 15]:
        G = nx.star_graph(i)
        max_degree_node = max(G, key=G.degree)
        assert_true(_is_separating_set(G, {max_degree_node}))


def test_non_repeated_cuts():
    # The algorithm was repeating the cut {0, 1} for the giant biconnected
    # component of the Karate club graph.
    K = nx.karate_club_graph()
    G = max(list(nx.biconnected_component_subgraphs(K)), key=len)
    solution = [{32, 33}, {2, 33}, {0, 3}, {0, 1}, {29, 33}]
    cuts = list(nx.all_node_cuts(G))
    if len(solution) != len(cuts):
        print(nx.info(G))
        print("Solution: {}".format(solution))
        print("Result: {}".format(cuts))
    assert_true(len(solution) == len(cuts))
    for cut in cuts:
        assert_true(cut in solution)
