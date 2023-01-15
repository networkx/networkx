# import unittest
# from networkx.algorithms.approximation import contiguous_oriented_labeling as dgc
# from networkx.classes.reportviews import InEdgeView
#
#
# class TestContiguousLabeling:
#     def test_get_contiguous_oriented_labeling(self):
#         g1 = dgc.graph_example1()
#         g2 = dgc.graph_example2()
#         g3 = dgc.graph_example3()
#         print(dgc.get_contiguous_oriented_labeling(g1))
#         # assert dgc.get_contiguous_oriented_labeling(g1) == ([(1, 3), (3, 2), (1, 2), (2, 4), (4, 6), (6, 5), (5, 4)], InEdgeView([(1, 2), (3, 2), (2, 4), (5, 4), (1, 3), (4, 6), (6, 5)]))
#         # assert dgc.get_contiguous_oriented_labeling(g2) == ([(1, 2), (2, 5), (5, 4), (4, 3), (2, 3)], InEdgeView([(1, 2), (2, 3), (4, 3), (2, 5), (5, 4)]))
#         # assert dgc.get_contiguous_oriented_labeling(g3) == ([(1, 2), (2, 5), (2, 3), (3, 4), (4, 5), (5, 6)], InEdgeView([(1, 2), (2, 3), (3, 4), (4, 5), (2, 5), (5, 6)]))
