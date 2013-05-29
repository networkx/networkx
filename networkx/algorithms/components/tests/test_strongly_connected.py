#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx import NetworkXError 

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
        for G,C in self.gc:
            if len(C)==1:
                assert_true(nx.is_strongly_connected(G))
            else:
                assert_false(nx.is_strongly_connected(G))


    def test_strongly_connected_component_subgraphs(self):
        scc=nx.strongly_connected_component_subgraphs
        for G,C in self.gc:
            assert_equal(sorted([sorted(g.nodes()) for g in scc(G)]),sorted(C))
        G,C=self.gc[0]
        G.add_edge(1,2,eattr='red')
        G.node[1]['nattr']='blue'
        G.graph['gattr']='green'
        sgs=scc(G)[1]
        assert_equal(sgs[1][2]['eattr'],'red')
        assert_equal(sgs.node[1]['nattr'],'blue')
        assert_equal(sgs.graph['gattr'],'green')
        sgs[1][2]['eattr']='blue'
        assert_equal(G[1][2]['eattr'],'red')
        assert_equal(sgs[1][2]['eattr'],'blue')

    def test_contract_scc1(self):
        G = nx.DiGraph()
        G.add_edges_from([(1,2),(2,3),(2,11),(2,12),(3,4),(4,3),(4,5),
                          (5,6),(6,5),(6,7),(7,8),(7,9),(7,10),(8,9),
                          (9,7),(10,6),(11,2),(11,4),(11,6),(12,6),(12,11)])
        scc = nx.strongly_connected_components(G)
        cG = nx.condensation(G, scc)
        # DAG
        assert_true(nx.is_directed_acyclic_graph(cG))
        # # nodes
        assert_equal(sorted(cG.nodes()),[0,1,2,3])
        # # edges
        mapping={}
        for i,component in enumerate(scc):
            for n in component:
                mapping[n] = i
        edge=(mapping[2],mapping[3])
        assert_true(cG.has_edge(*edge))
        edge=(mapping[2],mapping[5])
        assert_true(cG.has_edge(*edge))
        edge=(mapping[3],mapping[5])
        assert_true(cG.has_edge(*edge))

    def test_contract_scc_isolate(self):
        # Bug found and fixed in [1687].
        G = nx.DiGraph()
        G.add_edge(1,2)
        G.add_edge(2,1)
        scc = nx.strongly_connected_components(G)        
        cG = nx.condensation(G, scc)
        assert_equal(cG.nodes(),[0])
        assert_equal(cG.edges(),[])

    def test_contract_scc_edge(self):
        G = nx.DiGraph()
        G.add_edge(1,2)
        G.add_edge(2,1)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,3)
        scc = nx.strongly_connected_components(G)        
        cG = nx.condensation(G, scc)
        assert_equal(cG.nodes(),[0,1])
        if 1 in scc[0]:
            edge = (0,1)
        else:
            edge = (1,0)
        assert_equal(cG.edges(),[edge])
    
    def test_connected_raise(self):
        G=nx.Graph()
        assert_raises(NetworkXError,nx.strongly_connected_components,G)
        assert_raises(NetworkXError,nx.kosaraju_strongly_connected_components,G)
        assert_raises(NetworkXError,nx.strongly_connected_components_recursive,G)
        assert_raises(NetworkXError,nx.strongly_connected_component_subgraphs,G)
        assert_raises(NetworkXError,nx.is_strongly_connected,G)
        assert_raises(NetworkXError,nx.condensation,G)
