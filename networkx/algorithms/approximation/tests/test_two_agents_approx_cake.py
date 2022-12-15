import unittest
from networkx.algorithms.approximation import divide_graphical_cake as dgc


class TestDivideGraphicalCake:
    def test_get_contiguous_oriented_labeling(self):
        g1 = dgc.graph_example1()
        g2 = dgc.graph_example2()
        g3 = dgc.graph_example3()
        assert dgc.get_contiguous_oriented_labeling(g1) == {(1, 2): 2, (1, 3): 1, (2, 3): 3, (2, 4): 4, (4, 6): 5,
                                                            (4, 5): 6, (5, 6): 7}, {1: [1, -2], 2: [2, 3, -4],
                                                                                    3: [-1, -3], 4: [4, -5, -6],
                                                                                    5: [6, -7], 6: [5, 7]}
        assert dgc.get_contiguous_oriented_labeling(g2) == {(1, 2): 5, (2, 3): 3, (2, 5): 4, (5, 4): 1, (4, 3): 2}, {
            1: [5], 2: [-5, 3, -4], 3: [-3, 2], 4: [-2, 1], 5: [4, -1]}
        assert dgc.get_contiguous_oriented_labeling(g3) == {(1, 2): 1, (2, 3): 2, (2, 5): 5, (4, 5): 4, (3, 4): 3,
                                                            (5, 6): 6}, {1: [-1], 2: [1, -2, -5], 3: [2, -3],
                                                                         4: [3, -4], 5: [4, 5, -6], 6: [6]}
