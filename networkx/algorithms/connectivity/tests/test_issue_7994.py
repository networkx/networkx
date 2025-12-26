"""Tests for issue #7994 - all_node_cuts correctness fixes

This addresses the correctness bugs reported in #7994:
- Single node graph returning [set()] instead of []
- Two connected nodes handling

Note: The performance degradation issue (antichain explosion on larger
graphs like 8x8+) is a deeper algorithmic problem that requires
further investigation and is tracked in issue #7994.
"""

import pytest

import networkx as nx


class TestIssue7994:
    """Test fixes for all_node_cuts() issue #7994"""

    def test_single_node_graph_returns_empty(self):
        """Single node graph should return empty generator, not [set()]

        This was the specific bug reported: a single node graph was
        returning [set()] instead of [].
        """
        G = nx.Graph()
        G.add_node(1)
        result = list(nx.all_node_cuts(G))
        assert result == [], f"Expected [], got {result}"

    def test_two_connected_nodes_returns_empty(self):
        """Two connected nodes should return empty

        Neighbors cannot form a valid cut between each other.
        """
        G = nx.Graph([(1, 2)])
        result = list(nx.all_node_cuts(G))
        assert result == [], f"Expected [], got {result}"

    def test_complete_graph_returns_empty(self):
        """Complete graphs should return empty

        Complete graphs cannot be disconnected by removing nodes.
        """
        G = nx.complete_graph(5)
        result = list(nx.all_node_cuts(G))
        assert result == [], f"Expected [], got {result}"

    def test_path_graph_returns_middle_node(self):
        """Path graph should return middle node as cut"""
        G = nx.Graph([(1, 2), (2, 3)])
        result = list(nx.all_node_cuts(G))
        assert result == [{2}], f"Expected [{{2}}], got {result}"

    def test_small_grid_graph(self):
        """Test that small grid graphs work correctly

        4x4 grid should find 4 corner cuts.
        """
        G = nx.grid_2d_graph(4, 4)
        cuts = list(nx.all_node_cuts(G))
        assert len(cuts) == 4, f"Expected 4 cuts, got {len(cuts)}"

    def test_disconnected_graph_raises_error(self):
        """Disconnected graphs should raise NetworkXError"""
        G = nx.Graph()
        G.add_edges_from([(1, 2), (3, 4)])  # Two components

        with pytest.raises(nx.NetworkXError, match="Input graph is disconnected"):
            list(nx.all_node_cuts(G))
