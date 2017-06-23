#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti


def to_directed(G):
    """Convert an undirected graph to a directed one, alternating converting
    undirected edges to directed edges in either or both directions.
    """
    DG = nx.DiGraph()

    for i, (n1, n2) in enumerate(G.edges()):
        # Alternate converting undirected edges to directed in either or
        # both directions
        if i % 3 != 0:
            DG.add_edge(n1, n2)
        if i % 3 != 1:
            DG.add_edge(n2, n1)

    return DG


class TestConnected:

    def setUp(self):
        # Create union of three separate undirected graphs
        components = [
            nx.grid_2d_graph(2, 2),
            nx.lollipop_graph(3, 3),
            nx.house_graph()
        ]
        self.G = nx.Graph()
        self.G_components = set()
        for c in components:
            c = cnlti(c, first_label=len(self.G) + 1, ordering="sorted")
            self.G = nx.union(self.G, c)
            self.G_components.add(frozenset(c.nodes()))

        # A larger connected grid
        self.grid = cnlti(nx.grid_2d_graph(4, 4), first_label=1)

        self.gc = []
        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (2, 8), (3, 4), (3, 7), (4, 5),
                          (5, 3), (5, 6), (7, 4), (7, 6), (8, 1), (8, 7)])
        C = [[3, 4, 5, 7], [1, 2, 8], [6]]
        self.gc.append((G, C))

        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (1, 3), (1, 4), (4, 2), (3, 4), (2, 3)])
        C = [[2, 3, 4],[1]]
        self.gc.append((G, C))

        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 2), (2, 1)])
        C = [[1, 2, 3]]
        self.gc.append((G,C))

        # Eppstein's tests
        G = nx.DiGraph({0:[1], 1:[2, 3], 2:[4, 5], 3:[4, 5], 4:[6], 5:[], 6:[]})
        C = [[0], [1], [2],[ 3], [4], [5], [6]]
        self.gc.append((G,C))

        G = nx.DiGraph({0:[1], 1:[2, 3, 4], 2:[0, 3], 3:[4], 4:[3]})
        C = [[0, 1, 2], [3, 4]]
        self.gc.append((G, C))


    def test_connected_components(self):
        cc = nx.connected_components
        G = self.G
        C = self.G_components
        assert_equal({frozenset(g) for g in cc(G)}, C)
        assert_equal({frozenset(g) for g in cc(to_directed(G))}, C)

    def test_number_connected_components(self):
        ncc = nx.number_connected_components
        assert_equal(ncc(self.G), len(self.G_components))
        assert_equal(ncc(to_directed(self.G)), len(self.G_components))

    def test_number_connected_components2(self):
        ncc = nx.number_connected_components
        G = self.grid
        assert_equal(ncc(G), 1)
        assert_equal(ncc(to_directed(G)), 1)

    def test_connected_components2(self):
        cc = nx.connected_components
        G = self.grid
        C = {frozenset(G.nodes())}
        assert_equal({frozenset(g) for g in cc(G)}, C)
        assert_equal({frozenset(g) for g in cc(to_directed(G))}, C)

    def test_node_connected_components(self):
        ncc = nx.node_connected_component
        G = self.grid
        C = set(G.nodes())
        assert_equal(ncc(G, 1), C)

    def test_connected_component_subgraphs(self):
        wcc = nx.weakly_connected_component_subgraphs
        cc = nx.connected_component_subgraphs
        for G, C in self.gc:
            U = G.to_undirected()
            w = {frozenset(g) for g in wcc(G)}
            c = {frozenset(g) for g in cc(U)}
            assert_equal(w, c)
            d = {frozenset(g) for g in cc(G)}
            assert_equal(c, d)

    def test_is_connected(self):
        assert_true(nx.is_connected(self.grid))
        assert_true(nx.is_connected(to_directed(self.grid)))

        G = nx.Graph()
        G.add_nodes_from([1, 2])
        assert_false(nx.is_connected(G))
        assert_false(nx.is_connected(G.to_directed()))

    def test_connected_raise(self):
        assert_raises(nx.NetworkXPointlessConcept, nx.is_connected, nx.Graph())
