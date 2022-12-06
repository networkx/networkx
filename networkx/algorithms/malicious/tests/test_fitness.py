"""
    Tests for fitness.
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.fitness import calculate_fitness


class TestFitnessFunction:
    # basic_code reduced garph
    basic_RG = nx.diGraph()
    basic_RG.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG.add_edges_from(edges)

    # basic_code_v1 reduced garph
    # Variable renaming
    basic_RG_v1 = nx.diGraph()
    basic_RG_v1.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v1.add_edges_from(edges)

    # basic_code_v2 reduced garph
    # Statement reordering
    basic_RG_v2 = nx.diGraph()
    basic_RG_v2.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v2.add_edges_from(edges)

    # basic_code_v3 reduced garph
    # Format alternation
    basic_RG_v3 = nx.diGraph()
    basic_RG_v3.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v3.add_edges_from(edges)

    # basic_code_v4 reduced garph
    # Statement replacement
    basic_RG_v4 = nx.diGraph()
    basic_RG_v4.add_nodes_from(range(6, 10))
    edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    basic_RG_v4.add_edges_from(edges)

    # basic_code_v5 reduced garph
    # Spaghetti code
    basic_RG_v5 = nx.diGraph()
    basic_RG_v5.add_nodes_from((5, 6, 7, 12))
    edges = [(6, 6), (7, 5), (7, 6), (7, 7), (12, 7), (12, 5), (12, 6)]
    basic_RG_v5.add_edges_from(edges)
    ###############################################

    # stupid code reduced garph
    stupid_RG = nx.diGraph()
    stupid_RG.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_RG.add_edges_from(edges)

    # stupid_code_v1 reduced garph
    # variable renaming
    stupid_RG_v1 = nx.diGraph()
    stupid_RG_v1.add_nodes_from(range(1, 7))
    edges = [(1, 4), (2, 5), (3, 6)]
    stupid_RG_v1.add_edges_from(edges)
    ###############################################

    # fork_code reduced garph
    # fork code
    fork_RG = nx.diGraph()
    fork_RG.add_nodes_from(range(1, 7))
    edges = [(1, 2), (2, 3)]
    fork_RG.add_edges_from(edges)

    # fork_code_v1 reduced garph
    # junk code insertion
    fork_R1_RG = nx.diGraph()
    fork_R1_RG.add_nodes_from(range(1, 15))
    edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
    fork_R1_RG.add_edges_from(edges)

    # basic-code tests
    def test_basic_code_vs_basic_code(self):
        """
        Calculates the fitness between basic-code to itself:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v1(self):
        """
        Calculates the fitness between basic-code to basic-code.v1:
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v1)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v2(self):
        """
        Calculates the fitness between basic-code to basic-code.v2:
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v2)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v3(self):
        """
        Calculates the fitness between basic-code to basic-code.v3:
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v3)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v4(self):
        """
        Calculates the fitness between basic-code to basic-code.v4:
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v4)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_basic_code_v5(self):
        """
        Calculates the fitness between basic-code to basic-code.v5:
        """
        actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v5)
        expected_d = 0
        assert actual_d == expected_d

    def test_basic_code_vs_stupid_code(self):
        """
        Calculates the fitness between basic-code to stupid-code:
        """
        actual_d = calculate_fitness(self.basic_RG, self.stupid_RG)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_basic_code_vs_stupid_code_v1(self):
        """
        Calculates the fitness between basic-code to stupid-code.v1:
        """
        actual_d = calculate_fitness(self.basic_RG, self.stupid_RG_v1)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_basic_code_vs_fork_code(self):
        """
        Calculates the fitness between basic-code to fork-code:
        """
        actual_d = calculate_fitness(self.basic_RG, self.fork_RG)
        expected_d = 5/2
        assert actual_d == expected_d

    def test_basic_code_vs_fork_code_v1(self):
        """
        Calculates the fitness between basic-code to fork-code.v1:
        """
        actual_d = calculate_fitness(self.basic_RG, self.fork_R1_RG)
        expected_d = 3/7
        assert actual_d == expected_d


    # stupid-code tests
    def test_stupid_code_vs_basic_code_v1(self):
        """
        Calculates the fitness between stupid-code to basic-code.v1:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.basic_RG_v1)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v2(self):
        """
        Calculates the fitness between stupid-code to basic-code.v2:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.basic_RG_v2)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v3(self):
        """
        Calculates the fitness between stupid-code to basic-code.v3:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.basic_RG_v3)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v4(self):
        """
        Calculates the fitness between stupid-code to basic-code.v4:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.basic_RG_v4)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_stupid_code_vs_basic_code_v5(self):
        """
        Calculates the fitness between stupid-code to basic-code.v5:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.basic_RG_v5)
        expected_d = 10/7
        assert actual_d == expected_d

    def test_stupid_code_vs_stupid_code(self):
        """
        Calculates the fitness between stupid-code to itself:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.stupid_RG)
        expected_d = 0
        assert actual_d == expected_d

    def test_stupid_code_vs_stupid_code_v1(self):
        """
        Calculates the fitness between stupid-code to stupid-code.v1:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.stupid_RG_v1)
        expected_d = 0
        assert actual_d == expected_d

    def test_stupid_code_vs_fork_code(self):
        """
        Calculates the fitness between stupid-code to fork-code:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.fork_RG)
        expected_d = 1
        assert actual_d == expected_d

    def test_stupid_code_vs_fork_code_v1(self):
        """
        Calculates the fitness between stupid-code to fork-code.v1:
        """
        actual_d = calculate_fitness(self.stupid_RG, self.fork_R1_RG)
        expected_d = 4/3
        assert actual_d == expected_d

# TODO: change the variavles in the func
    # # fork-code tests
    # def test_stupid_fork_vs_basic_code_v1(self):
    #     """
    #     Calculates the fitness between fork-code to basic-code.v1:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v1)
    #     expected_d = 11
    #     assert actual_d == expected_d

    # def test_stupid_fork_vs_basic_code_v2(self):
    #     """
    #     Calculates the fitness between fork-code to basic-code.v2:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v2)
    #     expected_d = 10/7
    #     assert actual_d == expected_d

    # def test_fork_code_vs_basic_code_v3(self):
    #     """
    #     Calculates the fitness between fork-code to basic-code.v3:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v3)
    #     expected_d = 10/7
    #     assert actual_d == expected_d

    # def test_fork_code_vs_basic_code_v4(self):
    #     """
    #     Calculates the fitness between fork-code to basic-code.v4:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v4)
    #     expected_d = 10/7
    #     assert actual_d == expected_d

    # def test_fork_code_vs_basic_code_v5(self):
    #     """
    #     Calculates the fitness between fork-code to basic-code.v5:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.basic_RG_v5)
    #     expected_d = 10/7
    #     assert actual_d == expected_d

    # def test_fork_code_vs_stupid_code(self):
    #     """
    #     Calculates the fitness between fork-code to stupid-code:
    #     """
    #     actual_d = calculate_fitness(self.basic_RG, self.stupid_RG)
    #     expected_d = 0
    #     assert actual_d == expected_d

    # def test_fork_code_vs_stupid_code_v1(self):
    #     """
    #     Calculates the fitness between fork-code to stupid-code.v1:
    #     """
    #     actual_d = calculate_fitness(self.stupid_RG, self.stupid_RG_v1)
    #     expected_d = 0
    #     assert actual_d == expected_d

    # def test_fork_code_vs_fork_code(self):
    #     """
    #     Calculates the fitness between fork-code to itself:
    #     """
    #     actual_d = calculate_fitness(self.stupid_RG, self.stupid_RG_v1)
    #     expected_d = 1
    #     assert actual_d == expected_d

    # def test_fork_code_vs_fork_code_v1(self):
    #     """
    #     Calculates the fitness between fork-code to fork-code.v1:
    #     """
    #     actual_d = calculate_fitness(self.stupid_RG, self.stupid_RG_v1)
    #     expected_d = 4/3
    #     assert actual_d == expected_d




