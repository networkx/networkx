#!/usr/bin/env python
# run with nose: nosetests -v test_euler.py

from nose.tools import *
import networkx as nx
from networkx import is_eulerian,eulerian_circuit

class TestEuler:

    def test_is_eulerian(self):
        assert_true(is_eulerian(nx.complete_graph(5)))
        assert_true(is_eulerian(nx.complete_graph(7)))
        assert_true(is_eulerian(nx.hypercube_graph(4)))
        assert_true(is_eulerian(nx.hypercube_graph(6)))

        assert_false(is_eulerian(nx.complete_graph(4)))
        assert_false(is_eulerian(nx.complete_graph(6)))
        assert_false(is_eulerian(nx.hypercube_graph(3)))
        assert_false(is_eulerian(nx.hypercube_graph(5)))

        assert_false(is_eulerian(nx.petersen_graph()))
        assert_false(is_eulerian(nx.path_graph(4)))

    def test_is_eulerian2(self):
        # not connected
        G = nx.Graph()
        G.add_nodes_from([1,2,3])
        assert_false(is_eulerian(G))
        # not strongly connected
        G = nx.DiGraph()
        G.add_nodes_from([1,2,3])
        assert_false(is_eulerian(G))
        G = nx.MultiDiGraph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(2,3)
        G.add_edge(3,1)
        assert_false(is_eulerian(G))

        

    def test_eulerian_circuit_cycle(self):
        G=nx.cycle_graph(4)

        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,1,2,3])
        assert_equal(edges,[(0,1),(1,2),(2,3),(3,0)])

        edges=list(eulerian_circuit(G,source=1))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[1,0,3,2])
        assert_equal(edges,[(1,0),(0,3),(3,2),(2,1)])


    def test_eulerian_circuit_digraph(self):
        G=nx.DiGraph()
        G.add_cycle([0,1,2,3])

        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,1,2,3])
        assert_equal(edges,[(0,1),(1,2),(2,3),(3,0)])

        edges=list(eulerian_circuit(G,source=1))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[1,2,3,0])
        assert_equal(edges,[(1,2),(2,3),(3,0),(0,1)])


    def test_eulerian_circuit_multigraph(self):
        G=nx.MultiGraph()
        G.add_cycle([0,1,2,3])
        G.add_edge(1,2)
        G.add_edge(1,2)
        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,1,2,1,2,3])
        assert_equal(edges,[(0,1),(1,2),(2,1),(1,2),(2,3),(3,0)])


    @raises(nx.NetworkXError)
    def test_not_eulerian(self):    
        f=list(eulerian_circuit(nx.complete_graph(4)))
