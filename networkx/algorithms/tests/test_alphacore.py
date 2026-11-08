import warnings

import pytest

import networkx as nx
from networkx.algorithms.alphacore import alpha_core

# Skip this module entirely if NumPy isn’t available
np = pytest.importorskip("numpy")  # noqa: F401  (imported only for skip logic)


class TestAlphaCore:
    # ------------------------------------------------------------------ #
    # graph fixtures                                                     #
    # ------------------------------------------------------------------ #
    def setup_method(self):
        # Small directed graph with two numeric attributes
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

        # Larger random graph
        scale_free = nx.scale_free_graph(20, seed=42)
        self.H = nx.DiGraph()
        self.H.add_edges_from(scale_free.edges())
        for n in self.H:
            self.H.nodes[n]["f1"] = 0.1 * n
            self.H.nodes[n]["f2"] = 0.5 * n

    # ------------------------------------------------------------------ #
    # functional behaviour                                               #
    # ------------------------------------------------------------------ #
    @pytest.mark.parametrize("feat", [["f1"], ["f1", "f2"], ["all"], None])
    def test_feature_selection(self, feat):
        res = alpha_core(self.G, features=feat)
        assert isinstance(res, dict)
        assert len(res) == self.G.number_of_nodes()

    def test_parameter_variations(self):
        assert alpha_core(self.G, step_size=0.05) != alpha_core(self.G, step_size=0.2)
        assert alpha_core(self.G, expo_decay=False) != alpha_core(
            self.G, expo_decay=True
        )
        assert alpha_core(self.G, start_epsi=1.0) != alpha_core(self.G, start_epsi=0.5)

    def test_missing_features_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = alpha_core(self.G, features=["non_existent"])
        assert len(_) == self.G.number_of_nodes()
        assert any("missing values" in str(w_.message) for w_ in w)

    def test_covariance_warning(self):
        G = nx.DiGraph([(0, 1)])
        G.add_nodes_from([(0, {"f1": 1.0}), (1, {"f1": 1.0})])  # zero variance
        with warnings.catch_warnings(record=True) as w:
            alpha_core(G, features=["f1"])
        assert any("Covariance matrix is not invertible" in str(w_.message) for w_ in w)

    def test_unsupported_graph_type(self):
        with pytest.raises(nx.NetworkXNotImplemented):
            alpha_core(nx.Graph([(0, 1)]))

    def test_empty_graph(self):
        assert alpha_core(nx.DiGraph()) == {}

    def test_weighted_multigraph(self):
        MG = nx.MultiDiGraph()
        MG.add_weighted_edges_from([(0, 1, 1.5), (0, 1, 2.5), (1, 2, 3.0)])
        for n in MG:
            MG.nodes[n]["f1"] = float(n)
        res = alpha_core(MG)
        assert set(res) == set(MG)

    # ------------------------------------------------------------------ #
    # result schema / invariants                                         #
    # ------------------------------------------------------------------ #
    def test_result_schema(self):
        res = alpha_core(self.G)
        for nid, data in res.items():
            assert {"alpha", "batch_id"} <= data.keys()
            assert 0.0 <= data["alpha"] <= 1.0
            assert isinstance(data["batch_id"], int) and data["batch_id"] >= 0

    def test_batch_ordering(self):
        res = alpha_core(self.G)
        batch_ids = [d["batch_id"] for d in res.values()]
        assert sorted(batch_ids) == batch_ids  # non-decreasing

    # ------------------------------------------------------------------ #
    # performance smoke                                                  #
    # ------------------------------------------------------------------ #
    def test_large_graph_smoke(self):
        big = nx.gn_graph(1000, seed=1, create_using=nx.DiGraph)
        for n in big:
            big.nodes[n]["score"] = float(n)
        res = alpha_core(big, features=["score"], step_size=0.2)
        assert len(res) == big.number_of_nodes()

    # ------------------------------------------------------------------ #
    # internal feature-helper checks                                      #
    # ------------------------------------------------------------------ #
    def test_default_feature_consistency(self):
        """Every node must expose exactly the same feature keys."""
        import networkx.algorithms.alphacore as ac

        G = nx.DiGraph()
        G.add_weighted_edges_from([(0, 1, 2.0), (1, 2, 3.0), (2, 0, 4.0)])
        data = ac._compute_default_node_features(G)

        first_keys = set(next(iter(data.values())).keys())
        assert all(set(d.keys()) == first_keys for d in data.values())

    @pytest.mark.parametrize("with_weights", [False, True])
    def test_strength_column_presence(self, with_weights):
        """Strength columns appear iff at least one edge weight ≠ 1."""
        import networkx.algorithms.alphacore as ac

        G = nx.DiGraph()
        if with_weights:
            G.add_weighted_edges_from([(0, 1, 2.0), (1, 2, 1.0)])
        else:
            G.add_edges_from([(0, 1), (1, 2)])

        feats = ac._compute_default_node_features(G)
        cols = set(next(iter(feats.values())).keys())

        if with_weights:
            assert {"inStrength", "outStrength"} <= cols
        else:
            assert {"inStrength", "outStrength"}.isdisjoint(cols)
