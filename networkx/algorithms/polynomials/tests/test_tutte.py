import networkx as nx
import sympy


class TestTutte:
    def test_tutte_polynomial_K1(self):
        """Check the Tutte polynomial for $K_1$.
        """
        G = nx.complete_graph(1)
        assert nx.tutte_polynomial(G) == 1

    def test_tutte_polynomial_K4(self):
        """Check the Tutte polynomial for $K_4$.
        """
        G = nx.complete_graph(4)
        t = "x**3 + 3*x**2 + 4*x*y + 2*x + y**3 + 3*y**2 + 2*y"
        assert str(nx.tutte_polynomial(G)) == t

    def test_tutte_polynomial_C5(self):
        """Check the Tutte polynomial for $C_5$.
        """
        G = nx.cycle_graph(5)
        t = "x**4 + x**3 + x**2 + x + y"
        assert str(nx.tutte_polynomial(G)) == t

    def test_tutte_polynomial_diamond(self):
        """Check the Tutte polynomial for the diamond graph.
        """
        G = nx.diamond_graph()
        t = "x**3 + 2*x**2 + 2*x*y + x + y**2 + y"
        assert str(nx.tutte_polynomial(G)) == t

    def test_tutte_polynomial_disjoint_K1(self):
        """Tutte polynomial factors into the Tutte polynomials of its components.
        Verify this property with the disjoint union of two copies of $K_1$.
        """
        G = nx.complete_graph(1)
        t_G = nx.tutte_polynomial(G)
        H = nx.disjoint_union(G, G)
        t_H = nx.tutte_polynomial(H)
        assert sympy.simplify(t_G * t_G) == t_H

    def test_tutte_polynomial_disjoint_K4(self):
        """Tutte polynomial factors into the Tutte polynomials of its components.
        Verify this property with the disjoint union of two copies of $K_4$.
        """
        G = nx.complete_graph(4)
        t_G = nx.tutte_polynomial(G)
        H = nx.disjoint_union(G, G)
        t_H = nx.tutte_polynomial(H)
        assert sympy.simplify(t_G * t_G) == t_H

    def test_tutte_polynomial_disjoint_C5(self):
        """Tutte polynomial factors into the Tutte polynomials of its components.
        Verify this property with the disjoint union of two copies of $C_5$.
        """
        G = nx.cycle_graph(5)
        t_G = nx.tutte_polynomial(G)
        H = nx.disjoint_union(G, G)
        t_H = nx.tutte_polynomial(H)
        assert sympy.simplify(t_G * t_G) == t_H

    def test_tutte_polynomial_disjoint_diamond(self):
        """Tutte polynomial factors into the Tutte polynomials of its components.
        Verify this property with the disjoint union of two diamond graphs.
        """
        G = nx.diamond_graph()
        t_G = nx.tutte_polynomial(G)
        H = nx.disjoint_union(G, G)
        t_H = nx.tutte_polynomial(H)
        assert sympy.simplify(t_G * t_G) == t_H

    def test_get_cut_edges_barbell_3_3(self):
        G = nx.barbell_graph(3, 3)
        cut_edges = nx.algorithms.polynomials.tutte._get_cut_edges(G)
        assert len(cut_edges) == 4

    def test_get_cut_edges_barbell_3_10(self):
        G = nx.barbell_graph(3, 10)
        cut_edges = nx.algorithms.polynomials.tutte._get_cut_edges(G)
        assert len(cut_edges) == 11

    def test_get_cut_edges_barbell_K4(self):
        G = nx.complete_graph(4)
        cut_edges = nx.algorithms.polynomials.tutte._get_cut_edges(G)
        assert len(cut_edges) == 0
