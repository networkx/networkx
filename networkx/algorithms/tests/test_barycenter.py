from random import Random
from unittest import TestCase

import networkx


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
