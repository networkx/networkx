#!/usr/bin/env python
from nose.tools import *
import networkx
import networkx as nx

class TestCycles:
    def setUp(self):
        G=networkx.Graph() 
        G.add_cycle([0,1,2,3])
        G.add_cycle([0,3,4,5])
        G.add_cycle([0,1,6,7,8])
        G.add_edge(8,9)
        self.G=G
        
    def is_cyclic_permuatation(self,a,b):
        n=len(a)
        if len(b)!=n:
            return False
        l=a+a
        return any(l[i:i+n]==b for i in range(2*n-n+1))

    def test_cycle_basis(self):
        G=self.G
        cy=networkx.cycle_basis(G,0)
        sort_cy= sorted( sorted(c) for c in cy )
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5]])
        cy=networkx.cycle_basis(G,1)
        sort_cy= sorted( sorted(c) for c in cy )
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5]])
        cy=networkx.cycle_basis(G,9)
        sort_cy= sorted( sorted(c) for c in cy )
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5]])
        # test disconnected graphs
        G.add_cycle(list("ABC")) 
        cy=networkx.cycle_basis(G,9)
        sort_cy= sorted(sorted(c) for c in cy[:-1]) + [sorted(cy[-1])]
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5],['A','B','C']])

    @raises(nx.NetworkXNotImplemented)
    def test_cycle_basis(self):
        G=nx.DiGraph()
        cy=networkx.cycle_basis(G,0)

    @raises(nx.NetworkXNotImplemented)
    def test_cycle_basis(self):
        G=nx.MultiGraph()
        cy=networkx.cycle_basis(G,0)

    def test_simple_cycles(self):
        G = nx.DiGraph([(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)])
        c=sorted(nx.simple_cycles(G))
        ca=[[0, 0], [0, 1, 2, 0], [0, 2, 0], [1, 2, 1], [2, 2]]
        for (a,b) in zip(c,ca):
            assert_true(self.is_cyclic_permuatation(a[:-1],b[:-1]))

    @raises(nx.NetworkXNotImplemented)
    def test_simple_cycles_graph(self):
        G = nx.Graph()
        c = sorted(nx.simple_cycles(G))

    def test_unsortable(self):
        G=nx.DiGraph()
        G.add_cycle(['a',1])
        c=nx.simple_cycles(G)

    def test_simple_cycles_small(self):
        G = nx.DiGraph()
        G.add_path([1,2,3,1])
        c=sorted(nx.simple_cycles(G))
        assert_equal(c,[[1,2,3,1]])
        G.add_path([10,20,30,10])
        c=sorted(nx.simple_cycles(G))
        ca=[[1,2,3,1],[10,20,30,10]]
        for (a,b) in zip(c,ca):
            assert_true(self.is_cyclic_permuatation(a[:-1],b[:-1]))

    def test_simple_cycles_empty(self):
        G = nx.DiGraph()
        assert_equal(list(nx.simple_cycles(G)),[])
        
    def test_complete_directed_graph(self):
        # see table 2 in Johnson's paper
        ncircuits=[1,5,20,84,409,2365,16064]
        for n,c in zip(range(2,9),ncircuits):
            G=nx.DiGraph(nx.complete_graph(n))
            assert_equal(len(nx.simple_cycles(G)),c)
        
    def worst_case_graph(self,k):
        # see figure 1 in Johnson's paper
        # this graph has excactly 3k simple cycles
        G=nx.DiGraph()
        for n in range(2,k+2):
            G.add_edge(1,n)
            G.add_edge(n,k+2)
        G.add_edge(2*k+1,1)
        for n in range(k+2,2*k+2):
            G.add_edge(n,2*k+2)
            G.add_edge(n,n+1)
        G.add_edge(2*k+3,k+2)
        for n in range(2*k+3,3*k+3):
            G.add_edge(2*k+2,n)
            G.add_edge(n,3*k+3)
        G.add_edge(3*k+3,2*k+2)
        return G

    def test_worst_case_graph(self):
        # see figure 1 in Johnson's paper
        for k in range(3,10):
            G=self.worst_case_graph(k)
            l=len(nx.simple_cycles(G))
            assert_equal(l,3*k)
        
