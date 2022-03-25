"""Unit tests for the :mod:`networkx.algorithms.polynomials` module."""

import networkx as nx
import pytest

sympy = pytest.importorskip("sympy")


def test_tutte_polynomial_K1():
    """Check the Tutte polynomial for `K_1`."""
    g = nx.complete_graph(1)
    assert nx.tutte_polynomial(g) == 1


def test_tutte_polynomial_K4():
    """Check the Tutte polynomial for `K_4`."""
    g = nx.complete_graph(4)
    t = "x**3 + 3*x**2 + 4*x*y + 2*x + y**3 + 3*y**2 + 2*y"
    assert str(nx.tutte_polynomial(g)) == t


def test_tutte_polynomial_C5():
    """Check the Tutte polynomial for `C_5`."""
    g = nx.cycle_graph(5)
    t = "x**4 + x**3 + x**2 + x + y"
    assert str(nx.tutte_polynomial(g)) == t


def test_tutte_polynomial_diamond():
    """Check the Tutte polynomial for the diamond graph."""
    g = nx.diamond_graph()
    t = "x**3 + 2*x**2 + 2*x*y + x + y**2 + y"
    assert str(nx.tutte_polynomial(g)) == t


def test_tutte_polynomial_disjoint_K1():
    """Tutte polynomial factors into the Tutte polynomials of its components.
    Verify this property with the disjoint union of two copies of `K_1`.
    """
    g = nx.complete_graph(1)
    t_g = nx.tutte_polynomial(g)
    h = nx.disjoint_union(g, g)
    t_h = nx.tutte_polynomial(h)
    assert sympy.simplify(t_g * t_g).equals(t_h)


def test_tutte_polynomial_disjoint_K4():
    """Tutte polynomial factors into the Tutte polynomials of its components.
    Verify this property with the disjoint union of two copies of `K_4`.
    """
    g = nx.complete_graph(4)
    t_g = nx.tutte_polynomial(g)
    h = nx.disjoint_union(g, g)
    t_h = nx.tutte_polynomial(h)
    assert sympy.simplify(t_g * t_g).equals(t_h)


def test_tutte_polynomial_disjoint_C5():
    """Tutte polynomial factors into the Tutte polynomials of its components.
    Verify this property with the disjoint union of two copies of `C_5`.
    """
    g = nx.cycle_graph(5)
    t_g = nx.tutte_polynomial(g)
    h = nx.disjoint_union(g, g)
    t_h = nx.tutte_polynomial(h)
    assert sympy.simplify(t_g * t_g).equals(t_h)


def test_tutte_polynomial_disjoint_diamond():
    """Tutte polynomial factors into the Tutte polynomials of its components.
    Verify this property with the disjoint union of two diamond graphs.
    """
    g = nx.diamond_graph()
    t_g = nx.tutte_polynomial(g)
    h = nx.disjoint_union(g, g)
    t_h = nx.tutte_polynomial(h)
    assert sympy.simplify(t_g * t_g).equals(t_h)
