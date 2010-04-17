#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestStronglyConnected:

    def setUp(self):
        self.gc=[]
        G=nx.DiGraph()
        G.add_edges_from([(1,2),(2,3),(2,8),(3,4),(3,7),
                          (4,5),(5,3),(5,6),(7,4),(7,6),(8,1),(8,7)])
        C=[[3, 4, 5, 7], [1, 2, 8],  [6]]
        self.gc.append((G,C))

        G= nx.DiGraph()
        G.add_edges_from([(1,2),(1,3),(1,4),(4,2),(3,4),(2,3)])
        C = [[2, 3, 4],[1]]
        self.gc.append((G,C))

        G = nx.DiGraph()
        G.add_edges_from([(1,2),(2,3),(3,2),(2,1)])
        C = [[1, 2, 3]]
        self.gc.append((G,C))

        # Eppstein's tests
        G = nx.DiGraph({ 0:[1],1:[2,3],2:[4,5],3:[4,5],4:[6],5:[],6:[]})
        C = [[0],[1],[2],[3],[4],[5],[6]]
        self.gc.append((G,C))
    
        G = nx.DiGraph({0:[1],1:[2,3,4],2:[0,3],3:[4],4:[3]})
        C = [[0,1,2],[3,4]]
        self.gc.append((G,C))


    def test_tarjan(self):
        scc=nx.strongly_connected_components
        for G,C in self.gc:
            assert_equal(sorted([sorted(g) for g in scc(G)]),sorted(C))


    def test_tarjan_recursive(self):
        scc=nx.strongly_connected_components_recursive
        for G,C in self.gc:
            assert_equal(sorted([sorted(g) for g in scc(G)]),sorted(C))


    def test_kosaraju(self):
        scc=nx.kosaraju_strongly_connected_components
        for G,C in self.gc:
            assert_equal(sorted([sorted(g) for g in scc(G)]),sorted(C))

    def test_number_strongly_connected_components(self):
        ncc=nx.number_strongly_connected_components
        for G,C in self.gc:
            assert_equal(ncc(G),len(C))

    def test_is_strongly_connected(self):            
        ncc=nx.number_strongly_connected_components
        for G,C in self.gc:
            if len(C)==1:
                assert_true(nx.is_strongly_connected(G))
            else:
                assert_false(nx.is_strongly_connected(G))


    def test_strongly_connected_component_subgraphs(self):
        scc=nx.strongly_connected_component_subgraphs
        for G,C in self.gc:
            assert_equal(sorted([sorted(g.nodes()) for g in scc(G)]),sorted(C))


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




