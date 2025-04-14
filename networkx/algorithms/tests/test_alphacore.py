import numpy as np
import pandas as pd
import pytest

import networkx as nx
from networkx.algorithms.alphacore import alpha_core


class TestAlphaCore:
    def setup_method(self):
        # Create a simple directed graph for testing
        self.G = nx.DiGraph()
        self.G.add_nodes_from(
            [
                (0, {"f1": 0.2, "f2": 1.0}),
                (1, {"f1": 0.7, "f2": 2.0}),
                (2, {"f1": 0.5, "f2": 3.0}),
                (3, {"f1": 0.9, "f2": 4.0}),
            ]
        )
        self.G.add_edges_from([(0, 1), (1, 2), (2, 0), (2, 3)])

        # Create a larger graph for testing
        # Convert MultiDiGraph to DiGraph
        multi_graph = nx.scale_free_graph(20, seed=42)
        self.H = nx.DiGraph()
        # Add all edges from the multigraph to the regular digraph
        self.H.add_edges_from(multi_graph.edges())
        # Add some numeric features to nodes
        for n in self.H.nodes():
            self.H.nodes[n]["f1"] = 0.1 * n
            self.H.nodes[n]["f2"] = 0.5 * n

    def test_alpha_core_basic(self):
        """Test basic functionality of alpha_core."""
        result = alpha_core(self.G)

        # Check result is DataFrame with expected columns
        assert isinstance(result, pd.DataFrame)
        assert set(result.columns) == {"nodeID", "alpha", "batchID"}

        # Check all nodes get a ranking
        assert len(result) == self.G.number_of_nodes()
        assert set(result["nodeID"]) == set(self.G.nodes())

        # Alpha values should be in [0,1]
        assert all(0 <= a <= 1 for a in result["alpha"])

    def test_alpha_core_with_specific_features(self):
        """Test alpha_core with specific feature selection."""
        # Test with a single feature
        result_f1 = alpha_core(self.G, features=["f1"])
        assert isinstance(result_f1, pd.DataFrame)
        assert len(result_f1) == self.G.number_of_nodes()

        # Test with multiple features
        result_all = alpha_core(self.G, features=["f1", "f2"])
        assert isinstance(result_all, pd.DataFrame)
        assert len(result_all) == self.G.number_of_nodes()

        # Results should be different when using different feature sets
        # (Note: they could be the same by chance, but unlikely)
        alpha_f1 = set(result_f1["alpha"])
        alpha_all = set(result_all["alpha"])
        assert alpha_f1 != alpha_all

    def test_alpha_core_parameters(self):
        """Test alpha_core with different parameter settings."""
        # Test with different step sizes
        result1 = alpha_core(self.G, step_size=0.1)
        result2 = alpha_core(self.G, step_size=0.2)

        # Different step sizes should (usually) give different results
        assert set(result1["alpha"]) != set(result2["alpha"])

        # Test with different starting epsilon
        result3 = alpha_core(self.G, start_epsi=0.5)
        result4 = alpha_core(self.G, start_epsi=1.0)

        # Different starting epsilon should (usually) give different results
        assert set(result3["alpha"]) != set(result4["alpha"])

        # Test with expo_decay=True
        result5 = alpha_core(self.G, expo_decay=True)
        assert isinstance(result5, pd.DataFrame)
        assert len(result5) == self.G.number_of_nodes()

    def test_larger_graph(self):
        """Test alpha_core on a larger graph."""
        result = alpha_core(self.H)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == self.H.number_of_nodes()
        assert set(result["nodeID"]) == set(self.H.nodes())

    def test_feature_error_handling(self):
        """Test error handling for invalid features."""
        # Test with non-existent feature
        with pytest.raises(ValueError):
            alpha_core(self.G, features=["non_existent_feature"])

    def test_graph_type_validation(self):
        """Test that appropriate errors are raised for unsupported graph types."""
        # Create an undirected graph (should raise error because algorithm is only for directed graphs)
        undirected_G = nx.Graph()
        undirected_G.add_edges_from([(0, 1), (1, 2), (2, 0)])

        # Add node attributes
        for n in undirected_G.nodes():
            undirected_G.nodes[n]["f1"] = float(n) / 3

        # Should raise NetworkXNotImplemented for undirected graphs
        with pytest.raises(nx.NetworkXNotImplemented):
            alpha_core(undirected_G)

    def test_empty_graph(self):
        """Test alpha_core on an empty graph."""
        empty_G = nx.DiGraph()
        result = alpha_core(empty_G)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Should return empty DataFrame

    def test_graph_with_no_features(self):
        """Test alpha_core on a graph with no node features."""
        G_no_features = nx.DiGraph()
        G_no_features.add_edges_from([(0, 1), (1, 2), (2, 0)])

        # Should compute default features internally
        result = alpha_core(G_no_features)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == G_no_features.number_of_nodes()

    def test_consistency(self):
        """Test that alpha_core gives consistent results for the same input."""
        result1 = alpha_core(self.G, features=["f1"])
        result2 = alpha_core(self.G, features=["f1"])

        # Dataframes should be identical
        pd.testing.assert_frame_equal(result1, result2)

    def test_multigraph_support(self):
        """Test that alpha_core works with directed multigraphs."""
        # Create a directed multigraph
        multi_G = nx.MultiDiGraph()
        multi_G.add_edges_from([(0, 1), (0, 1), (1, 2), (2, 0)])

        # Add node attributes
        for n in multi_G.nodes():
            multi_G.nodes[n]["f1"] = float(n) / 3

        # Should work with multigraphs
        result = alpha_core(multi_G)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == multi_G.number_of_nodes()

        # Check all nodes get a ranking
        assert set(result["nodeID"]) == set(multi_G.nodes())

    def test_weighted_multigraph(self):
        """Test alpha_core on a weighted directed multigraph."""
        # Create a weighted directed multigraph
        weighted_multi_G = nx.MultiDiGraph()
        weighted_multi_G.add_weighted_edges_from(
            [
                (0, 1, 1.5),
                (0, 1, 2.5),  # Multiple edges between same nodes
                (1, 2, 3.0),
                (2, 0, 1.0),
            ]
        )

        # Add node attributes
        for n in weighted_multi_G.nodes():
            weighted_multi_G.nodes[n]["f1"] = float(n) / 2

        result = alpha_core(weighted_multi_G)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == weighted_multi_G.number_of_nodes()
        assert set(result["nodeID"]) == set(weighted_multi_G.nodes())
