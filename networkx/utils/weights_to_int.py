"""
Utility functions for converting edge weights to integers.
"""

import math
import numbers
from fractions import Fraction

import networkx as nx

__all__ = [
    "needs_integerization",
    "choose_scale_factor",
    "scale_edge_attribute_to_ints",
]


@nx._dispatchable(graphs="G")
def needs_integerization(G, weight="weight"):
    """Check if any of the edge weights may lead to floating-point rounding errors."""
    for _, _, w in G.edges(data=weight):
        if isinstance(w, (numbers.Real)) and not isinstance(w, (numbers.Rational)):
            if math.isfinite(w) and not float(w).is_integer():
                return True
    return False


@nx._dispatchable(graphs="G")
def choose_scale_factor(
    G, weight="weight", max_denominator=10**12, max_scale_factor=10**12
):
    """
    Convert each edge weight w to Fraction(w).limit_denominator(max_denominator),
    then use scale_factor = LCM of denominators, capped by max_scale_factor.
    """
    scale_factor = 1
    for _, _, w in G.edges(data=weight):
        if isinstance(w, (numbers.Real)):
            if math.isfinite(w) and not float(w).is_integer():
                # make a rational approximation with bounded denominator
                frac = Fraction(w).limit_denominator(max_denominator)
                scale_factor = math.lcm(scale_factor, frac.denominator)
                if scale_factor > max_scale_factor:
                    scale_factor = max_scale_factor
                    break
    return scale_factor


@nx._dispatchable(graphs="G")
def scale_edge_weight_to_ints(G, weight="weight", scale_factor=1, default_value=None):
    """
    Return a copy of G with edge weight `weight` multiplied by
    `scale_factor` and rounded to integers.

    Missing weights are set to `default_value` before scaling if provided.
    """

    def _scale_to_int(data):
        if weight not in data:
            w = default_value
        else:
            w = data[weight]
        if isinstance(w, numbers.Real):
            w *= scale_factor
            if math.isfinite(w):
                data[weight] = int(round(w))
            else:
                data[weight] = w

    H = G.copy()
    if H.is_multigraph():
        for _, _, _, data in H.edges(keys=True, data=True):
            _scale_to_int(data)
    else:
        for _, _, data in H.edges(data=True):
            _scale_to_int(data)
    return H
