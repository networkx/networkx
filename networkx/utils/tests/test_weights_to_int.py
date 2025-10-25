"""Test suite for functions related to scaling edge weights to integers."""

import math
from fractions import Fraction

import networkx as nx
from networkx.utils.weights_to_int import (
    choose_scale_factor,
    needs_integerization,
    scale_edge_weight_to_ints,
)


class TestNeedsIntegerization:
    def test_needs_integerization_false_for_integers_and_exact_types(self):
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=1)  # int
        G.add_edge("b", "c", weight=2.0)  # float but integral
        G.add_edge("c", "d", weight=Fraction(3, 4))  # exact rational
        G.add_edge("d", "e")  # missing weight
        assert needs_integerization(G, weight="weight") is False

    def test_needs_integerization_true_for_non_integral_floats(self):
        G = nx.DiGraph()
        G.add_edge("s", "a", weight=0.3)
        G.add_edge("a", "t", weight=1.25)
        assert needs_integerization(G, weight="weight") is True

    def test_needs_integerization_skips_infinities_and_nans(self):
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=float("inf"))
        G.add_edge("b", "c", weight=float("-inf"))
        G.add_edge("c", "d", weight=float("nan"))
        # No other non-integral finite floats present; should not force scaling
        assert needs_integerization(G, weight="weight") is False


class TestChooseScaleFactor:
    def test_choose_scale_factor_lcm_of_denominators_basic(self):
        # 0.25 -> 1/4, 0.1 -> 1/10  => LCM(4,10)=20
        G = nx.DiGraph()
        G.add_edge("s", "a", weight=0.25)
        G.add_edge("a", "t", weight=0.1)
        K = choose_scale_factor(
            G, weight="weight", max_denominator=10**6, max_scale_factor=10**12
        )
        assert K == 20

    def test_choose_scale_factor_ignores_integers_and_missing_and_infinities(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=2.0)  # integral; should not affect K
        G.add_edge(2, 3)  # missing -> default/inf semantics; ignore
        G.add_edge(3, 4, weight=float("inf"))  # ignore
        G.add_edge(4, 5, weight=3)  # int; ignore
        K = choose_scale_factor(G, weight="weight")
        assert K == 1

    def test_choose_scale_factor_respects_caps(self):
        G = nx.DiGraph()
        # Make a set that would suggest a large LCM
        G.add_edge("u", "v", weight=0.2)  # 1/5
        G.add_edge("v", "w", weight=0.125)  # 1/8
        G.add_edge("w", "x", weight=42)  # int; ignore
        # LCM(5,8)=40 normally, but cap at 10
        K = choose_scale_factor(
            G, weight="weight", max_denominator=10**6, max_scale_factor=10
        )
        assert K == 10


class TestScaleEdgeWeightToInts:
    def test_scale_edge_weight_to_ints_preserves_graph_type_and_copies(self):
        # Works for Graph/DiGraph/MultiDiGraph; here we check a MultiDiGraph case
        MG = nx.MultiDiGraph()
        MG.add_edge("s", "a", key="k1", weight=0.3)
        MG.add_edge("s", "a", key="k2", weight=0.1)
        MG.add_edge("a", "t", key="k3", weight=1.0)

        K = 10  # scale by 10
        H = scale_edge_weight_to_ints(
            MG, weight="weight", scale_factor=K, default_value=None
        )

        # Type preserved
        assert isinstance(H, nx.MultiDiGraph)

        # Original graph is unchanged
        assert MG["s"]["a"]["k1"]["weight"] == 0.3

        # Each parallel edge scaled independently (keys=True iteration required by impl)
        assert H["s"]["a"]["k1"]["weight"] == int(round(0.3 * K))  # 3
        assert H["s"]["a"]["k2"]["weight"] == int(round(0.1 * K))  # 1
        assert H["a"]["t"]["k3"]["weight"] == int(round(1.0 * K))  # 10

    def test_scale_edge_weight_to_ints_handles_missing_weights_with_default(self):
        G = nx.DiGraph()
        G.add_edge(1, 2, weight=0.25)
        G.add_edge(2, 3)  # missing
        H = scale_edge_weight_to_ints(
            G, weight="weight", scale_factor=20, default_value=42
        )
        # 0.25 * 20 = 5
        assert H[1][2]["weight"] == 5
        # default_value=42 -> 42 * 20 = 840
        assert H[2][3]["weight"] == 840

    def test_scale_edge_weight_to_ints_flips_infinity_signs(self):
        G = nx.Graph()
        G.add_edge("x", "y", weight=float("inf"))
        G.add_edge("y", "z", weight=float("-inf"))
        G.add_edge("z", "w", weight=float("nan"))
        G.add_edge("x", "w", weight=0)
        # negative scale factor to flip signs of infinities
        H = scale_edge_weight_to_ints(
            G, weight="weight", scale_factor=-10, default_value=None
        )
        assert math.isinf(H["x"]["y"]["weight"]) and H["x"]["y"]["weight"] < 0
        assert math.isinf(H["y"]["z"]["weight"]) and H["y"]["z"]["weight"] > 0
        assert math.isnan(H["z"]["w"]["weight"])
        assert H["x"]["w"]["weight"] == 0

    def test_scale_edge_weight_to_ints_rounds_to_nearest_int(self):
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=0.149)  # *100 => 14.9 -> round -> 15
        H = scale_edge_weight_to_ints(
            G, weight="weight", scale_factor=100, default_value=None
        )
        assert H["a"]["b"]["weight"] == 15

    def test_end_to_end_integerization_workflow_example(self):
        # If any non-integral finite float is present, needs_integerization triggers,
        # choose_scale_factor picks a sane K, and scaler converts weights to ints.
        G = nx.DiGraph()
        G.add_edge("s", "a", weight=0.256)  # 256/1000 = 64/250
        G.add_edge("a", "t", weight=0.33)  # 33/100

        assert needs_integerization(G, weight="weight") is True
        K = choose_scale_factor(G, weight="weight")
        assert K == 500  # LCM(250,100)=500

        H = scale_edge_weight_to_ints(
            G, weight="weight", scale_factor=K, default_value=None
        )
        assert H["s"]["a"]["weight"] == int(round(0.256 * K))
        assert H["a"]["t"]["weight"] == int(round(0.33 * K))
