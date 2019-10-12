# -*- encoding: utf-8 -*-
# test_random_graphs.py - unit tests for random graph generators
#
# Copyright 2010-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.random_graphs` module.

"""
import pytest

from networkx.exception import NetworkXError
from networkx.generators.random_graphs import barabasi_albert_graph
from networkx.generators.random_graphs import dual_barabasi_albert_graph
from networkx.generators.random_graphs import extended_barabasi_albert_graph
from networkx.generators.random_graphs import binomial_graph
from networkx.generators.random_graphs import connected_watts_strogatz_graph
from networkx.generators.random_graphs import dense_gnm_random_graph
from networkx.generators.random_graphs import erdos_renyi_graph
from networkx.generators.random_graphs import fast_gnp_random_graph
from networkx.generators.random_graphs import gnm_random_graph
from networkx.generators.random_graphs import gnp_random_graph
from networkx.generators.random_graphs import newman_watts_strogatz_graph
from networkx.generators.random_graphs import powerlaw_cluster_graph
from networkx.generators.random_graphs import random_kernel_graph
from networkx.generators.random_graphs import random_lobster
from networkx.generators.random_graphs import random_powerlaw_tree
from networkx.generators.random_graphs import random_powerlaw_tree_sequence
from networkx.generators.random_graphs import random_regular_graph
from networkx.generators.random_graphs import random_shell_graph
from networkx.generators.random_graphs import watts_strogatz_graph


class TestGeneratorsRandom(object):

    def smoke_test_random_graph(self):
        seed = 42
        G = gnp_random_graph(100, 0.25, seed)
        G = gnp_random_graph(100, 0.25, seed, directed=True)
        G = binomial_graph(100, 0.25, seed)
        G = erdos_renyi_graph(100, 0.25, seed)
        G = fast_gnp_random_graph(100, 0.25, seed)
        G = fast_gnp_random_graph(100, 0.25, seed, directed=True)
        G = gnm_random_graph(100, 20, seed)
        G = gnm_random_graph(100, 20, seed, directed=True)
        G = dense_gnm_random_graph(100, 20, seed)

        G = watts_strogatz_graph(10, 2, 0.25, seed)
        assert len(G) == 10
        assert G.number_of_edges() == 10

        G = connected_watts_strogatz_graph(10, 2, 0.1, tries=10, seed=seed)
        assert len(G) == 10
        assert G.number_of_edges() == 10
        pytest.raises(NetworkXError, connected_watts_strogatz_graph, \
                      10, 2, 0.1, tries=0)

        G = watts_strogatz_graph(10, 4, 0.25, seed)
        assert len(G) == 10
        assert G.number_of_edges() == 20

        G = newman_watts_strogatz_graph(10, 2, 0.0, seed)
        assert len(G) == 10
        assert G.number_of_edges() == 10

        G = newman_watts_strogatz_graph(10, 4, 0.25, seed)
        assert len(G) == 10
        assert G.number_of_edges() >= 20

        G = barabasi_albert_graph(100, 1, seed)
        G = barabasi_albert_graph(100, 3, seed)
        assert G.number_of_edges() == (97 * 3)

        G = extended_barabasi_albert_graph(100, 1, 0, 0, seed)
        assert G.number_of_edges() == 99
        G = extended_barabasi_albert_graph(100, 3, 0, 0, seed)
        assert G.number_of_edges() == 97 * 3
        G = extended_barabasi_albert_graph(100, 1, 0, 0.5, seed)
        assert G.number_of_edges() == 99
        G = extended_barabasi_albert_graph(100, 2, 0.5, 0, seed)
        assert G.number_of_edges() > 100 * 3
        assert G.number_of_edges() < 100 * 4

        G = extended_barabasi_albert_graph(100, 2, 0.3, 0.3, seed)
        assert G.number_of_edges() > 100 * 2
        assert G.number_of_edges() < 100 * 4

        G = powerlaw_cluster_graph(100, 1, 1.0, seed)
        G = powerlaw_cluster_graph(100, 3, 0.0, seed)
        assert G.number_of_edges() == (97 * 3)

        G = random_regular_graph(10, 20, seed)

        pytest.raises(NetworkXError, random_regular_graph, 3, 21)
        pytest.raises(NetworkXError, random_regular_graph, 33, 21)

        constructor = [(10, 20, 0.8), (20, 40, 0.8)]
        G = random_shell_graph(constructor, seed)

        G = random_lobster(10, 0.1, 0.5, seed)

        # difficult to find seed that requires few tries
        seq = random_powerlaw_tree_sequence(10, 3, seed=14, tries=1)
        G = random_powerlaw_tree(10, 3, seed=14, tries=1)

    def test_dual_barabasi_albert(self, m1=1, m2=4, p=0.5):
        """
        Tests that the dual BA random graph generated behaves consistently.

        Tests the exceptions are raised as expected.

        The graphs generation are repeated several times to prevent lucky shots

        """
        seed = 42
        repeats = 2

        while repeats:
            repeats -= 1

            # This should be BA with m = m1
            BA1 = barabasi_albert_graph(100, m1, seed)
            DBA1 = dual_barabasi_albert_graph(100, m1, m2, 1, seed)
            assert BA1.size() == DBA1.size()

            # This should be BA with m = m2
            BA2 = barabasi_albert_graph(100, m2, seed)
            DBA2 = dual_barabasi_albert_graph(100, m1, m2, 0, seed)
            assert BA2.size() == DBA2.size()

        # Testing exceptions
        dbag = dual_barabasi_albert_graph
        pytest.raises(NetworkXError, dbag, m1, m1, m2, 0)
        pytest.raises(NetworkXError, dbag, m2, m1, m2, 0)
        pytest.raises(NetworkXError, dbag, 100, m1, m2, -0.5)
        pytest.raises(NetworkXError, dbag, 100, m1, m2, 1.5)

    def test_extended_barabasi_albert(self, m=2):
        """
        Tests that the extended BA random graph generated behaves consistently.

        Tests the exceptions are raised as expected.

        The graphs generation are repeated several times to prevent lucky-shots

        """
        seed = 42
        repeats = 2
        BA_model = barabasi_albert_graph(100, m, seed)
        BA_model_edges = BA_model.number_of_edges()

        while repeats:
            repeats -= 1

            # This behaves just like BA, the number of edges must be the same
            G1 = extended_barabasi_albert_graph(100, m, 0, 0, seed)
            assert G1.size() == BA_model_edges

            # More than twice more edges should have been added
            G1 = extended_barabasi_albert_graph(100, m, 0.8, 0, seed)
            assert G1.size() > BA_model_edges * 2

            # Only edge rewiring, so the number of edges less than original
            G2 = extended_barabasi_albert_graph(100, m, 0, 0.8, seed)
            assert G2.size() == BA_model_edges

            # Mixed scenario: less edges than G1 and more edges than G2
            G3 = extended_barabasi_albert_graph(100, m, 0.3, 0.3, seed)
            assert G3.size() > G2.size()
            assert G3.size() < G1.size()

        # Testing exceptions
        ebag = extended_barabasi_albert_graph
        pytest.raises(NetworkXError, ebag, m, m, 0, 0)
        pytest.raises(NetworkXError, ebag, 1, 0.5, 0, 0)
        pytest.raises(NetworkXError, ebag, 100, 2, 0.5, 0.5)

    def test_random_zero_regular_graph(self):
        """Tests that a 0-regular graph has the correct number of nodes and
        edges.

        """
        seed = 42
        G = random_regular_graph(0, 10, seed)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 0

    def test_gnp(self):
        for generator in [gnp_random_graph, binomial_graph, erdos_renyi_graph,
                          fast_gnp_random_graph]:
            G = generator(10, -1.1)
            assert len(G) == 10
            assert sum(1 for _ in G.edges()) == 0

            G = generator(10, 0.1)
            assert len(G) == 10

            G = generator(10, 0.1, seed=42)
            assert len(G) == 10

            G = generator(10, 1.1)
            assert len(G) == 10
            assert sum(1 for _ in G.edges()) == 45

            G = generator(10, -1.1, directed=True)
            assert G.is_directed()
            assert len(G) == 10
            assert sum(1 for _ in G.edges()) == 0

            G = generator(10, 0.1, directed=True)
            assert G.is_directed()
            assert len(G) == 10

            G = generator(10, 1.1, directed=True)
            assert G.is_directed()
            assert len(G) == 10
            assert sum(1 for _ in G.edges()) == 90

            # assert that random graphs generate all edges for p close to 1
            edges = 0
            runs = 100
            for i in range(runs):
                edges += sum(1 for _ in generator(10, 0.99999, directed=True).edges())
            assert abs(edges / float(runs) - 90) <= runs * 2.0 / 100

    def test_gnm(self):
        G = gnm_random_graph(10, 3)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 3

        G = gnm_random_graph(10, 3, seed=42)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 3

        G = gnm_random_graph(10, 100)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 45

        G = gnm_random_graph(10, 100, directed=True)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 90

        G = gnm_random_graph(10, -1.1)
        assert len(G) == 10
        assert sum(1 for _ in G.edges()) == 0

    def test_watts_strogatz_big_k(self):
        #Test to make sure than n <= k
        pytest.raises(NetworkXError, watts_strogatz_graph, 10, 11, 0.25)
        pytest.raises(NetworkXError, newman_watts_strogatz_graph, 10, 11, 0.25)
        
        # could create an infinite loop, now doesn't
        # infinite loop used to occur when a node has degree n-1 and needs to rewire
        watts_strogatz_graph(10, 9, 0.25, seed=0)
        newman_watts_strogatz_graph(10, 9, 0.5, seed=0)

        #Test k==n scenario
        watts_strogatz_graph(10, 10, 0.25, seed=0)
        newman_watts_strogatz_graph(10, 10, 0.25, seed=0)

    def test_random_kernel_graph(self):
        def integral(u, w, z):
            return c * (z - w)

        def root(u, w, r):
            return r / c + w
        c = 1
        graph = random_kernel_graph(1000, integral, root)
        graph = random_kernel_graph(1000, integral, root, seed=42)
        assert len(graph) == 1000
