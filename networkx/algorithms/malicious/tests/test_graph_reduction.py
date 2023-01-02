"""
    Tests for graph_reduction.
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.graph_reduction import build_RG_from_DG


class TestDepndencyGraph:
    # basic_code control_flow_graph
    basic_DG = nx.DiGraph()
    basic_DG.add_nodes_from(range(1, 12))
    edges = [(1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 7),
                (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_DG.add_edges_from(edges)

    # basic_code_v1 control_flow_graph
    # Variable renaming
    basic_DG_v1 = nx.DiGraph()
    basic_DG_v1.add_nodes_from(range(1, 12))
    edges = [(1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 7),
                (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_DG_v1.add_edges_from(edges)

    # basic_code_v2 control_flow_graph
    # Statement reordering
    basic_DG_v2 = nx.DiGraph()
    basic_DG_v2.add_nodes_from(range(1, 12))
    edges = [(1, 3), (2, 6), (4, 5), (3, 8), (6, 7), (6, 8),
                (6, 9), (5, 7), (9, 7), (9, 8), (9, 9), (8, 8)]
    basic_DG_v2.add_edges_from(edges)

    # basic_code_v3 control_flow_graph
    # Format alternation
    basic_DG_v3 = nx.DiGraph()
    basic_DG_v3.add_nodes_from(range(1, 12))
    edges = [(1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 7),
                (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_DG_v3.add_edges_from(edges)

    # basic_code_v4 control_flow_graph
    # Statement replacement
    basic_DG_v4 = nx.DiGraph()
    basic_DG_v4.add_nodes_from(range(1, 12))
    edges = [(1, 5), (2, 6), (3, 4), (4, 5), (5, 8), (6, 7),
                (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_DG_v4.add_edges_from(edges)

    # basic_code_v5 control_flow_graph
    # Spaghetti code
    basic_DG_v5 = nx.DiGraph()
    basic_DG_v5.add_nodes_from(range(1, 14))
    edges = [(1, 11), (2, 12), (3, 10), (11, 6), (12, 6), (12, 7),
                (12, 5), (10, 5), (6, 6), (7, 6), (7, 7), (7, 5)]
    basic_DG_v5.add_edges_from(edges)
    ###############################################

    # stupid code control_flow_graph
    stupid_DG = nx.DiGraph()
    stupid_DG.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_DG.add_edges_from(edges)

    # stupid_code_v1 contrfol_flow_graph
    # variable renaming
    stupid_DG_v1 = nx.DiGraph()
    stupid_DG_v1.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_DG_v1.add_edges_from(edges)
    ###############################################

    # fork_code control_flow_graph
    # fork code
    fork_DG = nx.DiGraph()
    fork_DG.add_nodes_from(range(1, 7))
    edges = [(1, 2), (2, 3)]
    fork_DG.add_edges_from(edges)

    # fork_code_v1 control_flow_graph
    # junk code insertion
    fork_v1_DG = nx.DiGraph()
    fork_v1_DG.add_nodes_from(range(1, 15))
    edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
    fork_v1_DG.add_edges_from(edges)


    def test_basic_code(self):
        """
        Checks the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        
        basic_RG = self.basic_DG
        basic_RG.remove_edges_from([(1,4),(2,5),(3,6),(4,7),(5,8)])
        basic_RG.remove_nodes_from([1,2,3,4,5,10,11])

        assert build_RG_from_DG(self.basic_DG) == basic_RG

    def test_basic_code_v1(self):
        """
        Checks the first varient (Variable renaming) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        basic_v1_RG = self.basic_DG_v1
        basic_v1_RG.remove_edges_from([(1,4),(2,5),(3,6),(4,7),(5,8)])
        basic_v1_RG.remove_nodes_from([1,2,3,4,5,10,11])

        assert build_RG_from_DG(self.basic_DG_v1) == basic_v1_RG

    def test_basic_code_v2(self):
        """
        Checks the second varient (Statement reordering) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        basic_v2_RG = self.basic_DG_v2
        basic_v2_RG.remove_edges_from([(1,3),(2,6),(4,5),(3,8),(5,7)])
        basic_v2_RG.remove_nodes_from([1,2,3,4,5,10,11])

        assert build_RG_from_DG(self.basic_DG_v2) == basic_v2_RG

    def test_basic_code_v3(self):
        """
        Checks the third varient (Format alternation) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        basic_v3_RG = self.basic_DG_v3
        basic_v3_RG.remove_edges_from([(1,4),(2,5),(3,6),(4,7),(5,8)])
        basic_v3_RG.remove_nodes_from([1,2,3,4,5,10,11])

        assert build_RG_from_DG(self.basic_DG_v3) == basic_v3_RG

    def test_basic_code_v4(self):
        """
        Checks the fourth varient (Statement replacement) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        basic_v4_RG = self.basic_DG_v4
        basic_v4_RG.remove_edges_from([(1,5),(2,6),(3,4),(4,5),(5,8)])
        basic_v4_RG.remove_nodes_from([1,2,3,4,5,10,11])

        assert build_RG_from_DG(self.basic_DG_v4) == basic_v4_RG


    def test_basic_code_v5(self):
        """
        Checks the fith varient (Spaghetti code) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        basic_v5_RG = self.basic_DG_v5
        basic_v5_RG.remove_edges_from([(1,11),(2,12),(3,10),(11,6),(10,5)])
        basic_v5_RG.remove_nodes_from([1,2,3,4,8,9,10,11,13])

        assert build_RG_from_DG(self.basic_DG_v5) == basic_v5_RG

    def test_stupid_code(self):
        """
        Checks the stupid_code example that we made up:
        """
        stupid_RG = self.stupid_DG # no edges or nodes to reduce

        assert build_RG_from_DG(self.stupid_DG) == stupid_RG

    def test_stupid_code_v1(self):
        """
        Checks the first variant of stupid_code:
        """
        
        stupid_v1_RG = self.stupid_DG_v1 # no edges or nodes to reduce

        assert build_RG_from_DG(self.stupid_DG_v1) == stupid_v1_RG

    def test_fork_code(self):
        """
        Checks the fork_code virus code:
        """
        
        fork_RG = self.fork_DG
        fork_RG.remove_nodes_from([4, 5, 6])

        assert build_RG_from_DG(self.fork_DG) == fork_RG

    def test_fork_code_v1(self):
        """
        Checks the first variant of fork_code virus code:
        """
        
        fork_v1_RG = self.fork_v1_DG
        fork_v1_RG.remove_nodes_from([1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14])

        assert build_RG_from_DG(self.fork_v1_DG) == fork_v1_RG

