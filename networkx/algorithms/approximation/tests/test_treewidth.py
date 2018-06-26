# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Rudolf-Andreas Floren <rudi.floren@gmail.com>
#    Dominik Meier <dominik.meier@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
import networkx as nx
from nose.tools import assert_equals, ok_
from networkx.algorithms.approximation import treewidth_min_degree
from networkx.algorithms.approximation import treewidth_min_fill_in
from networkx.algorithms.approximation.treewidth import min_fill_in_heuristic
from networkx.algorithms.approximation.treewidth import MinDegreeHeuristic
import itertools


def is_tree_decomp(graph, decomp):
    """Check if the given tree decomposition is valid."""
    for x in graph.nodes():
        appear_once = False
        for bag in decomp.nodes():
            if x in bag:
                appear_once = True
                break
        ok_(appear_once)

    # Check if each connected pair of nodes are at least once together in a bag
    for (x, y) in graph.edges():
        appear_together = False
        for bag in decomp.nodes():
            if x in bag and y in bag:
                appear_together = True
                break
        ok_(appear_together)

    # Check if the nodes associated with vertex v form a connected subset of T
    for v in graph.nodes():
        subset = []
        for bag in decomp.nodes():
            if v in bag:
                subset.append(bag)
        sub_graph = decomp.subgraph(subset)
        ok_(nx.is_connected(sub_graph))


class TestTreewidthMinDegree(object):
    """Unit tests for the min_degree function"""
    def setUp(self):
        """Setup for different kinds of trees"""
        self.complete = nx.Graph()
        self.complete.add_edge(1, 2)
        self.complete.add_edge(2, 3)
        self.complete.add_edge(1, 3)

        self.small_tree = nx.Graph()
        self.small_tree.add_edge(1, 3)
        self.small_tree.add_edge(4, 3)
        self.small_tree.add_edge(2, 3)
        self.small_tree.add_edge(3, 5)
        self.small_tree.add_edge(5, 6)
        self.small_tree.add_edge(5, 7)
        self.small_tree.add_edge(6, 7)

        self.deterministic_graph = nx.Graph()
        self.deterministic_graph.add_edge(0, 1)  # deg(0) = 1

        self.deterministic_graph.add_edge(1, 2)  # deg(1) = 2

        self.deterministic_graph.add_edge(2, 3)
        self.deterministic_graph.add_edge(2, 4)  # deg(2) = 3

        self.deterministic_graph.add_edge(3, 4)
        self.deterministic_graph.add_edge(3, 5)
        self.deterministic_graph.add_edge(3, 6)  # deg(3) = 4

        self.deterministic_graph.add_edge(4, 5)
        self.deterministic_graph.add_edge(4, 6)
        self.deterministic_graph.add_edge(4, 7)  # deg(4) = 5

        self.deterministic_graph.add_edge(5, 6)
        self.deterministic_graph.add_edge(5, 7)
        self.deterministic_graph.add_edge(5, 8)
        self.deterministic_graph.add_edge(5, 9)  # deg(5) = 6

        self.deterministic_graph.add_edge(6, 7)
        self.deterministic_graph.add_edge(6, 8)
        self.deterministic_graph.add_edge(6, 9)  # deg(6) = 6

        self.deterministic_graph.add_edge(7, 8)
        self.deterministic_graph.add_edge(7, 9)  # deg(7) = 5

        self.deterministic_graph.add_edge(8, 9)  # deg(8) = 4

    def test_petersen_graph(self):
        """Test Petersen graph tree decomposition result"""
        G = nx.petersen_graph()
        _, decomp = treewidth_min_degree(G)
        is_tree_decomp(G, decomp)

    def test_small_tree_treewidth(self):
        """Test small tree

        Test if the computed treewidth of the known self.small_tree is 2.
        As we know which value we can expect from our heuristic, values other
        than two are regressions
        """
        G = self.small_tree
        # the order of removal should be [1,2,4]3[5,6,7]
        # (with [] denoting any order of the containing nodes)
        # resulting in treewidth 2 for the heuristic
        treewidth, _ = treewidth_min_fill_in(G)
        assert_equals(treewidth, 2)

    def test_heuristic_abort(self):
        """Test heuristic abort condition for fully connected graph"""
        graph = {}
        for u in self.complete:
            graph[u] = set()
            for v in self.complete[u]:
                if u != v:  # ignore self-loop
                    graph[u].add(v)

        deg_heuristic = MinDegreeHeuristic(graph)
        node = deg_heuristic.best_node(graph)
        if node is None:
            pass
        else:
            assert False

    def test_empty_graph(self):
        """Test empty graph"""
        G = nx.Graph()
        _, _ = treewidth_min_degree(G)

    def test_two_component_graph(self):
        """Test empty graph"""
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        treewidth, _ = treewidth_min_degree(G)
        assert_equals(treewidth, 0)

    def test_heuristic_first_steps(self):
        """Test first steps of min_degree heuristic"""
        graph = {n: set(self.deterministic_graph[n]) - set([n])
                 for n in self.deterministic_graph}
        deg_heuristic = MinDegreeHeuristic(graph)
        elim_node = deg_heuristic.best_node(graph)
        print("Graph {}:".format(graph))
        steps = []

        while elim_node is not None:
            print("Removing {}:".format(elim_node))
            steps.append(elim_node)
            nbrs = graph[elim_node]

            for u, v in itertools.permutations(nbrs, 2):
                if v not in graph[u]:
                    graph[u].add(v)

            for u in graph:
                if elim_node in graph[u]:
                    graph[u].remove(elim_node)

            del graph[elim_node]
            print("Graph {}:".format(graph))
            elim_node = deg_heuristic.best_node(graph)

        # check only the first 5 elements for equality
        assert_equals(steps[:5], [0, 1, 2, 3, 4])


class TestTreewidthMinFillIn(object):
    """Unit tests for the treewidth_min_fill_in function."""
    def setUp(self):
        """Setup for different kinds of trees"""
        self.complete = nx.Graph()
        self.complete.add_edge(1, 2)
        self.complete.add_edge(2, 3)
        self.complete.add_edge(1, 3)

        self.small_tree = nx.Graph()
        self.small_tree.add_edge(1, 2)
        self.small_tree.add_edge(2, 3)
        self.small_tree.add_edge(3, 4)
        self.small_tree.add_edge(1, 4)
        self.small_tree.add_edge(2, 4)
        self.small_tree.add_edge(4, 5)
        self.small_tree.add_edge(5, 6)
        self.small_tree.add_edge(5, 7)
        self.small_tree.add_edge(6, 7)

        self.deterministic_graph = nx.Graph()
        self.deterministic_graph.add_edge(1, 2)
        self.deterministic_graph.add_edge(1, 3)
        self.deterministic_graph.add_edge(3, 4)
        self.deterministic_graph.add_edge(2, 4)
        self.deterministic_graph.add_edge(3, 5)
        self.deterministic_graph.add_edge(4, 5)
        self.deterministic_graph.add_edge(3, 6)
        self.deterministic_graph.add_edge(5, 6)

    def test_petersen_graph(self):
        """Test Petersen graph tree decomposition result"""
        G = nx.petersen_graph()
        _, decomp = treewidth_min_fill_in(G)
        is_tree_decomp(G, decomp)

    def test_small_tree_treewidth(self):
        """Test if the computed treewidth of the known self.small_tree is 2"""
        G = self.small_tree
        # the order of removal should be [1,2,4]3[5,6,7]
        # (with [] denoting any order of the containing nodes)
        # resulting in treewidth 2 for the heuristic
        treewidth, _ = treewidth_min_fill_in(G)
        assert_equals(treewidth, 2)

    def test_heuristic_abort(self):
        """Test if min_fill_in returns None for fully connected graph"""
        graph = {}
        for u in self.complete:
            graph[u] = set()
            for v in self.complete[u]:
                if u != v:  # ignore self-loop
                    graph[u].add(v)
        next_node = min_fill_in_heuristic(graph)
        if next_node is None:
            pass
        else:
            assert False

    def test_empty_graph(self):
        """Test empty graph"""
        G = nx.Graph()
        _, _ = treewidth_min_fill_in(G)

    def test_two_component_graph(self):
        """Test empty graph"""
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        treewidth, _ = treewidth_min_fill_in(G)
        assert_equals(treewidth, 0)

    def test_heuristic_first_steps(self):
        """Test first steps of min_fill_in heuristic"""
        graph = {n: set(self.deterministic_graph[n]) - set([n])
                 for n in self.deterministic_graph}
        print("Graph {}:".format(graph))
        elim_node = min_fill_in_heuristic(graph)
        steps = []

        while elim_node is not None:
            print("Removing {}:".format(elim_node))
            steps.append(elim_node)
            nbrs = graph[elim_node]

            for u, v in itertools.permutations(nbrs, 2):
                if v not in graph[u]:
                    graph[u].add(v)

            for u in graph:
                if elim_node in graph[u]:
                    graph[u].remove(elim_node)

            del graph[elim_node]
            print("Graph {}:".format(graph))
            elim_node = min_fill_in_heuristic(graph)

        # check only the first 2 elements for equality
        assert_equals(steps[:2], [6, 5])
