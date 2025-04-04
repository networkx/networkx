import random

import pytest

import networkx as nx
from networkx.algorithms import modular_decomposition
from networkx.algorithms.modular import Node, NodeType


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
        assert isinstance(root, Node) and root.node_type == NodeType.PRIME

        expected = [
            (NodeType.PRIME, NodeType.SERIES),
            (NodeType.PRIME, NodeType.PARALLEL),
            (NodeType.PRIME, 4),
            (NodeType.PRIME, 8),
            (NodeType.SERIES, 0),
            (NodeType.SERIES, 1),
            (NodeType.SERIES, 2),
            (NodeType.SERIES, 3),
            (NodeType.PARALLEL, 5),
            (NodeType.PARALLEL, 6),
            (NodeType.PARALLEL, 7),
        ]

        edges = []
        for tail, head in tree.edges():
            if isinstance(tail, Node):
                tail = tail.node_type
            if isinstance(head, Node):
                head = head.node_type
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
            if isinstance(tail, Node):
                tail = tail.node_type
            if isinstance(head, Node):
                head = head.node_type
            edges1.append((tail, head))

        edges2 = []
        for tail, head in tree1.edges():
            if isinstance(tail, Node):
                tail = tail.node_type
            if isinstance(head, Node):
                head = head.node_type
            edges2.append((tail, head))

        assert set(edges1) == set(edges2)
