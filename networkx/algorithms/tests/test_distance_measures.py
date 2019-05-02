#!/usr/bin/env python
from random import Random
from nose.tools import assert_equal, assert_is_instance, \
        assert_raises, raises, assert_less_equal, assert_false

import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti


class TestDistance:
    def setUp(self):
        G = cnlti(nx.grid_2d_graph(4, 4), first_label=1, ordering="sorted")
        self.G = G

    def test_eccentricity(self):
        assert_equal(nx.eccentricity(self.G, 1), 6)
        e = nx.eccentricity(self.G)
        assert_equal(e[1], 6)

        sp = dict(nx.shortest_path_length(self.G))
        e = nx.eccentricity(self.G, sp=sp)
        assert_equal(e[1], 6)

        e = nx.eccentricity(self.G, v=1)
        assert_equal(e, 6)

        # This behavior changed in version 1.8 (ticket #739)
        e = nx.eccentricity(self.G, v=[1, 1])
        assert_equal(e[1], 6)
        e = nx.eccentricity(self.G, v=[1, 2])
        assert_equal(e[1], 6)

        # test against graph with one node
        G = nx.path_graph(1)
        e = nx.eccentricity(G)
        assert_equal(e[0], 0)
        e = nx.eccentricity(G, v=0)
        assert_equal(e, 0)
        assert_raises(nx.NetworkXError, nx.eccentricity, G, 1)

        # test against empty graph
        G = nx.empty_graph()
        e = nx.eccentricity(G)
        assert_equal(e, {})

    def test_diameter(self):
        assert_equal(nx.diameter(self.G), 6)

    def test_radius(self):
        assert_equal(nx.radius(self.G), 4)

    def test_periphery(self):
        assert_equal(set(nx.periphery(self.G)), set([1, 4, 13, 16]))

    def test_center(self):
        assert_equal(set(nx.center(self.G)), set([6, 7, 10, 11]))

    def test_bound_diameter(self):
        assert_equal(nx.diameter(self.G, usebounds=True), 6)

    def test_bound_radius(self):
        assert_equal(nx.radius(self.G, usebounds=True), 4)

    def test_bound_periphery(self):
        result = set([1, 4, 13, 16])
        assert_equal(set(nx.periphery(self.G, usebounds=True)), result)

    def test_bound_center(self):
        result = set([6, 7, 10, 11])
        assert_equal(set(nx.center(self.G, usebounds=True)), result)

    def test_radius_exception(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)
        assert_raises(nx.NetworkXError, nx.diameter, G)

    @raises(nx.NetworkXError)
    def test_eccentricity_infinite(self):
        G = nx.Graph([(1, 2), (3, 4)])
        e = nx.eccentricity(G)

    @raises(nx.NetworkXError)
    def test_eccentricity_undirected_not_connected(self):
        G = nx.Graph([(1, 2), (3, 4)])
        e = nx.eccentricity(G, sp=1)

    @raises(nx.NetworkXError)
    def test_eccentricity_directed_weakly_connected(self):
        DG = nx.DiGraph([(1, 2), (1, 3)])
        nx.eccentricity(DG)


class TestBarycenter(object):
    """Test :func:`networkx.algorithms.distance_measures.barycenter`."""
    def barycenter_as_subgraph(self, g, **kwargs):
        """Return the subgraph induced on the barycenter of g"""
        b = nx.barycenter(g, **kwargs)
        assert_is_instance(b, list)
        assert_less_equal(set(b), set(g))
        return g.subgraph(b)

    def test_must_be_connected(self):
        assert_raises(nx.NetworkXNoPath, nx.barycenter, nx.empty_graph(5))

    def test_sp_kwarg(self):
        # Complete graph K_5. Normally it works...
        K_5 = nx.complete_graph(5)
        sp = dict(nx.shortest_path_length(K_5))
        assert_equal(nx.barycenter(K_5, sp=sp), list(K_5))

        # ...but not with the weight argument
        for u, v, data in K_5.edges.data():
            data['weight'] = 1
        assert_raises(ValueError, nx.barycenter, K_5, sp=sp, weight='weight')

        # ...and a corrupted sp can make it seem like K_5 is disconnected
        del sp[0][1]
        assert_raises(nx.NetworkXNoPath, nx.barycenter, K_5, sp=sp)

    def test_trees(self):
        """The barycenter of a tree is a single vertex or an edge.

        See [West01]_, p. 78.
        """
        prng = Random(0xdeadbeef)
        for i in range(50):
            RT = nx.random_tree(prng.randint(1, 75), prng)
            b = self.barycenter_as_subgraph(RT)
            if len(b) == 2:
                assert_equal(b.size(), 1)
            else:
                assert_equal(len(b), 1)
                assert_equal(b.size(), 0)

    def test_this_one_specific_tree(self):
        """Test the tree pictured at the bottom of [West01]_, p. 78."""
        g = nx.Graph({
            'a': ['b'],
            'b': ['a', 'x'],
            'x': ['b', 'y'],
            'y': ['x', 'z'],
            'z': ['y', 0, 1, 2, 3, 4],
            0: ['z'], 1: ['z'], 2: ['z'], 3: ['z'], 4: ['z']})
        b = self.barycenter_as_subgraph(g, attr='barycentricity')
        assert_equal(list(b), ['z'])
        assert_false(b.edges)
        expected_barycentricity = {0: 23, 1: 23, 2: 23, 3: 23, 4: 23,
                                   'a': 35, 'b': 27, 'x': 21, 'y': 17, 'z': 15
                                   }
        for node, barycentricity in expected_barycentricity.items():
            assert_equal(g.nodes[node]['barycentricity'], barycentricity)

        # Doubling weights should do nothing but double the barycentricities
        for edge in g.edges:
            g.edges[edge]['weight'] = 2
        b = self.barycenter_as_subgraph(g, weight='weight',
                                        attr='barycentricity2')
        assert_equal(list(b), ['z'])
        assert_false(b.edges)
        for node, barycentricity in expected_barycentricity.items():
            assert_equal(g.nodes[node]['barycentricity2'], barycentricity*2)
