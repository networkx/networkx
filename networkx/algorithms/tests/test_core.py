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
        self.H=nx.havel_hakimi_graph(degseq)



    def test_trivial(self):
        """Empty graph"""
        G = nx.Graph()
        assert_equal(nx.find_cores(G),{})

    def find_cores(self):
        cores=find_cores(self.G)
        nodes_by_core=[]
        for val in [0,1,2,3]:
            nodes_by_core.append( sorted([k for k in cores if cores[k]==val]))
        assert_equal(nodes_by_core[0],[21])
        assert_equal(nodes_by_core[1],[17, 18, 19, 20])
        assert_equal(nodes_by_core[2],[9, 10, 11, 12, 13, 14, 15, 16])
        assert_equal(nodes_by_core[3], [1, 2, 3, 4, 5, 6, 7, 8])

    def find_cores2(self):
        cores=find_cores(self.H)
        nodes_by_core=[]
        for val in [0,1,2]:
            nodes_by_core.append( sorted([k for k in cores if cores[k]==val]))
        assert_equal(nodes_by_core[0],[0])
        assert_equal(nodes_by_core[1],[1, 3])
        assert_equal(nodes_by_core[2],[2, 4, 5, 6])
