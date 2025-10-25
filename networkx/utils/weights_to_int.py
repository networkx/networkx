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
    """
    Check if any of the edge weights may lead to floating-point rounding errors.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    weight : string
        Name of the edge attribute to scale. Default value: 'weight'.

    Returns
    -------
    bool
        True if integerization is needed, False otherwise.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edge("x", "y", capacity=0.1)
    >>> G.add_edge("y", "z", capacity=1.0)
    >>> G.add_edge("x", "z", capacity=2.5)
    >>> needs_integerization(G, weight="capacity")
    True

    >>> H = nx.DiGraph()
    >>> H.add_edge("a", "b", capacity=2)
    >>> H.add_edge("b", "c", capacity=3.0)
    >>> needs_integerization(H, weight="capacity")
    False
    """
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
    Choose a scale factor for converting edge weights to integers.

    Convert each edge weight w to Fraction(w).limit_denominator(max_denominator),
    then use scale_factor = LCM of denominators, capped by max_scale_factor.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    weight : string
        Name of the edge attribute to scale. Default value: 'weight'.

    max_denominator : integer
        Maximum denominator for rational approximations of edge weights. Default value: 10**12.

    max_scale_factor : integer
        Maximum allowed scale factor. Default value: 10**12.

    Returns
    -------
    scale_factor : integer
        Factor by which to multiply each edge weight before rounding to
        an integer.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edge("x", "y", capacity=0.25)
    >>> G.add_edge("y", "z", capacity=0.1)
    >>> G.add_edge("x", "z", capacity=0.5)
    >>> scale_factor = choose_scale_factor(G, weight="capacity")
    >>> scale_factor
    20
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

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    weight : string
        Name of the edge attribute to scale. Default value: 'weight'.

    scale_factor : integer
        Factor by which to multiply each edge weight before rounding to
        an integer. Default value: 1.

    default_value : integer, float, optional
        Value to use for edges that do not have the specified weight
        attribute before scaling. If not provided, edges without the
        specified weight attribute are left unchanged.

    Returns
    -------
    H : NetworkX graph
        A copy of G with edge weights scaled to integers.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edge("x", "y", capacity=0.5)
    >>> G.add_edge("y", "z", capacity=1.5)
    >>> G.add_edge("x", "z", capacity=2.5)
    >>> scaled_G = scale_edge_weight_to_ints(G, weight="capacity", scale_factor=2)
    >>> for u, v, c in scaled_G.edges(data="capacity"):
    ...     print(f"({u}, {v}): {c}")
    (x, y): 1
    (x, z): 5
    (y, z): 3
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
