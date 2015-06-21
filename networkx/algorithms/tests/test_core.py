#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestCore:

    def setUp(self):
        # G is the example graph in Figure 1 from Batagelj and
        # Zaversnik's paper titled An O(m) Algorithm for Cores
        # Decomposition of Networks, 2003,
        # http://arXiv.org/abs/cs/0310049.  With nodes labeled as
        # shown, the 3-core is given by nodes 1-8, the 2-core by nodes
        # 9-16, the 1-core by nodes 17-20 and node 21 is in the
        # 0-core.
        t1=nx.convert_node_labels_to_integers(nx.tetrahedral_graph(),1)
        t2=nx.convert_node_labels_to_integers(t1,5)
        G=nx.union(t1,t2)
        G.add_edges_from( [(3,7), (2,11), (11,5), (11,12), (5,12), (12,19),
                           (12,18), (3,9), (7,9), (7,10), (9,10), (9,20),
                           (17,13), (13,14), (14,15), (15,16), (16,13)])
        G.add_node(21)
        self.G=G

        # Create the graph H resulting from the degree sequence
        # [0,1,2,2,2,2,3] when using the Havel-Hakimi algorithm. 

        degseq=[0,1,2,2,2,2,3]
        H = nx.havel_hakimi_graph(degseq)
        mapping = {6:0, 0:1, 4:3, 5:6, 3:4, 1:2, 2:5 }
        self.H = nx.relabel_nodes(H, mapping)

    def test_trivial(self):
        """Empty graph"""
        G = nx.Graph()
        assert_equal(nx.find_cores(G),{})

    def test_find_cores(self):
        cores=nx.find_cores(self.G)
        nodes_by_core=[]
        for val in [0,1,2,3]:
            nodes_by_core.append( sorted([k for k in cores if cores[k]==val]))
        assert_equal(nodes_by_core[0],[21])
        assert_equal(nodes_by_core[1],[17, 18, 19, 20])
        assert_equal(nodes_by_core[2],[9, 10, 11, 12, 13, 14, 15, 16])
        assert_equal(nodes_by_core[3], [1, 2, 3, 4, 5, 6, 7, 8])

    def test_core_number(self):
        # smoke test real name
        cores=nx.core_number(self.G)

    def test_find_cores2(self):
        cores=nx.find_cores(self.H)
        nodes_by_core=[]
        for val in [0,1,2]:
            nodes_by_core.append( sorted([k for k in cores if cores[k]==val]))
        assert_equal(nodes_by_core[0],[0])
        assert_equal(nodes_by_core[1],[1, 3])
        assert_equal(nodes_by_core[2],[2, 4, 5, 6])

    def test_main_core(self):
        main_core_subgraph=nx.k_core(self.H)
        assert_equal(sorted(main_core_subgraph.nodes()),[2,4,5,6])

    def test_k_core(self):
        # k=0
        k_core_subgraph=nx.k_core(self.H,k=0)
        assert_equal(sorted(k_core_subgraph.nodes()),sorted(self.H.nodes()))
        # k=1
        k_core_subgraph=nx.k_core(self.H,k=1)
        assert_equal(sorted(k_core_subgraph.nodes()),[1,2,3,4,5,6])
        # k=2
        k_core_subgraph=nx.k_core(self.H,k=2)
        assert_equal(sorted(k_core_subgraph.nodes()),[2,4,5,6])

    def test_main_crust(self):
        main_crust_subgraph=nx.k_crust(self.H)
        assert_equal(sorted(main_crust_subgraph.nodes()),[0,1,3])

    def test_k_crust(self):
        # k=0
        k_crust_subgraph=nx.k_crust(self.H,k=2)
        assert_equal(sorted(k_crust_subgraph.nodes()),sorted(self.H.nodes()))
        # k=1
        k_crust_subgraph=nx.k_crust(self.H,k=1)
        assert_equal(sorted(k_crust_subgraph.nodes()),[0,1,3])
        # k=2
        k_crust_subgraph=nx.k_crust(self.H,k=0)
        assert_equal(sorted(k_crust_subgraph.nodes()),[0])

    def test_main_shell(self):
        main_shell_subgraph=nx.k_shell(self.H)
        assert_equal(sorted(main_shell_subgraph.nodes()),[2,4,5,6])

    def test_k_shell(self):
        # k=0
        k_shell_subgraph=nx.k_shell(self.H,k=2)
        assert_equal(sorted(k_shell_subgraph.nodes()),[2,4,5,6])
        # k=1
        k_shell_subgraph=nx.k_shell(self.H,k=1)
        assert_equal(sorted(k_shell_subgraph.nodes()),[1,3])
        # k=2
        k_shell_subgraph=nx.k_shell(self.H,k=0)
        assert_equal(sorted(k_shell_subgraph.nodes()),[0])

    def test_k_corona(self):
        # k=0
        k_corona_subgraph=nx.k_corona(self.H,k=2)
        assert_equal(sorted(k_corona_subgraph.nodes()),[2,4,5,6])
        # k=1
        k_corona_subgraph=nx.k_corona(self.H,k=1)
        assert_equal(sorted(k_corona_subgraph.nodes()),[1])
        # k=2
        k_corona_subgraph=nx.k_corona(self.H,k=0)
        assert_equal(sorted(k_corona_subgraph.nodes()),[0])
