"""
    Tests for fitness.
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.graph_reduction import build_RG_from_DG
from networkx.algorithms.malicious.genetic_algorithm import GA


class TestFitnessFunction:
    # basic_code reduced garph
    basic_RG = nx.DiGraph()
    basic_RG.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG.add_edges_from(edges)

    # basic_code_v1 reduced garph
    # Variable renaming
    basic_RG_v1 = nx.DiGraph()
    basic_RG_v1.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v1.add_edges_from(edges)

    # basic_code_v2 reduced garph
    # Statement reordering
    basic_RG_v2 = nx.DiGraph()
    basic_RG_v2.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v2.add_edges_from(edges)

    # basic_code_v3 reduced garph
    # Format alternation
    basic_RG_v3 = nx.DiGraph()
    basic_RG_v3.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v3.add_edges_from(edges)

    # basic_code_v4 reduced garph
    # Statement replacement
    basic_RG_v4 = nx.DiGraph()
    basic_RG_v4.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v4.add_edges_from(edges)

    # basic_code_v5 reduced garph
    # Spaghetti code
    basic_RG_v5 = nx.DiGraph()
    basic_RG_v5.add_nodes_from((5, 6, 7, 12))
    edges = [(6, 6), (7, 5), (7, 6), (7, 7), (12, 7), (12, 5), (12, 6)]
    basic_RG_v5.add_edges_from(edges)
    ###############################################

    # stupid code reduced garph
    stupid_RG = nx.DiGraph()
    stupid_RG.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_RG.add_edges_from(edges)

    # stupid_code_v1 reduced garph
    # variable renaming
    stupid_RG_v1 = nx.DiGraph()
    stupid_RG_v1.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_RG_v1.add_edges_from(edges)
    ###############################################

    # fork_code reduced garph
    # fork code
    fork_DG = nx.DiGraph()
    fork_DG.add_nodes_from(range(1, 7))
    edges = [(1, 2), (2, 3)]
    fork_DG.add_edges_from(edges)
    fork_RG = build_RG_from_DG(fork_DG)
    print(fork_RG)

    # fork_code_v1 reduced garph
    # junk code insertion
    fork_R1_RG = nx.DiGraph()
    fork_R1_RG.add_nodes_from(range(1, 15))
    edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
    fork_R1_RG.add_edges_from(edges)

    # basic-code tests
    def test_basic_code_vs_basic_code(self):
        """
        Calculates the fitness between basic-code to itself:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        actual_d = GA(self.basic_RG, self.basic_RG)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v1(self):
        """
        Calculates the fitness between basic-code to basic-code.v1:
        """
        actual_d = GA(self.basic_RG, self.basic_RG_v1)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v2(self):
        """
        Calculates the fitness between basic-code to basic-code.v2:
        """
        actual_d = GA(self.basic_RG, self.basic_RG_v2)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v3(self):
        """
        Calculates the fitness between basic-code to basic-code.v3:
        """
        actual_d = GA(self.basic_RG, self.basic_RG_v3)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v4(self):
        """
        Calculates the fitness between basic-code to basic-code.v4:
        """
        actual_d = GA(self.basic_RG, self.basic_RG_v4)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v5(self):
        """
        Calculates the fitness between basic-code to basic-code.v5:
        """
        actual_d = GA(self.basic_RG, self.basic_RG_v5)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_stupid_code(self):
        """
        Calculates the fitness between basic-code to stupid-code:
        """
        actual_d = GA(self.basic_RG, self.stupid_RG)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_basic_code_vs_stupid_code_v1(self):
        """
        Calculates the fitness between basic-code to stupid-code.v1:
        """
        actual_d = GA(self.basic_RG, self.stupid_RG_v1)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_basic_code_vs_fork_code(self):
        """
        Calculates the fitness between basic-code to fork-code:
        """
        actual_d = GA(self.basic_RG, self.fork_RG)
        expected_d = 7/2
        assert actual_d == expected_d

    def test_basic_code_vs_fork_code_v1(self):
        """
        Calculates the fitness between basic-code to fork-code.v1:
        """
        actual_d = GA(self.basic_RG, self.fork_R1_RG)
        expected_d = 8/7
        assert actual_d == expected_d

    # stupid-code tests

    def test_stupid_code_vs_basic_code_v1(self):
        """
        Calculates the fitness between stupid-code to basic-code.v1:
        """
        actual_d = GA(self.stupid_RG, self.basic_RG_v1)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v2(self):
        """
        Calculates the fitness between stupid-code to basic-code.v2:
        """
        actual_d = GA(self.stupid_RG, self.basic_RG_v2)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v3(self):
        """
        Calculates the fitness between stupid-code to basic-code.v3:
        """
        actual_d = GA(self.stupid_RG, self.basic_RG_v3)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v4(self):
        """
        Calculates the fitness between stupid-code to basic-code.v4:
        """
        actual_d = GA(self.stupid_RG, self.basic_RG_v4)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v5(self):
        """
        Calculates the fitness between stupid-code to basic-code.v5:
        """
        actual_d = GA(self.stupid_RG, self.basic_RG_v5)
        expected_d = 8/7
        assert actual_d == expected_d

    def test_stupid_code_vs_stupid_code(self):
        """
        Calculates the fitness between stupid-code to itself:
        """
        actual_d = GA(self.stupid_RG, self.stupid_RG)
        expected_d = 0
        assert actual_d == expected_d

    def test_stupid_code_vs_stupid_code_v1(self):
        """
        Calculates the fitness between stupid-code to stupid-code.v1:
        """
        actual_d = GA(self.stupid_RG, self.stupid_RG_v1)
        expected_d = 0
        assert actual_d == expected_d

    def test_stupid_code_vs_fork_code(self):
        """
        Calculates the fitness between stupid-code to fork-code:
        """
        actual_d = GA(self.stupid_RG, self.fork_RG)
        expected_d = 3/2
        assert actual_d == expected_d

    def test_stupid_code_vs_fork_code_v1(self):
        """
        Calculates the fitness between stupid-code to fork-code.v1:
        """
        actual_d = GA(self.stupid_RG, self.fork_R1_RG)
        expected_d = 4/3
        assert actual_d == expected_d
