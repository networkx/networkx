"""Unit tests for the :mod:`networkx.algorithms.polynomials` module."""

import networkx as nx
import pytest

sympy = pytest.importorskip("sympy")


# Mapping of input graphs to a string representation of their tutte polynomials
_test_graphs = {
    nx.complete_graph(1): "1",
    nx.complete_graph(4): "x**3 + 3*x**2 + 4*x*y + 2*x + y**3 + 3*y**2 + 2*y",
    nx.cycle_graph(5): "x**4 + x**3 + x**2 + x + y",
    nx.diamond_graph(): "x**3 + 2*x**2 + 2*x*y + x + y**2 + y",
}


@pytest.mark.parametrize(("G", "expected"), _test_graphs.items())
def test_tutte_polynomial(G, expected):
    assert str(nx.tutte_polynomial(G)) == expected


@pytest.mark.parametrize("G", _test_graphs.keys())
def test_tutte_polynomial_disjoint_K1(G):
    """Tutte polynomial factors into the Tutte polynomials of its components.
    Verify this property with the disjoint union of two copies of the input graph.
    """
    t_g = nx.tutte_polynomial(G)
    H = nx.disjoint_union(G, G)
    t_h = nx.tutte_polynomial(H)
    assert sympy.simplify(t_g * t_g).equals(t_h)
