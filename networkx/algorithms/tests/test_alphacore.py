import warnings

import pytest

import networkx as nx
from networkx.algorithms.alphacore import alpha_core

# Use importorskip for optional dependencies
np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")


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
        multi_graph = nx.scale_free_graph(20, seed=42)
        self.H = nx.DiGraph()
        self.H.add_edges_from(multi_graph.edges())
        for n in self.H.nodes():
            self.H.nodes[n]["f1"] = 0.1 * n
            self.H.nodes[n]["f2"] = 0.5 * n

    def test_alpha_core_with_specific_features(self):
        """Test alpha_core with different feature selections."""
        # Test with single feature
        result_f1 = alpha_core(self.G, features=["f1"])
        assert isinstance(result_f1, pd.DataFrame)
        assert len(result_f1) == self.G.number_of_nodes()

        # Test with multiple features
        result_all = alpha_core(self.G, features=["f1", "f2"])
        assert isinstance(result_all, pd.DataFrame)
        assert len(result_all) == self.G.number_of_nodes()

    def test_alpha_core_parameters(self):
        """Test different parameter combinations."""
        # Test step sizes
        result1 = alpha_core(self.G, step_size=0.1)
        result2 = alpha_core(self.G, step_size=0.2)
        assert isinstance(result1, pd.DataFrame)
        assert isinstance(result2, pd.DataFrame)
        assert not result1.equals(result2)

        # Test exponential decay
        result_normal = alpha_core(self.G, expo_decay=False)
        result_decay = alpha_core(self.G, expo_decay=True)
        assert isinstance(result_normal, pd.DataFrame)
        assert isinstance(result_decay, pd.DataFrame)
        assert not result_normal.equals(result_decay)

        # Test start epsilon
        result_default = alpha_core(self.G, start_epsi=1.0)
        result_custom = alpha_core(self.G, start_epsi=0.5)
        assert isinstance(result_default, pd.DataFrame)
        assert isinstance(result_custom, pd.DataFrame)
        assert not result_default.equals(result_custom)

    def test_feature_error_handling(self):
        """Test error handling for invalid features."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = alpha_core(self.G, features=["non_existent_feature"])
            # Check for the warning about using default features
            assert any(
                "No node features found" in str(warning.message) for warning in w
            )
            # Check for the covariance matrix warning
            assert any(
                "Covariance matrix is not invertible" in str(warning.message)
                for warning in w
            )

        # Check the result is still valid
        assert isinstance(result, pd.DataFrame)
        assert len(result) == self.G.number_of_nodes()

    def test_graph_type_validation(self):
        """Test that appropriate errors are raised for unsupported graph types."""
        undirected_G = nx.Graph()
        undirected_G.add_edges_from([(0, 1), (1, 2), (2, 0)])
        for n in undirected_G.nodes():
            undirected_G.nodes[n]["f1"] = float(n) / 3

        with pytest.raises(nx.NetworkXNotImplemented):
            alpha_core(undirected_G)

    def test_empty_and_no_features(self):
        """Test empty graph and graph with no features."""
        # Empty graph
        empty_G = nx.DiGraph()
        result = alpha_core(empty_G)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

        # No features
        G_no_features = nx.DiGraph()
        G_no_features.add_edges_from([(0, 1), (1, 2), (2, 0)])
        with warnings.catch_warnings(record=True) as w:
            result = alpha_core(G_no_features)
            assert any(
                "No node features found" in str(warning.message) for warning in w
            )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == G_no_features.number_of_nodes()

    def test_multigraph_and_weighted(self):
        """Test multigraph and weighted graph support."""
        # Weighted multigraph
        weighted_multi_G = nx.MultiDiGraph()
        weighted_multi_G.add_weighted_edges_from(
            [(0, 1, 1.5), (0, 1, 2.5), (1, 2, 3.0), (2, 0, 1.0)]
        )
        for n in weighted_multi_G.nodes():
            weighted_multi_G.nodes[n]["f1"] = float(n) / 2

        result = alpha_core(weighted_multi_G)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == weighted_multi_G.number_of_nodes()
        assert set(result["nodeID"]) == set(weighted_multi_G.nodes())

    def test_covariance_matrix_warnings(self):
        """Test warnings for non-invertible covariance matrix."""
        G = nx.DiGraph()
        G.add_nodes_from([(0, {"f1": 1.0}), (1, {"f1": 1.0})])
        G.add_edge(0, 1)

        with warnings.catch_warnings(record=True) as w:
            result = alpha_core(G, features=["f1"])
            assert any(
                "Covariance matrix is not invertible" in str(warning.message)
                for warning in w
            )
        assert isinstance(result, pd.DataFrame)

    def test_feature_validation(self):
        """Test feature validation and error handling."""
        # Test with empty feature list
        with warnings.catch_warnings(record=True) as w:
            result = alpha_core(self.G, features=[])
            assert any(
                "No node features found" in str(warning.message) for warning in w
            )

        # Test with None and ["all"] features
        result = alpha_core(self.G, features=None)
        assert isinstance(result, pd.DataFrame)
        result = alpha_core(self.G, features=["all"])
        assert isinstance(result, pd.DataFrame)

    def test_performance_and_ci(self):
        """Test performance with larger graphs and CI-specific cases."""
        # Large graph
        G_large = nx.DiGraph()
        for i in range(100):
            G_large.add_node(i, f1=float(i))
        for i in range(99):
            G_large.add_edge(i, i + 1)

        result = alpha_core(G_large)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100

        # CI-specific minimal graph
        G_min = nx.DiGraph()
        G_min.add_nodes_from([(0, {"f1": 1.0}), (1, {"f1": 2.0})])
        G_min.add_edge(0, 1)

        result = alpha_core(G_min)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_backend_compatibility(self):
        """Test compatibility with different backends."""
        result = alpha_core(self.G)
        assert isinstance(result, pd.DataFrame)

        multi_G = nx.MultiDiGraph(self.G)
        result = alpha_core(multi_G)
        assert isinstance(result, pd.DataFrame)
