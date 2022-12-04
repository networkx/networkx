"""
    Tests for dependency_graph(DG).
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.dependency_graph import build_DG_from_CFG


class TestDepndencyGraph:
    #basic_code control_flow_graph
        basic_CFG = nx.diGraph()
        basic_CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        basic_CFG.add_edges_from(edges)

       #basic_code_v1 control_flow_graph
       #Variable renaming
        basic_CFG_v1 = nx.diGraph()
        basic_CFG_v1.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        basic_CFG_v1.add_edges_from(edges)


       #basic_code_v2 control_flow_graph
       #Statement reordering
        basic_CFG_v2 = nx.diGraph()
        basic_CFG_v2.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        basic_CFG_v2.add_edges_from(edges)

       #basic_code_v3 control_flow_graph
       #Format alternation
        basic_CFG_v3 = nx.diGraph()
        basic_CFG_v3.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        basic_CFG_v3.add_edges_from(edges)

       #basic_code_v4 control_flow_graph
       #Statement replacement
        basic_CFG_v4 = nx.diGraph()
        basic_CFG_v4.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        basic_CFG_v4.add_edges_from(edges)

       #basic_code_v5 control_flow_graph
       #Spaghetti code 
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,14))
        CFG.add_edge_from((1,2),(2,3),(3,4),(4,10),(10,11),(11,12),(12,13),(13,5),(5,6),(6,7),(7,8),(8,5)(8,9),(5,9))
    ###############################################

    #stupid code_v1 control_flow_graph
        stupid_CFG = nx.diGraph()
        stupid_CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 7)]
        stupid_CFG.add_edges_from(edges)
    
    #stupid_code_v2 contrfol_flow_graph
    #variable renaming
        stupid_v1_CFG = nx.diGraph()
        stupid_v1_CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 7)]
        stupid_v1_CFG.add_edges_from(edges)
    ###############################################

    #fork_code control_flow_graph
    #fork code
        fork_CFG = nx.diGraph()
        fork_CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 5)]
        edges.append((5,3),(3,6))
        fork_CFG.add_edges_from(edges)
    
    #fork_code_v1 control_flow_graph
    #junk code insertion
        fork_v1_CFG = nx.diGraph()
        fork_v1_CFG.add_nodes_from(range(1,15))
        edges = [(edge, edge+1) for edge in range(1, 15)]
        edges.append((8,12),(11,8),(13,7),(7,14))
        fork_v1_CFG.add_edges_from(edges)


    def test_basic_code(self):
        """
        Checks the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        
        basic_DG = nx.diGraph()
        basic_DG.add_nodes_from(range(1,12))
        edges = [(1,4),(2,5),(3,6),(4,7),(5,8),(6,7),(6,8),(6,9),(8,8),(9,7),(9,8),(9,9)]
        CFG.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG) == basic_DG

    def test_basic_code_v1(self):
        """
        Checks the first varient (Variable renaming) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        basic_DG_v1 = nx.diGraph()
        basic_DG_v1.add_nodes_from(range(1,12))
        edges = [(1,4),(2,5),(3,6),(4,7),(5,8),(6,7),(6,8),(6,9),(8,8),(9,7),(9,8),(9,9)]
        basic_DG_v1.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG_v1) == basic_DG_v1

    def test_basic_code_v2(self):
        """
        Checks the second varient (Statement reordering) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        basic_DG_v2 = nx.diGraph()
        basic_DG_v2.add_nodes_from(range(1,12))
        edges = [(1,3),(2,6),(4,5),(3,8),(6,7),(6,8),(6,9),(5,7),(9,7),(9,8),(9,9),(8,8)]
        basic_DG_v2.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG_v2) == basic_DG_v2

    def test_basic_code_v3(self):
        """
        Checks the third varient (Format alternation) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        basic_DG_v3 = nx.diGraph()
        basic_DG_v3.add_nodes_from(range(1,12))
        edges = [(1,4),(2,5),(3,6),(4,7),(5,8),(6,7),(6,8),(6,9),(8,8),(9,7),(9,8),(9,9)]
        basic_DG_v3.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG_v3) == basic_DG_v3

    def test_basic_code_v4(self):
        """
        Checks the fourth varient (Statement replacement) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        basic_DG_v4 = nx.diGraph()
        basic_DG_v4.add_nodes_from(range(1,12))
        edges = [(1,5),(2,6),(3,4),(4,5),(5,8),(6,7),(6,8),(6,9),(8,8),(9,7),(9,8),(9,9)]
        basic_DG_v4.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG_v4) == basic_DG_v4


    def test_basic_code_v5(self):
        """
        Checks the fith varient (Spaghetti code) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

        """
        basic_DG_v5 = nx.diGraph()
        basic_DG_v5.add_nodes_from(range(1,12))
        edges = [(1,11),(2,12),(3,10),(11,6),(12,6),(12,7),(12,5),(10,5),(6,6),(7,6),(7,7),(7,5)]
        basic_DG_v5.add_edges_from(edges)

        assert build_DG_from_CFG(self.basic_CFG_v5) == basic_DG_v5

    def test_stupid_code(self):
        """
        Checks the stupid_code example that we made up:
        """
        stupid_DG = nx.diGraph()
        stupid_DG.add_nodes_from(range(1,7))
        edges = [(1,4),(2,5),(3,6)]
        stupid_DG.add_edges_from(edges)

        assert build_DG_from_CFG(self.stupid_CFG) == stupid_DG

    def test_stupid_code_v1(self):
        """
        Checks the first variant of stupid_code:
        """
        
        stupid_DG_v1 = nx.diGraph()
        stupid_DG_v1.add_nodes_from(range(1,7))
        edges = [(1,4),(2,5),(3,6)]
        stupid_DG_v1.add_edges_from(edges)

        assert build_DG_from_CFG(self.stupid_CFG_v1) == stupid_DG_v1

    def test_fork_code(self):
        """
        Checks the fork_code virus code:
        """
        
        fork_DG = nx.diGraph()
        fork_DG.add_nodes_from(range(1,7))
        edges = [(1,2),(2,3)]
        fork_DG.add_edges_from(edges)

        assert build_DG_from_CFG(self.fork_CFG) == fork_DG

    def test_fork_code_v1(self):
        """
        Checks the first variant of fork_code virus code:
        """
        
        fork_v1_DG = nx.diGraph()
        fork_v1_DG.add_nodes_from(range(1,15))
        edges = [(1,4),(2,6),(3,5),(4,7),(5,8),(5,10),(10,10)]
        fork_v1_DG.add_edges_from(edges)

        assert build_DG_from_CFG(self.fork_v1_CFG) == fork_v1_DG





