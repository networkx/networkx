"""Independent exact checks for the #4936 assortativity numerical refactor."""

from decimal import Decimal, localcontext
from fractions import Fraction
import math
import random

import networkx as nx
import numpy as np
import pytest


def _fraction(value):
    if hasattr(value, "as_integer_ratio"):
        return Fraction(*value.as_integer_ratio())
    return Fraction(int(value))


def _exact_correlation(pairs):
    """Raw moments evaluated in exact rational arithmetic, then decimal sqrt."""
    if not pairs:
        return float("nan")
    xs, ys = zip(*pairs)
    xs = list(map(_fraction, xs))
    ys = list(map(_fraction, ys))
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    vx = n * sum(x * x for x in xs) - sx * sx
    vy = n * sum(y * y for y in ys) - sy * sy
    cov = n * sum(x * y for x, y in zip(xs, ys)) - sx * sy
    if not vx or not vy:
        return float("nan")
    with localcontext() as context:
        context.prec = 90

        def dec(value):
            return Decimal(value.numerator) / Decimal(value.denominator)

        return float(dec(cov) / (dec(vx) * dec(vy)).sqrt())


def _numeric_pairs(G, attribute, nodes=None):
    selected = set(G) if nodes is None else set(nodes)
    support = {G.nodes[u][attribute] for u in selected}
    pairs = []
    for u, v in G.edges():
        x, y = G.nodes[u][attribute], G.nodes[v][attribute]
        if u in selected and y in support:
            pairs.append((x, y))
        if not G.is_directed() and u != v and v in selected and x in support:
            pairs.append((y, x))
    return pairs


def _degree_pairs(G, x, y, weight, nodes=None):
    selected = set(G) if nodes is None else set(nodes)
    if G.is_directed():
        degree = {"in": G.in_degree, "out": G.out_degree}
        xd, yd = degree[x], degree[y]
    else:
        xd = yd = G.degree
    pairs = []
    for u, v in G.edges():
        if u in selected and v in selected:
            pairs.append((xd(u, weight=weight), yd(v, weight=weight)))
            if not G.is_directed() and u != v:
                pairs.append((xd(v, weight=weight), yd(u, weight=weight)))
    return pairs


def _assert_same(actual, expected):
    assert type(actual) is float
    if math.isnan(expected):
        assert math.isnan(actual)
    else:
        assert actual == pytest.approx(expected, rel=4e-14, abs=4e-15)


@pytest.mark.parametrize(
    "values",
    [
        [0, 1, 2, 3],
        [10**12 + i for i in range(4)],
        [10**12 + float(i) for i in range(4)],
        [np.int64(2**62 + i) for i in range(4)],
        [np.uint64(2**63 + i) for i in range(4)],
        [10**400 + i for i in range(4)],
        [i * 5e-324 for i in range(4)],
        [-1e308, 0.0, 1e308, 5e307],
        [np.bool_(v) for v in [False, True, True, False]],
        [np.float32(i) for i in range(4)],
        [np.longdouble(i) for i in range(4)],
    ],
)
def test_numeric_extreme_finite_values(values, request):
    if request.config.backend == "nx_loopback" and any(
        isinstance(v, np.number) for v in values
    ):
        pytest.skip("Loopback rejects NumPy scalars yielded by node_attribute_xy")
    G = nx.path_graph(4)
    nx.set_node_attributes(G, dict(enumerate(values)), "value")
    actual = nx.numeric_assortativity_coefficient(G, "value")
    _assert_same(actual, _exact_correlation(_numeric_pairs(G, "value")))


@pytest.mark.parametrize("graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph])
@pytest.mark.parametrize("seed", range(8))
def test_numerical_metrics_against_exact_edge_reference(graph_type, seed):
    rng = random.Random(seed)
    G = graph_type()
    G.add_nodes_from(range(9))
    for _ in range(23):
        G.add_edge(rng.randrange(8), rng.randrange(8), strength=rng.randrange(-7, 11) / 4)
    nx.set_node_attributes(G, {u: rng.randrange(-9, 10) / 3 for u in G}, "value")
    for nodes in (None, [0, 2, 4, 6, 8], [1, 3], []):
        expected = _exact_correlation(_numeric_pairs(G, "value", nodes))
        _assert_same(nx.numeric_assortativity_coefficient(G, "value", nodes), expected)
        if nodes is not None:
            _assert_same(
                nx.numeric_assortativity_coefficient(G, "value", iter(nodes)), expected
            )
        directions = [("out", "in"), ("in", "out"), ("in", "in"), ("out", "out")]
        for x, y in directions if G.is_directed() else directions[:1]:
            for weight in (None, "strength"):
                expected = _exact_correlation(_degree_pairs(G, x, y, weight, nodes))
                _assert_same(
                    nx.degree_assortativity_coefficient(G, x=x, y=y, weight=weight, nodes=nodes),
                    expected,
                )
                if nodes is not None:
                    _assert_same(
                        nx.degree_assortativity_coefficient(
                            G, x=x, y=y, weight=weight, nodes=iter(nodes)
                        ),
                        expected,
                    )


def test_numeric_subset_preserves_attribute_support():
    # Only source nodes 0 and 1 are selected. Target 2 shares a selected value
    # and is retained; target 3 has an unselected value and is excluded.
    G = nx.DiGraph([(0, 1), (1, 0), (0, 2), (1, 3)])
    nx.set_node_attributes(G, {0: 1, 1: 2, 2: 1, 3: 100}, "value")
    expected = _exact_correlation([(1, 2), (2, 1), (1, 1)])
    _assert_same(nx.numeric_assortativity_coefficient(G, "value", [0, 1]), expected)


@pytest.mark.parametrize("G", [nx.empty_graph(3), nx.cycle_graph(4), nx.Graph([(0, 0)])])
def test_undefined_correlations(G):
    nx.set_node_attributes(G, 7, "value")
    assert math.isnan(nx.degree_assortativity_coefficient(G))
    assert math.isnan(nx.numeric_assortativity_coefficient(G, "value"))


@pytest.mark.parametrize("scale", [1e-200, 1e200])
@pytest.mark.parametrize("graph_type", [nx.Graph, nx.DiGraph, nx.MultiDiGraph])
def test_weight_scale_invariance(graph_type, scale):
    G = graph_type()
    G.add_weighted_edges_from([(0, 1, 1), (1, 2, 2), (2, 0, 4), (0, 2, 3), (2, 3, 8)])
    expected = nx.degree_assortativity_coefficient(G, weight="weight")
    for _, _, data in G.edges(data=True):
        data["weight"] *= scale
    _assert_same(nx.degree_assortativity_coefficient(G, weight="weight"), expected)


def _exact_attribute_correlation(G, nodes=None):
    """Evaluate the original dense-matrix equation using exact Fractions."""
    selected = set(G) if nodes is None else set(nodes)
    pairs = []
    categories = {}
    for u, v in G.edges():
        x = G.nodes[u].get("category")
        y = G.nodes[v].get("category")
        if u in selected:
            pairs.append((x, y))
        if not G.is_directed() and u != v and v in selected:
            pairs.append((y, x))
    if not pairs:
        return float("nan")
    for pair in pairs:
        for value in pair:
            if value not in categories:
                categories[value] = len(categories)
    k = len(categories)
    M = [[Fraction(0) for _ in range(k)] for _ in range(k)]
    for x, y in pairs:
        M[categories[x]][categories[y]] += Fraction(1, len(pairs))
    trace = sum(M[i][i] for i in range(k))
    square_sum = sum(M[i][j] * M[j][l] for i in range(k) for j in range(k) for l in range(k))
    if square_sum == 1:
        return float("nan")
    return float((trace - square_sum) / (1 - square_sum))


@pytest.mark.parametrize("graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph])
@pytest.mark.parametrize("seed", range(8))
def test_categorical_against_exact_matrix_equation(graph_type, seed):
    rng = random.Random(seed)
    G = graph_type()
    G.add_nodes_from(range(9))
    for _ in range(23):
        G.add_edge(rng.randrange(8), rng.randrange(8))
    labels = ["a", "b", 5, (1, 2), None]
    for u in range(7):
        G.nodes[u]["category"] = rng.choice(labels)
    # Missing attributes, isolates, loops, parallel edges and selected sources
    # with unselected targets all occur in this family.
    for nodes in (None, [0, 2, 4, 6, 8], [1, 3], []):
        expected = _exact_attribute_correlation(G, nodes)
        _assert_same(nx.attribute_assortativity_coefficient(G, "category", nodes), expected)
        if nodes is not None:
            _assert_same(
                nx.attribute_assortativity_coefficient(G, "category", iter(nodes)), expected
            )


@pytest.mark.parametrize("shared_nan", [False, True])
def test_nonfinite_categories(shared_nan):
    G = nx.MultiDiGraph([(0, 1), (0, 1), (1, 2), (2, 0), (2, 2), (2, 3)])
    first = float("nan")
    second = first if shared_nan else float("nan")
    nx.set_node_attributes(
        G, {0: first, 1: second, 2: float("inf"), 3: float("-inf")}, "category"
    )
    _assert_same(
        nx.attribute_assortativity_coefficient(G, "category"),
        _exact_attribute_correlation(G),
    )


def test_categorical_undefined():
    for G in [nx.empty_graph(3), nx.path_graph(4)]:
        nx.set_node_attributes(G, "only", "category")
        assert math.isnan(nx.attribute_assortativity_coefficient(G, "category"))


def test_categories_use_dictionary_equality():
    class Category:
        def __init__(self, code):
            self.code = code

        def __hash__(self):
            return self.code

        def __eq__(self, other):
            if self is other:
                return True
            raise TypeError("Cross-category comparison is unsupported")

    G = nx.DiGraph([(0, 1), (1, 2), (2, 2), (2, 0)])
    nx.set_node_attributes(G, {u: Category(u) for u in G}, "category")
    _assert_same(
        nx.attribute_assortativity_coefficient(G, "category"),
        _exact_attribute_correlation(G),
    )
