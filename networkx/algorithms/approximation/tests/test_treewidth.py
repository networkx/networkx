#-*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Rudolf-Andreas Floren <rudi.floren@gmail.com>
#    Dominik Meier <dominik.meier@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
import networkx as nx
from nose.tools import assert_equals, assert_is_none
from nose.tools import ok_
from networkx.algorithms.approximation import treewidth_min_degree
from networkx.algorithms.approximation import treewidth_min_fill_in
from networkx.algorithms.approximation.treewidth import MinFillInHeuristic
from networkx.algorithms.approximation.treewidth import MinDegreeHeuristic
"""Unit tests for the :mod:`networkx.algorithms.approximation.treewidth`
module.

"""


def is_tree_decomp(graph, decomp):
    """Check if the given decomposition tree is a decomposition tree of the given graph"""
    for x in graph.nodes():
        appearOnce = False
        for bag in decomp.nodes():
            if x in bag:
                appearOnce = True
                break
        ok_(appearOnce)

    # Check if each connected pair of nodes appears at least once together in a bag
    for (x, y) in graph.edges():
        appearTogether = False
        for bag in decomp.nodes():
            if x in bag and y in bag:
                appearTogether = True
                break
        ok_(appearTogether)

    # Check if the nodes associated with vertex v form a connected subset of T
    for v in graph.nodes():
        subset = []
        for bag in decomp.nodes():
            if (v in bag):
                subset.append(bag)
        subGraph = decomp.subgraph(subset)
        ok_(nx.is_connected(subGraph))


class TestTreewidthMinDegree(object):
    """Unit tests for the :mod:`networkx.algorithms.approximation.treewidth_min_degree`
    function.

    """

    def setUp(self):
        """Setup for different kinds of trees"""
        self.complete = nx.Graph()
        self.complete.add_edge(1, 2)
        self.complete.add_edge(2, 3)
        self.complete.add_edge(1, 3)

        self.smallTree = nx.Graph()
        self.smallTree.add_edge(1, 3)
        self.smallTree.add_edge(4, 3)
        self.smallTree.add_edge(2, 3)
        self.smallTree.add_edge(3, 5)
        self.smallTree.add_edge(5, 6)
        self.smallTree.add_edge(5, 7)
        self.smallTree.add_edge(6, 7)

        self.deterministicGraph = nx.Graph()
        self.deterministicGraph.add_edge(0, 1) # deg(0) = 1

        self.deterministicGraph.add_edge(1, 2) # deg(1) = 2

        self.deterministicGraph.add_edge(2, 3) 
        self.deterministicGraph.add_edge(2, 4) # deg(2) = 3

        self.deterministicGraph.add_edge(3, 4) 
        self.deterministicGraph.add_edge(3, 5) 
        self.deterministicGraph.add_edge(3, 6) # deg(3) = 4

        self.deterministicGraph.add_edge(4, 5) 
        self.deterministicGraph.add_edge(4, 6) 
        self.deterministicGraph.add_edge(4, 7) # deg(4) = 5

        self.deterministicGraph.add_edge(5, 6) 
        self.deterministicGraph.add_edge(5, 7) 
        self.deterministicGraph.add_edge(5, 8) 
        self.deterministicGraph.add_edge(5, 9) # deg(5) = 6

        self.deterministicGraph.add_edge(6, 7) 
        self.deterministicGraph.add_edge(6, 8) 
        self.deterministicGraph.add_edge(6, 9) # deg(6) = 6

        self.deterministicGraph.add_edge(7, 8) 
        self.deterministicGraph.add_edge(7, 9) # deg(7) = 5
        
        self.deterministicGraph.add_edge(8, 9) # deg(7) = 4

        

    def test_tree_decomposition(self):
        """Test if the returned decomposition is a valid decomposition for a selection 
        of various graphs
        """
        G = nx.petersen_graph()
        _, decomp = treewidth_min_degree(G)
        is_tree_decomp(G, decomp)
        # Check if each vertex appears at least once in a bag

    def test_small_tree_treewidth(self):
        """Test if the computed treewidth of the known self.smallTree is 2.
        As we know which value we can expect from our heuristic, values other than two are regressions

        """
        G = self.smallTree
        # The order of removal should be (with [] denoting any order of the containing nodes) [1,2,4]3[5,6,7], resulting in treewdith 2 for the heuristic
        
        treewidth, _ = treewidth_min_fill_in(G)
        assert_equals(treewidth, 2)


    def test_heuristic_abort(self):
        """Test if min_degree_heuristic returns None for fully connected graph"""
        graph = {}
        for u in self.complete:
            graph[u] = set()
            for v in self.complete[u]:
                if u != v:  # ignore self-loop
                    graph[u].add(v)

        iterator = MinDegreeHeuristic(graph)
        try:
            print("Removing {}:".format(next(iterator)))
            assert False
        except StopIteration:
            pass

    def test_heuristic_first_steps(self):
        """Test first steps of min_degree heuristic"""
        graph = {}
        for u in self.deterministicGraph:
            graph[u] = set()
            for v in self.deterministicGraph[u]:
                if u != v:  # ignore self-loop
                    graph[u].add(v)
        iterator = MinDegreeHeuristic(graph)
        print("Graph {}:".format(graph))
        
        steps = []
        for elim_node in iterator:
            print("Removing {}:".format(elim_node))
            steps.append(elim_node)
            neighbors = graph[elim_node]
            for n in neighbors:
                for m in neighbors:
                    if n != m and not m in graph[n]:
                        graph[n].add(m)
                        graph[m].add(n)
            for u in graph:
                if elim_node in graph[u]:
                    graph[u].remove(elim_node)
            graph.pop(elim_node, None)
            print("Graph {}:".format(graph))

        # Check only the first 5 elements for equality
        assert_equals(steps[:5], [0, 1, 2, 3, 4])




class TestTreewidthMinFillIn(object):
    """Unit tests for the :mod:`networkx.algorithms.approximation.treewidth_min_fill_in`
    function.

    """

    def setUp(self):
        """Setup for different kinds of trees"""
        self.complete = nx.Graph()
        self.complete.add_edge(1, 2)
        self.complete.add_edge(2, 3)
        self.complete.add_edge(1, 3)

        self.smallTree = nx.Graph()
        self.smallTree.add_edge(1, 2)
        self.smallTree.add_edge(2, 3)
        self.smallTree.add_edge(3, 4)
        self.smallTree.add_edge(1, 4)
        self.smallTree.add_edge(2, 4)
        self.smallTree.add_edge(4, 5)
        self.smallTree.add_edge(5, 6)
        self.smallTree.add_edge(5, 7)
        self.smallTree.add_edge(6, 7)

        self.deterministicGraph = nx.Graph()
        self.deterministicGraph.add_edge(1, 2)
        self.deterministicGraph.add_edge(1, 3)
        self.deterministicGraph.add_edge(3, 4)
        self.deterministicGraph.add_edge(2, 4)
        self.deterministicGraph.add_edge(3, 5)
        self.deterministicGraph.add_edge(4, 5)
        self.deterministicGraph.add_edge(3, 6)
        self.deterministicGraph.add_edge(5, 6)

        #self.largeTree


    def test_tree_decomposition(self):
        """Test if the returned decomposition is a valid decomposition for a selection 
        of various graphs
        """
        G = nx.petersen_graph()
        _, decomp = treewidth_min_fill_in(G)
        is_tree_decomp(G, decomp)
        # Check if each vertex appears at least once in a bag

    def test_small_tree_treewidth(self):
        """Test if the computed treewidth of the known self.smallTree is 2"""
        G = self.smallTree
        # The order of removal should be (with [] denoting any order of the containing nodes) [1,2,4]3[5,6,7], resulting in treewdith 2 for the heuristic
        
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
        iterator = MinFillInHeuristic(graph)
        try:
            print("Removing {}:".format(next(iterator)))
            assert False
        except StopIteration:
            pass

    def test_heuristic_first_steps(self):
        """Test first steps of min_fill_in heuristic"""

        graph = {}
        for u in self.deterministicGraph:
            graph[u] = set()
            for v in self.deterministicGraph[u]:
                if u != v:  # ignore self-loop
                    graph[u].add(v)
        iterator = MinFillInHeuristic(graph)
        print("Graph {}:".format(graph))


        steps = []
        for elim_node in iterator:
            print("Removing {}:".format(elim_node))
            steps.append(elim_node)
            neighbors = graph[elim_node]
            for n in neighbors:
                for m in neighbors:
                    if n != m and not m in graph[n]:
                        graph[n].add(m)
                        graph[m].add(n)
            for u in graph:
                if elim_node in graph[u]:
                    graph[u].remove(elim_node)
            graph.pop(elim_node, None)
            print("Graph {}:".format(graph))

        # Check only the first 2 elements for equality
        assert_equals(steps[:2], [6, 5])