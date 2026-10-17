"""Internal graph preparation shared by local structural coefficients."""

import math
from fractions import Fraction
from itertools import chain
from numbers import Real


def _selected_nodes(G, nodes):
    """Use NetworkX's scalar/nbunch convention without changing the graph."""
    if nodes in G:
        return [nodes], True
    return list(dict.fromkeys(G.nbunch_iter(nodes))), False


def _normalized_adjacency(G, weight):
    """Return loop-free adjacency; optionally normalize nonnegative weights.

    Missing attributes have weight one. Normalization uses all non-loop edges,
    including edges outside a requested node subset. Input data is never edited.
    """
    adjacency = {v: {} for v in G}
    edges = []
    scale = 1.0 if weight is None else 0.0
    for u, v, data in G.edges(data=True):
        if u == v:
            continue
        value = 1 if weight is None else data.get(weight, 1)
        if weight is not None:
            if not isinstance(value, Real):
                raise ValueError(
                    "Edge weights must be finite nonnegative real numbers."
                )
            try:
                value = float(value)
            except (OverflowError, ValueError) as err:
                raise ValueError(
                    "Edge weights must be finite nonnegative real numbers."
                ) from err
            if not math.isfinite(value) or value < 0:
                raise ValueError(
                    "Edge weights must be finite nonnegative real numbers."
                )
            scale = max(scale, value)
        edges.append((u, v, value))
    # All-zero weighted graphs represent zero opportunities.
    scale = scale or 1.0
    # Three normalized weights are multiplied in triangle counts. For extreme
    # dynamic ranges, float products (or normalization itself) can underflow
    # even when the final ratio is near one. Preserve exact binary-float ratios
    # in that uncommon case; normal inputs retain the fast float path.
    exact = weight is not None and any(
        value > 0 and value / scale < 1e-75 for _, _, value in edges
    )
    for u, v, value in edges:
        if weight is not None:
            value = Fraction(value) / Fraction(scale) if exact else value / scale
        adjacency[u][v] = value
        if not G.is_directed():
            adjacency[v][u] = value
    return adjacency


def _sum(values):
    """Sum a numeric domain without zero terms coercing exact fractions.

    Zero-opportunity terms are omitted and empty sums return integer zero, so
    subsequent fractional counts retain their domain. All nonzero terms from
    one prepared graph share a type.
    """
    values = (value for value in values if value != 0)
    first = next(values, None)
    if first is None:
        return 0
    values = chain((first,), values)
    return sum(values) if isinstance(first, Fraction) else math.fsum(values)


def _result(values, selected, single):
    return values[selected[0]] if single else values


def _mean(values, count_zeros):
    values = list(values.values()) if isinstance(values, dict) else [values]
    if not count_zeros:
        values = [value for value in values if value != 0]
    return math.fsum(values) / len(values) if values else 0.0
