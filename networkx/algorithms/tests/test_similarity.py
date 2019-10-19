#!/usr/bin/env python
import pytest

import networkx as nx
from networkx.algorithms.similarity import (
    graph_edit_distance,
    optimal_edit_paths,
    optimize_graph_edit_distance
)
from networkx.generators.classic import (
    circular_ladder_graph,
    cycle_graph,
    path_graph,
    wheel_graph
)


def nmatch(n1, n2):
    return n1 == n2


def ematch(e1, e2):
    return e1 == e2


def getCanonical():
    G = nx.Graph()
    G.add_node('A', label='A')
    G.add_node('B', label='B')
    G.add_node('C', label='C')
    G.add_node('D', label='D')
    G.add_edge('A', 'B', label='a-b')
    G.add_edge('B', 'C', label='b-c')
    G.add_edge('B', 'D', label='b-d')
    return G


class TestSimilarity:

    @classmethod
    def setup_class(cls):
        global numpy
        global scipy
        numpy = pytest.importorskip('numpy')
        scipy = pytest.importorskip('scipy')

    def test_graph_edit_distance(self):
        G0 = nx.Graph()
        G1 = path_graph(6)
        G2 = cycle_graph(6)
        G3 = wheel_graph(7)

        assert graph_edit_distance(G0, G0) == 0
        assert graph_edit_distance(G0, G1) == 11
        assert graph_edit_distance(G1, G0) == 11
        assert graph_edit_distance(G0, G2) == 12
        assert graph_edit_distance(G2, G0) == 12
        assert graph_edit_distance(G0, G3) == 19
        assert graph_edit_distance(G3, G0) == 19

        assert graph_edit_distance(G1, G1) == 0
        assert graph_edit_distance(G1, G2) == 1
        assert graph_edit_distance(G2, G1) == 1
        assert graph_edit_distance(G1, G3) == 8
        assert graph_edit_distance(G3, G1) == 8

        assert graph_edit_distance(G2, G2) == 0
        assert graph_edit_distance(G2, G3) == 7
        assert graph_edit_distance(G3, G2) == 7

        assert graph_edit_distance(G3, G3) == 0

    def test_graph_edit_distance_node_match(self):
        G1 = cycle_graph(5)
        G2 = cycle_graph(5)
        for n, attr in G1.nodes.items():
            attr['color'] = 'red' if n % 2 == 0 else 'blue'
        for n, attr in G2.nodes.items():
            attr['color'] = 'red' if n % 2 == 1 else 'blue'
        assert graph_edit_distance(G1, G2) == 0
        assert graph_edit_distance(G1, G2, node_match=lambda n1, n2: n1['color'] == n2['color']) == 1

    def test_graph_edit_distance_edge_match(self):
        G1 = path_graph(6)
        G2 = path_graph(6)
        for e, attr in G1.edges.items():
            attr['color'] = 'red' if min(e) % 2 == 0 else 'blue'
        for e, attr in G2.edges.items():
            attr['color'] = 'red' if min(e) // 3 == 0 else 'blue'
        assert graph_edit_distance(G1, G2) == 0
        assert graph_edit_distance(G1, G2, edge_match=lambda e1, e2: e1['color'] == e2['color']) == 2

    def test_graph_edit_distance_node_cost(self):
        G1 = path_graph(6)
        G2 = path_graph(6)
        for n, attr in G1.nodes.items():
            attr['color'] = 'red' if n % 2 == 0 else 'blue'
        for n, attr in G2.nodes.items():
            attr['color'] = 'red' if n % 2 == 1 else 'blue'

        def node_subst_cost(uattr, vattr):
            if uattr['color'] == vattr['color']:
                return 1
            else:
                return 10

        def node_del_cost(attr):
            if attr['color'] == 'blue':
                return 20
            else:
                return 50

        def node_ins_cost(attr):
            if attr['color'] == 'blue':
                return 40
            else:
                return 100

        assert graph_edit_distance(G1, G2,
                                   node_subst_cost=node_subst_cost,
                                   node_del_cost=node_del_cost,
                                   node_ins_cost=node_ins_cost) == 6

    def test_graph_edit_distance_edge_cost(self):
        G1 = path_graph(6)
        G2 = path_graph(6)
        for e, attr in G1.edges.items():
            attr['color'] = 'red' if min(e) % 2 == 0 else 'blue'
        for e, attr in G2.edges.items():
            attr['color'] = 'red' if min(e) // 3 == 0 else 'blue'

        def edge_subst_cost(gattr, hattr):
            if gattr['color'] == hattr['color']:
                return 0.01
            else:
                return 0.1

        def edge_del_cost(attr):
            if attr['color'] == 'blue':
                return 0.2
            else:
                return 0.5

        def edge_ins_cost(attr):
            if attr['color'] == 'blue':
                return 0.4
            else:
                return 1.0

        assert graph_edit_distance(G1, G2,
                                   edge_subst_cost=edge_subst_cost,
                                   edge_del_cost=edge_del_cost,
                                   edge_ins_cost=edge_ins_cost) == 0.23

    def test_graph_edit_distance_upper_bound(self):
        G1 = circular_ladder_graph(2)
        G2 = circular_ladder_graph(6)
        assert graph_edit_distance(G1, G2, upper_bound=5) is None
        assert graph_edit_distance(G1, G2, upper_bound=24) == 22
        assert graph_edit_distance(G1, G2) == 22

    def test_optimal_edit_paths(self):
        G1 = path_graph(3)
        G2 = cycle_graph(3)
        paths, cost = optimal_edit_paths(G1, G2)
        assert cost == 1
        assert len(paths) == 6

        def canonical(vertex_path, edge_path):
            return tuple(sorted(vertex_path)), tuple(sorted(edge_path, key=lambda x: (None in x, x)))

        expected_paths = [([(0, 0), (1, 1), (2, 2)], [((0, 1), (0, 1)), ((1, 2), (1, 2)), (None, (0, 2))]),
                          ([(0, 0), (1, 2), (2, 1)], [((0, 1), (0, 2)), ((1, 2), (1, 2)), (None, (0, 1))]),
                          ([(0, 1), (1, 0), (2, 2)], [((0, 1), (0, 1)), ((1, 2), (0, 2)), (None, (1, 2))]),
                          ([(0, 1), (1, 2), (2, 0)], [((0, 1), (1, 2)), ((1, 2), (0, 2)), (None, (0, 1))]),
                          ([(0, 2), (1, 0), (2, 1)], [((0, 1), (0, 2)), ((1, 2), (0, 1)), (None, (1, 2))]),
                          ([(0, 2), (1, 1), (2, 0)], [((0, 1), (1, 2)), ((1, 2), (0, 1)), (None, (0, 2))])]
        assert (set(canonical(*p) for p in paths) ==
                set(canonical(*p) for p in expected_paths))

    def test_optimize_graph_edit_distance(self):
        G1 = circular_ladder_graph(2)
        G2 = circular_ladder_graph(6)
        bestcost = 1000
        for cost in optimize_graph_edit_distance(G1, G2):
            assert cost < bestcost
            bestcost = cost
        assert bestcost == 22

    # def test_graph_edit_distance_bigger(self):
    #     G1 = circular_ladder_graph(12)
    #     G2 = circular_ladder_graph(16)
    #     assert_equal(graph_edit_distance(G1, G2), 22)

    def test_selfloops(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G1.add_edges_from((('A', 'A'), ('A', 'B')))
        G2 = nx.Graph()
        G2.add_edges_from((('A', 'B'), ('B', 'B')))
        G3 = nx.Graph()
        G3.add_edges_from((('A', 'A'), ('A', 'B'), ('B', 'B')))

        assert graph_edit_distance(G0, G0) == 0
        assert graph_edit_distance(G0, G1) == 4
        assert graph_edit_distance(G1, G0) == 4
        assert graph_edit_distance(G0, G2) == 4
        assert graph_edit_distance(G2, G0) == 4
        assert graph_edit_distance(G0, G3) == 5
        assert graph_edit_distance(G3, G0) == 5

        assert graph_edit_distance(G1, G1) == 0
        assert graph_edit_distance(G1, G2) == 0
        assert graph_edit_distance(G2, G1) == 0
        assert graph_edit_distance(G1, G3) == 1
        assert graph_edit_distance(G3, G1) == 1

        assert graph_edit_distance(G2, G2) == 0
        assert graph_edit_distance(G2, G3) == 1
        assert graph_edit_distance(G3, G2) == 1

        assert graph_edit_distance(G3, G3) == 0

    def test_digraph(self):
        G0 = nx.DiGraph()
        G1 = nx.DiGraph()
        G1.add_edges_from((('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')))
        G2 = nx.DiGraph()
        G2.add_edges_from((('A', 'B'), ('B', 'C'), ('C', 'D'), ('A', 'D')))
        G3 = nx.DiGraph()
        G3.add_edges_from((('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')))

        assert graph_edit_distance(G0, G0) == 0
        assert graph_edit_distance(G0, G1) == 8
        assert graph_edit_distance(G1, G0) == 8
        assert graph_edit_distance(G0, G2) == 8
        assert graph_edit_distance(G2, G0) == 8
        assert graph_edit_distance(G0, G3) == 8
        assert graph_edit_distance(G3, G0) == 8

        assert graph_edit_distance(G1, G1) == 0
        assert graph_edit_distance(G1, G2) == 2
        assert graph_edit_distance(G2, G1) == 2
        assert graph_edit_distance(G1, G3) == 4
        assert graph_edit_distance(G3, G1) == 4

        assert graph_edit_distance(G2, G2) == 0
        assert graph_edit_distance(G2, G3) == 2
        assert graph_edit_distance(G3, G2) == 2

        assert graph_edit_distance(G3, G3) == 0

    def test_multigraph(self):
        G0 = nx.MultiGraph()
        G1 = nx.MultiGraph()
        G1.add_edges_from((('A', 'B'), ('B', 'C'), ('A', 'C')))
        G2 = nx.MultiGraph()
        G2.add_edges_from((('A', 'B'), ('B', 'C'), ('B', 'C'), ('A', 'C')))
        G3 = nx.MultiGraph()
        G3.add_edges_from((('A', 'B'), ('B', 'C'), ('A', 'C'), ('A', 'C'), ('A', 'C')))

        assert graph_edit_distance(G0, G0) == 0
        assert graph_edit_distance(G0, G1) == 6
        assert graph_edit_distance(G1, G0) == 6
        assert graph_edit_distance(G0, G2) == 7
        assert graph_edit_distance(G2, G0) == 7
        assert graph_edit_distance(G0, G3) == 8
        assert graph_edit_distance(G3, G0) == 8

        assert graph_edit_distance(G1, G1) == 0
        assert graph_edit_distance(G1, G2) == 1
        assert graph_edit_distance(G2, G1) == 1
        assert graph_edit_distance(G1, G3) == 2
        assert graph_edit_distance(G3, G1) == 2

        assert graph_edit_distance(G2, G2) == 0
        assert graph_edit_distance(G2, G3) == 1
        assert graph_edit_distance(G3, G2) == 1

        assert graph_edit_distance(G3, G3) == 0

    def test_multidigraph(self):
        G1 = nx.MultiDiGraph()
        G1.add_edges_from((('hardware', 'kernel'), ('kernel', 'hardware'), ('kernel', 'userspace'), ('userspace', 'kernel')))
        G2 = nx.MultiDiGraph()
        G2.add_edges_from((('winter', 'spring'), ('spring', 'summer'), ('summer', 'autumn'), ('autumn', 'winter')))

        assert graph_edit_distance(G1, G2) == 5
        assert graph_edit_distance(G2, G1) == 5

    # by https://github.com/jfbeaumont
    def testCopy(self):
        G = nx.Graph()
        G.add_node('A', label='A')
        G.add_node('B', label='B')
        G.add_edge('A', 'B', label='a-b')
        assert graph_edit_distance(G, G.copy(), node_match=nmatch, edge_match=ematch) == 0

    def testSame(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_edge('A', 'B', label='a-b')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 0

    def testOneEdgeLabelDiff(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_edge('A', 'B', label='bad')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 1

    def testOneNodeLabelDiff(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='Z')
        G2.add_node('B', label='B')
        G2.add_edge('A', 'B', label='a-b')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 1

    def testOneExtraNode(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_node('C', label='C')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 1

    def testOneExtraEdge(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_node('C', label='C')
        G1.add_node('C', label='C')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('A', 'C', label='a-c')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 1

    def testOneExtraNodeAndEdge(self):
        G1 = nx.Graph()
        G1.add_node('A', label='A')
        G1.add_node('B', label='B')
        G1.add_edge('A', 'B', label='a-b')
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('A', 'C', label='a-c')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 2

    def testGraph1(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('D', label='D')
        G2.add_node('E', label='E')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('B', 'D', label='b-d')
        G2.add_edge('D', 'E', label='d-e')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 3

    def testGraph2(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_node('D', label='D')
        G2.add_node('E', label='E')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('B', 'C', label='b-c')
        G2.add_edge('C', 'D', label='c-d')
        G2.add_edge('C', 'E', label='c-e')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 4

    def testGraph3(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_node('D', label='D')
        G2.add_node('E', label='E')
        G2.add_node('F', label='F')
        G2.add_node('G', label='G')
        G2.add_edge('A', 'C', label='a-c')
        G2.add_edge('A', 'D', label='a-d')
        G2.add_edge('D', 'E', label='d-e')
        G2.add_edge('D', 'F', label='d-f')
        G2.add_edge('D', 'G', label='d-g')
        G2.add_edge('E', 'B', label='e-b')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 12

    def testGraph4(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_node('D', label='D')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('B', 'C', label='b-c')
        G2.add_edge('C', 'D', label='c-d')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 2

    def testGraph4_a(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_node('D', label='D')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('B', 'C', label='b-c')
        G2.add_edge('A', 'D', label='a-d')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 2

    def testGraph4_b(self):
        G1 = getCanonical()
        G2 = nx.Graph()
        G2.add_node('A', label='A')
        G2.add_node('B', label='B')
        G2.add_node('C', label='C')
        G2.add_node('D', label='D')
        G2.add_edge('A', 'B', label='a-b')
        G2.add_edge('B', 'C', label='b-c')
        G2.add_edge('B', 'D', label='bad')
        assert graph_edit_distance(G1, G2, node_match=nmatch, edge_match=ematch) == 1

    def test_simrank_no_source_no_target(self):
        G = nx.cycle_graph(5)
        expected = {0: {0: 1, 1: 0.3951219505902448, 2: 0.5707317069281646, 3: 0.5707317069281646, 4: 0.3951219505902449}, 1: {0: 0.3951219505902448, 1: 1, 2: 0.3951219505902449, 3: 0.5707317069281646, 4: 0.5707317069281646}, 2: {0: 0.5707317069281646, 1: 0.3951219505902449, 2: 1, 3: 0.3951219505902449, 4: 0.5707317069281646}, 3: {0: 0.5707317069281646, 1: 0.5707317069281646, 2: 0.3951219505902449, 3: 1, 4: 0.3951219505902449}, 4: {0: 0.3951219505902449, 1: 0.5707317069281646, 2: 0.5707317069281646, 3: 0.3951219505902449, 4: 1}}
        actual = nx.simrank_similarity(G)
        assert expected == actual

    def test_simrank_source_no_target(self):
        G = nx.cycle_graph(5)
        expected = {0: 1, 1: 0.3951219505902448, 2: 0.5707317069281646, 3: 0.5707317069281646, 4: 0.3951219505902449}
        actual = nx.simrank_similarity(G, source=0)
        assert expected == actual

    def test_simrank_source_and_target(self):
        G = nx.cycle_graph(5)
        expected = 1
        actual = nx.simrank_similarity(G, source=0, target=0)
        assert expected == actual

    def test_simrank_numpy_no_source_no_target(self):
        G = nx.cycle_graph(5)
        expected = numpy.array([
            [1.0, 0.3947180735764555, 0.570482097206368, 0.570482097206368, 0.3947180735764555],
            [0.3947180735764555, 1.0, 0.3947180735764555, 0.570482097206368, 0.570482097206368],
            [0.570482097206368, 0.3947180735764555, 1.0, 0.3947180735764555, 0.570482097206368],
            [0.570482097206368, 0.570482097206368, 0.3947180735764555, 1.0, 0.3947180735764555],
            [0.3947180735764555, 0.570482097206368, 0.570482097206368, 0.3947180735764555, 1.0]
        ])
        actual = nx.simrank_similarity_numpy(G)
        numpy.testing.assert_allclose(expected, actual, atol=1e-7)

    def test_simrank_numpy_source_no_target(self):
        G = nx.cycle_graph(5)
        expected = numpy.array(
            [1.0, 0.3947180735764555, 0.570482097206368, 0.570482097206368, 0.3947180735764555],
        )
        actual = nx.simrank_similarity_numpy(G, source=0)
        numpy.testing.assert_allclose(expected, actual, atol=1e-7)

    def test_simrank_numpy_source_and_target(self):
        G = nx.cycle_graph(5)
        expected = 1.0
        actual = nx.simrank_similarity_numpy(G, source=0, target=0)
        numpy.testing.assert_allclose(expected, actual, atol=1e-7)
