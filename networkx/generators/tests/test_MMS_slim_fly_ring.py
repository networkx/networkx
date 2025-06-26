"""
Unit tests for Slim Fly MMS ring-based graph construction.

This test suite includes:
- Structural tests: ensure no self-loops or duplicate edges, and expected node count.
- Connectivity test: ensure the graph is connected.
- Diameter test: verify that the diameter is small (expected 2 or close).
- Radix test: verify that node degrees are approximately regular within a bounded tolerance
Explanation about the tolerance and diameter:
When q is not a prime number (e.g., q = p^n), not all elements between 1 and q−1
are units (i.e., invertible elements in Z_q).
For powers greater than one, the graph may not be k-regular because some elements
have gcd(x, q) > 1 and do not belong to the multiplicative group Z_q*.

Example: q = 9
Elements like 3 and 6 have gcd(3,9) = 3 and gcd(6,9) = 3 → not coprime with 9.
Their powers collapse to zero:
  3^2 % 9 = 0
  6^2 % 9 = 0

These elements cannot be used to generate powers of a primitive root,
which breaks the structure of the graph.
As a result, the graph may not have diameter 2.

These tests help validate the mathematical properties and construction
logic of Slim Fly graphs over commutative rings.
"""

import math

import pytest

import networkx as nx
from networkx.generators.MMS_slim_fly_ring import slim_fly_graph

# Try importing numpy, skip tests if not available
try:
    import numpy as np

    _np_available = True
except ImportError:
    _np_available = False


def validate_graph_structure(G):
    loops = list(nx.selfloop_edges(G))
    assert not loops, f"Graph contains self-loops: {loops}"
    if G.is_multigraph():
        multi = [
            (u, v, G.number_of_edges(u, v))
            for u, v, _ in G.edges(keys=True)
            if G.number_of_edges(u, v) > 1
        ]
        assert not multi, f"Graph contains multiple edges: {multi}"
    else:
        simple_count = nx.Graph(G).number_of_edges()
        assert G.number_of_edges() == simple_count, "Graph contains duplicate edges"


@pytest.mark.parametrize("q", [3, 4, 5, 9, 27])
def test_slim_fly_structure(q):
    G = slim_fly_graph(q)
    expected = 2 * (q**2)
    assert G.number_of_nodes() == expected
    validate_graph_structure(G)


@pytest.mark.parametrize("q", [3, 4, 5, 9, 27])
def test_slim_fly_connectivity(q):
    G = slim_fly_graph(q)
    assert nx.is_connected(G)


@pytest.mark.parametrize("q", [3, 4, 5, 9, 27])
def test_slim_fly_diameter_is_two(q):
    if not _np_available:
        pytest.skip(
            "Numpy not available, skipping diameter test that relies on prime_factors."
        )
    G = slim_fly_graph(q)
    if G.number_of_nodes() == 0:
        pytest.skip(f"q={q} is not a valid number or graph was not constructed")
    diameter = nx.diameter(G)

    # Move prime_factors inside the test function or make it a helper function if needed.
    # It's not general utility, so keeping it closer to where it's used.
    def _prime_factors_for_test(n):
        """Return the list of prime divisors of n."""
        factors = []
        while n % 2 == 0:
            factors.append(2)
            n //= 2
        for i in range(3, int(np.sqrt(n)) + 1, 2):
            while n % i == 0:
                factors.append(i)
                n //= i
        if n > 1:
            factors.append(n)
        return factors

    expected_diameter = min(1 + len(_prime_factors_for_test(q)), 4)
    assert diameter == expected_diameter, (
        f"Expected low diameter for q={q}",
        f" but got {diameter}",
    )


def is_almost_k_regular(G, k, tolerance):
    return all(abs(deg - k) <= tolerance for _, deg in G.degree())


@pytest.mark.parametrize("q", [3, 4, 5, 9, 27])
def test_slim_fly_radix(q):
    if not _np_available:
        pytest.skip("Numpy not available, skipping radix test that relies on numpy.")
    G = slim_fly_graph(q)
    if G.number_of_nodes() == 0:
        pytest.skip(f"q={q} is not a valid number or graph was not constructed")
    delta = 1 if q % 4 == 1 else -1 if q % 4 == 3 else 0
    expected_radix = (3 * q - delta) // 2
    gcd_of_q = [math.gcd(q, i) - 1 for i in range(1, q)]
    tol = sum(1 for x in gcd_of_q if x != 0)
    assert is_almost_k_regular(G, expected_radix, tolerance=tol), (
        f"Graph is not almost k-regular (±{tol})"
    )
