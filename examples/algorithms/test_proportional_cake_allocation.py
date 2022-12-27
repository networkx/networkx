import proportional_cake_allocation as pca
import PiecewiseConstantValuation as pc
import networkx as nx
from networkx.algorithms.approximation import contiguous_oriented_labeling as col
import networkx.algorithms.isomorphism as iso


class TestAlloc:
    def test_prop_cake_allo(self):
        g1, g2 = pca.allocation_graph1()
        g3, g4 = pca.get_proportional_allocation(
            [pc.PiecewiseConstantValuation([10, 20]), pc.PiecewiseConstantValuation([10]),
             pc.PiecewiseConstantValuation([5]),
             pc.PiecewiseConstantValuation([10, 20]), pc.PiecewiseConstantValuation([10]),
             pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([5, 10])],
            [pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]),
             pc.PiecewiseConstantValuation([4, 6, 8, 10]), pc.PiecewiseConstantValuation([5]),
             pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([10])], pca.graph_example1())
        em = iso.numerical_edge_match('weight', 1)
        b = (iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em))
        assert b is True
        g1, g2 = pca.allocation_graph2()
        g3, g4 = pca.get_proportional_allocation(
            [pc.PiecewiseConstantValuation([1]), pc.PiecewiseConstantValuation([1, 2, 3, 4]),
             pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([2, 4]),
             pc.PiecewiseConstantValuation([5, 10])],
            [pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([5]),
             pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2, 4]),
             pc.PiecewiseConstantValuation([2, 4])], pca.graph_example2())
        em = iso.numerical_edge_match('weight', 1)
        b = iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em)
        assert b is True
        g1, g2 = pca.allocation_graph3()
        g3, g4 = pca.get_proportional_allocation(
            [pc.PiecewiseConstantValuation([5, 10, 15]), pc.PiecewiseConstantValuation([2]),
             pc.PiecewiseConstantValuation([2]), pc.PiecewiseConstantValuation([1, 2]),
             pc.PiecewiseConstantValuation([3]), pc.PiecewiseConstantValuation([20])],
            [pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([1]),
             pc.PiecewiseConstantValuation([2, 4]),
             pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2]),
             pc.PiecewiseConstantValuation([5, 10])], pca.graph_example3())
        em = iso.numerical_edge_match('weight', 1)
        b = iso.is_isomorphic(g1, g3, edge_match=em) and iso.is_isomorphic(g2, g4, edge_match=em)
        assert b is True
