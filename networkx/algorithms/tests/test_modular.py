import random

import pytest

import networkx as nx
from networkx.algorithms import modular_decomposition


class TestModularDecomposition:
    """Test modular decomposition.

    Example graph taken from [1]_, chapter 3.

    .. [1] Goeppel, Luis. "Efficient Implementation of Modular Graph Decomposition."
    """

    def _get_example_graph(self):
        g = nx.Graph()
        g.add_edges_from(
            [
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 3),
                (2, 4),
                (3, 4),
                (4, 5),
                (4, 6),
                (4, 7),
                (5, 8),
                (6, 8),
                (7, 8),
            ]
        )
        return g

    def test_modular_decomposition(self):
        g = self._get_example_graph()
        tree, root = modular_decomposition(g)

        #
        # Make sure the root node is PRIME.
        #
        assert tree.nodes[root]["type"] == "prime"

        expected = [
            ("prime", "series"),
            ("prime", "parallel"),
            ("prime", 4),
            ("prime", 8),
            ("series", 0),
            ("series", 1),
            ("series", 2),
            ("series", 3),
            ("parallel", 5),
            ("parallel", 6),
            ("parallel", 7),
        ]

        edges = []
        for tail, head in tree.edges():
            tail_type = tree.nodes[tail]["type"]
            if tail_type != "leaf":
                tail = tail_type
            head_type = tree.nodes[head]["type"]
            if head_type != "leaf":
                head = head_type
            edges.append((tail, head))

        #
        # Make sure actual edges match the expected edges.
        #
        assert set(expected) == set(edges)

    def test_modular_decomposition_pivot_picker(self):
        #
        # Pivot picker that picks a random graph node. Modular decomposition
        # result should not be affected.
        #
        def _pivot_picker(g):
            return random.choice(list(g))

        g = self._get_example_graph()
        tree1, root1 = modular_decomposition(g)
        tree2, root2 = modular_decomposition(g, pivot_picker=_pivot_picker)

        edges1 = []
        for tail, head in tree1.edges():
            tail_type = tree1.nodes[tail]["type"]
            if tail_type != "leaf":
                tail = tail_type
            head_type = tree1.nodes[head]["type"]
            if head_type != "leaf":
                head = head_type
            edges1.append((tail, head))

        edges2 = []
        for tail, head in tree2.edges():
            tail_type = tree2.nodes[tail]["type"]
            if tail_type != "leaf":
                tail = tail_type
            head_type = tree2.nodes[head]["type"]
            if head_type != "leaf":
                head = head_type
            edges2.append((tail, head))

        assert set(edges1) == set(edges2)
