#!/usr/bin/env python

from random import Random
from unittest import TestCase

from nose.tools import *
import networkx


class TestDistance:

    def setUp(self):
        G = networkx.Graph()
        from networkx import convert_node_labels_to_integers as cnlti
        G = cnlti(networkx.grid_2d_graph(4, 4), first_label=1, ordering="sorted")
        self.G = G

    def test_eccentricity(self):
        assert_equal(networkx.eccentricity(self.G, 1), 6)
        e = networkx.eccentricity(self.G)
        assert_equal(e[1], 6)
        sp = dict(networkx.shortest_path_length(self.G))
        e = networkx.eccentricity(self.G, sp=sp)
        assert_equal(e[1], 6)
        e = networkx.eccentricity(self.G, v=1)
        assert_equal(e, 6)
        # This behavior changed in version 1.8 (ticket #739)
        e = networkx.eccentricity(self.G, v=[1, 1])
        assert_equal(e[1], 6)
        e = networkx.eccentricity(self.G, v=[1, 2])
        assert_equal(e[1], 6)
        # test against graph with one node
        G = networkx.path_graph(1)
        e = networkx.eccentricity(G)
        assert_equal(e[0], 0)
        e = networkx.eccentricity(G, v=0)
        assert_equal(e, 0)
        assert_raises(networkx.NetworkXError, networkx.eccentricity, G, 1)
        # test against empty graph
        G = networkx.empty_graph()
        e = networkx.eccentricity(G)
        assert_equal(e, {})

    def test_diameter(self):
        assert_equal(networkx.diameter(self.G), 6)

    def test_radius(self):
        assert_equal(networkx.radius(self.G), 4)

    def test_periphery(self):
        assert_equal(set(networkx.periphery(self.G)), set([1, 4, 13, 16]))

    def test_center(self):
        assert_equal(set(networkx.center(self.G)), set([6, 7, 10, 11]))

    def test_bound_diameter(self):
        assert_equal(networkx.diameter(self.G, usebounds=True), 6)

    def test_bound_radius(self):
        assert_equal(networkx.radius(self.G, usebounds=True), 4)

    def test_bound_periphery(self):
        assert_equal(set(networkx.periphery(self.G, usebounds=True)), set([1, 4, 13, 16]))

    def test_bound_center(self):
        assert_equal(set(networkx.center(self.G, usebounds=True)), set([6, 7, 10, 11]))

    def test_radius_exception(self):
        G = networkx.Graph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)
        assert_raises(networkx.NetworkXError, networkx.diameter, G)

    @raises(networkx.NetworkXError)
    def test_eccentricity_infinite(self):
        G = networkx.Graph([(1, 2), (3, 4)])
        e = networkx.eccentricity(G)

    @raises(networkx.NetworkXError)
    def test_eccentricity_undirected_not_connected(self):
        G = networkx.Graph([(1, 2), (3, 4)])
        e = networkx.eccentricity(G, sp=1)

    @raises(networkx.NetworkXError)
    def test_eccentricity_directed_weakly_connected(self):
        DG = networkx.DiGraph([(1, 2), (1, 3)])
        networkx.eccentricity(DG)


class TestBarycenter(TestCase):

    """Test :func:`networkx.algorithms.distance_measures.barycenter`."""

    def get_barycenter_as_subgraph(self, g, **kwargs):
        """Wrap :func:`networkx.barycenter` with :meth:`networkx.Graph.subgraph`.

        :meth:`get_barycenter_as_subgraph` asserts that
        :func:`networkx.barycenter` returns a :class:`list` of nodes contained
        in ``g``.
        """
        b = networkx.barycenter(g, **kwargs)
        self.assertIsInstance(b, list)
        self.assertLessEqual(set(b), set(g), "barycenter returned non-nodes")
        return g.subgraph(b)

    def test_must_be_connected(self):
        self.assertRaisesRegex(
            networkx.NetworkXNoPath, 'disconnected', networkx.barycenter,
            networkx.empty_graph(5))

    def test_sp_kwarg(self):
        # Complete graph K_5. Normally it works...
        K_5 = networkx.complete_graph(5)
        sp = dict(networkx.shortest_path_length(K_5))
        self.assertEqual(networkx.barycenter(K_5, sp=sp), list(K_5))
        # ...but not with the weight argument
        for u, v, data in K_5.edges.data():
            data['weight'] = 1
        self.assertRaisesRegex(
            ValueError, 'both.*(sp|weight).*(sp|weight)', networkx.barycenter,
            K_5, sp=sp, weight='weight')
        # ...and a corrupted sp can make it seem like K_5 is disconnected
        del sp[0][1]
        self.assertRaisesRegex(
            networkx.NetworkXNoPath, 'disconnected', networkx.barycenter, K_5,
            sp=sp)

    def test_trees(self):
        """The barycenter of a tree is a single vertex or an edge.

        See [West01]_, p. 78.
        """
        prng = Random(0xdeadbeef)
        for i in range(50):
            with self.subTest(trial=i):
                b = self.get_barycenter_as_subgraph(
                    networkx.random_tree(prng.randint(1, 75), prng))
                if len(b) == 2:
                    self.assertEqual(b.size(), 1)
                else:
                    self.assertEqual(len(b), 1)
                    self.assertEqual(b.size(), 0)

    def test_this_one_specific_tree(self):
        """Test the tree pictured at the bottom of [West01]_, p. 78."""
        g = networkx.Graph({
            'a': ['b'],
            'b': ['a', 'x'],
            'x': ['b', 'y'],
            'y': ['x', 'z'],
            'z': ['y', 0, 1, 2, 3, 4],
            0: ['z'], 1: ['z'], 2: ['z'], 3: ['z'], 4: ['z']})
        b = self.get_barycenter_as_subgraph(g, attr='barycentricity')
        self.assertEqual(list(b), ['z'])
        self.assertFalse(b.edges)
        expected_barycentricity = {
            0: 23, 1: 23, 2: 23, 3: 23, 4: 23, 'a': 35, 'b': 27, 'x': 21,
            'y': 17, 'z': 15
        }
        for node, barycentricity in expected_barycentricity.items():
            self.assertEqual(g.nodes[node]['barycentricity'], barycentricity)

        # Doubling weights should do nothing but double the barycentricities
        for edge in g.edges:
            g.edges[edge]['weight'] = 2
        b = self.get_barycenter_as_subgraph(
            g, weight='weight', attr='barycentricity2')
        self.assertEqual(list(b), ['z'])
        self.assertFalse(b.edges)
        for node, barycentricity in expected_barycentricity.items():
            self.assertEqual(
                g.nodes[node]['barycentricity2'], barycentricity*2)
