#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestComponent:

    def test_contract_scc(self):
        G = nx.DiGraph()
        G.add_edges_from([(1,2),(2,3),(2,11),(2,12),(3,4),(4,3),(4,5),
                          (5,6),(6,5),(6,7),(7,8),(7,9),(7,10),(8,9),
                          (9,7),(10,6),(11,2),(11,4),(11,6),(12,6),(12,11)])
        cG = nx.contract_strongly_connected_components(G)
        # nodes
        assert((1,) in cG)
        assert((2,11,12) in cG)
        assert((3,4) in cG)
        assert((5,6,7,8,9,10) in cG)
        assert((2,11,12) in cG[(1,)])
        # edges
        assert((3,4) in cG[(2,11,12)])
        assert((5,6,7,8,9,10) in cG[(2,11,12)])
        assert((5,6,7,8,9,10) in cG[(3,4)])
        # DAG
        assert(nx.is_directed_acyclic_graph(cG))
