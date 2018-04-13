from unittest import TestCase
from numpy.random import RandomState

import networkx


class TestBarycenter(TestCase):

	"""Test ``barycenter``.

	Refernces to West (2000) refer to the citation in ``barycenter``'s
	docstring.
	"""

	def test_must_be_connected(self):
		self.assertRaises(
			networkx.NetworkXNoPath, networkx.barycenter, networkx.empty_graph(5))

	@staticmethod
	def random_tree(n, prng):
		"""Return a uniformly random tree on `n` nodes.

		Code copied from networkx.random_tree, version 2.1. The problem with
		NetworkX's version of this function is that it modifies the global seed
		on every call, making it difficult to get a consistent, random sample
		from run to run.

		prng should be a NumPy `RandomState`.
		"""
		if n == 0:
			raise networkx.NetworkXPointlessConcept('the null graph is not a tree')
		if n == 1:
			return networkx.empty_graph(1)
		return networkx.from_prufer_sequence(prng.choice(n, n - 1))

	def test_trees(self):
		"""The barycenter of a tree is a single vertex or an edge.

		West (2000), p. 78.
		"""
		# random_tree is fast, but barycenter is slow, so use fewer nodes.
		prng, avg_order, trials = RandomState(0xdeadbeef), 25, 100
		for i in range(trials):
			with self.subTest(i):
				b = networkx.barycenter(self.random_tree(prng.poisson(avg_order), prng))
				if len(b) == 2:
					self.assertEqual(b.size(), 1)
				else:
					self.assertEqual(len(b), 1)
					self.assertEqual(b.size(), 0)

	def test_this_one_specific_tree(self):
		"Test the tree pictured at the bottom of West (2000), p. 78."
		g = networkx.Graph({
			'a': ['b'],
			'b': ['a', 'x'],
			'x': ['b', 'y'],
			'y': ['x', 'z'],
			'z': ['y', 0, 1, 2, 3, 4],
			0: ['z'], 1: ['z'], 2: ['z'], 3: ['z'], 4: ['z']})
		b = networkx.barycenter(g)
		self.assertEqual(list(b), ['z'])
		self.assertFalse(b.edges)
		expected_barycentricity = {
			0: 23, 1: 23, 2: 23, 3: 23, 4: 23, 'a': 35, 'b': 27, 'x': 21,
			'y': 17, 'z': 15
		}
		for node, barycentricity in expected_barycentricity.items():
			self.assertEqual(g.nodes[node]['barycentricity'], barycentricity)

		# Doubling the weights should do nothing but double the barycentricities
		for edge in g.edges:
			g.edges[edge]['weight'] = 2
		b = networkx.barycenter(g, 'weight')
		self.assertEqual(list(b), ['z'])
		self.assertFalse(b.edges)
		for node, barycentricity in expected_barycentricity.items():
			self.assertEqual(g.nodes[node]['barycentricity'], barycentricity*2)
