"""
    Tests for genetic_algorithm.
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.genetic_algorithm import two_vertex_exchange_heuristic, vertex_relocation_heuristic

def is_equal(G1, G2):
    return G1.nodes == G2.nodes and G1.edges == G2.edges

class TestVertexExchange:
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


    def test_exchange_basic_code(self):
        # exchange vertecies 7 and 8 
        expected_G = nx.diGraph()
        nodes = [6, 8, 7, 9]
        expected_G.add_nodes_from(nodes)
        edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
        expected_G.add_edges_from(edges)
        actual_graph = two_vertex_exchange_heuristic(self.basic_RG)

        assert is_equal(expected_G, actual_graph)

    def test_exchange_basic_code_v5(self):
        # exchange vertecies 7 and 5
        expected_G = nx.diGraph()
        nodes = [7, 6, 5, 12]
        expected_G.add_nodes_from(nodes)
        edges = [(6, 6), (7, 5), (7, 6), (7, 7), (12, 7), (12, 5), (12, 6)]
        expected_G.add_edges_from(edges)
        actual_graph = two_vertex_exchange_heuristic(self.basic_RG_v5)

        assert is_equal(expected_G, actual_graph)

    def test_exchange_stupid_code(self):
        # exchange vertecies 3 and 4
        expected_G = nx.diGraph()
        nodes = [1, 2, 5, 3, 5, 6]
        expected_G.add_nodes_from(nodes)
        edges = [(1, 4), (2, 5), (3, 6)]
        expected_G.add_edges_from(edges)
        actual_graph = two_vertex_exchange_heuristic(self.stupid_RG)

        assert is_equal(expected_G, actual_graph)


class TestVertexRelocation:
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

    def test_exchange_basic_code(self):
        # relocate vertex 6 to the last index
        expected_G = nx.diGraph()
        nodes = [7, 8, 9, 6]
        expected_G.add_nodes_from(nodes)
        edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
        expected_G.add_edges_from(edges)
        actual_graph = vertex_relocation_heuristic(self.basic_RG)

        assert is_equal(expected_G, actual_graph)

    def test_exchange_basic_code_v5(self):
        # relocate 7 to the last index
        expected_G = nx.diGraph()
        nodes = [5, 6, 12, 7]
        expected_G.add_nodes_from(nodes)
        edges = [(6, 6), (7, 5), (7, 6), (7, 7), (12, 7), (12, 5), (12, 6)]
        expected_G.add_edges_from(edges)
        actual_graph = vertex_relocation_heuristic(self.basic_RG_v5)

        assert is_equal(expected_G, actual_graph)

        # relocate 5 to the last index
    def test_exchange_stupid_code(self):
        expected_G = nx.diGraph()
        nodes = [1, 2, 3, 4, 6 ,5]
        expected_G.add_nodes_from(nodes)
        edges = [(1, 4), (2, 5), (3, 6)]
        expected_G.add_edges_from(edges)
        actual_graph = vertex_relocation_heuristic(self.stupid_RG)

        assert is_equal(expected_G, actual_graph)
