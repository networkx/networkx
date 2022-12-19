import proportional_cake_allocation as pca
import PiecewiseConstantValuation as pc


class TestAlloc:
    g1 = pca.graph_example1()
    g2 = pca.graph_example2()
    g3 = pca.graph_example3()
    g4, g5 = pca.allocation_graph1()
    g6, g7 = pca.allocation_graph2()
    g8, g9 = pca.allocation_graph3()
    assert pca.get_proportional_allocation(
        [pc.PiecewiseConstantValuation([10, 20]), pc.PiecewiseConstantValuation([10]),
         pc.PiecewiseConstantValuation([5, 10, 15]),
         pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([10]), pc.PiecewiseConstantValuation([10]),
         pc.PiecewiseConstantValuation([5, 10])],
        [pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]),
         pc.PiecewiseConstantValuation([4, 6, 8]), pc.PiecewiseConstantValuation([5]),
         pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5])], g1) == g4, g5
    assert pca.get_proportional_allocation(
        [pc.PiecewiseConstantValuation([1, 2, 3]), pc.PiecewiseConstantValuation([10]),
         pc.PiecewiseConstantValuation([2, 4, 6]), pc.PiecewiseConstantValuation([5, 10]),
         pc.PiecewiseConstantValuation([1])]
        ,
        [pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2, 4]),
         pc.PiecewiseConstantValuation([2, 4]), pc.PiecewiseConstantValuation([6])], g2) == g6, g7
    assert pca.get_proportional_allocation(
        [pc.PiecewiseConstantValuation([5, 10, 15]), pc.PiecewiseConstantValuation([2]),
         pc.PiecewiseConstantValuation([1, 2, 3]), pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([3]),
         pc.PiecewiseConstantValuation([20])],
        [pc.PiecewiseConstantValuation([5, 10]), pc.PiecewiseConstantValuation([1]),
         pc.PiecewiseConstantValuation([2, 4]),
         pc.PiecewiseConstantValuation([5]), pc.PiecewiseConstantValuation([2]),
         pc.PiecewiseConstantValuation([5, 10])], g3) == g8, g9
