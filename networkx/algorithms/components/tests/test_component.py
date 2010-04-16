#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestComponent:

    def test_contract_scc1(self):
        G = nx.DiGraph()
        G.add_edges_from([(1,2),(2,3),(2,11),(2,12),(3,4),(4,3),(4,5),
                          (5,6),(6,5),(6,7),(7,8),(7,9),(7,10),(8,9),
                          (9,7),(10,6),(11,2),(11,4),(11,6),(12,6),(12,11)])
        cG = nx.condensation(G)
        # nodes
        assert_true((1,) in cG)
        assert_true((2,11,12) in cG)
        assert_true((3,4) in cG)
        assert_true((5,6,7,8,9,10) in cG)
        assert_true((2,11,12) in cG[(1,)])
        # edges
        assert_true((3,4) in cG[(2,11,12)])
        assert_true((5,6,7,8,9,10) in cG[(2,11,12)])
        assert_true((5,6,7,8,9,10) in cG[(3,4)])
        # DAG
        assert_true(nx.is_directed_acyclic_graph(cG))

    def test_contract_scc2(self):
        # Bug found and fixed in [1687].
        G = nx.DiGraph()
        G.add_edge(1,2)
        G.add_edge(2,1)
        cG = nx.condensation(G)
        assert_true((1,2) in cG)

class TestAttractingComponents(object):
    def setUp(self):
        self.G1 = nx.DiGraph()
        self.G1.add_edges_from([(5,11),(11,2),(11,9),(11,10),
                                (7,11),(7,8),(8,9),(3,8),(3,10)])
        self.G2 = nx.DiGraph()
        self.G2.add_edges_from([(0,1),(0,2),(1,1),(1,2),(2,1)])

        self.G3 = nx.DiGraph()
        self.G3.add_edges_from([(0,1),(1,2),(2,1),(0,3),(3,4),(4,3)])

    def test_attracting_components(self):
        ac = nx.attracting_components(self.G1)
        assert_true((2,) in ac)
        assert_true((9,) in ac)
        assert_true((10,) in ac)

        ac = nx.attracting_components(self.G2)
        ac = [tuple(sorted(x)) for x in ac]
        print ac
        assert_true(ac == [(1,2)])

        ac = nx.attracting_components(self.G3)
        ac = [tuple(sorted(x)) for x in ac]
        assert_true((1,2) in ac)
        assert_true((3,4) in ac)
        assert_equal(len(ac), 2)
        
    def test_number_attacting_components(self):
        assert_equal(len(nx.attracting_components(self.G1)), 3)
        assert_equal(len(nx.attracting_components(self.G2)), 1)
        assert_equal(len(nx.attracting_components(self.G3)), 2)

    def test_is_attracting_component(self):
        assert_false(nx.is_attracting_component(self.G1))
        assert_false(nx.is_attracting_component(self.G2))
        assert_false(nx.is_attracting_component(self.G3))
        g2 = self.G3.subgraph([1,2])
        assert_true(nx.is_attracting_component(g2))

    def test_attracting_component_subgraphs(self):
        subgraphs = nx.attracting_component_subgraphs(self.G1)
        for subgraph in subgraphs:
            assert_equal(len(subgraph), 1)

        subgraphs = nx.attracting_component_subgraphs(self.G2)
        assert_equal(len(subgraphs), 1)
        assert_true(1 in subgraphs[0])
        assert_true(2 in subgraphs[0])
        
