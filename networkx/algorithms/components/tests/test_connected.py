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
        ccs = nx.connected_component_subgraphs
        G = self.G
        C = self.G_components
        assert_equal({frozenset(g.nodes()) for g in ccs(G)}, C)
        assert_equal({frozenset(g.nodes()) for g in ccs(to_directed(G))}, C)

    def test_is_connected(self):
        assert_true(nx.is_connected(self.grid))
        assert_true(nx.is_connected(to_directed(self.grid)))

        G = nx.Graph()
        G.add_nodes_from([1, 2])
        assert_false(nx.is_connected(G))
        assert_false(nx.is_connected(G.to_directed()))

    def test_connected_raise(self):
        assert_raises(nx.NetworkXPointlessConcept, nx.is_connected, nx.Graph())
