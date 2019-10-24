import unittest

import networkx as nx
from networkx.algorithms.community import lukes_partitioning

EWL = 'e_weight'
NWL = 'n_weight'


class ErrorTestCase(unittest.TestCase):
    def test_tree(self):
        not_a_tree = nx.complete_graph(4)
        self.assertRaises(nx.NotATree, lukes_partitioning, not_a_tree, 5)

    def test_int(self):

        byte_block_size = 32

        ex_1_broken = nx.DiGraph()

        ex_1_broken.add_edge(1, 2, **{EWL: 3.2})
        ex_1_broken.add_edge(1, 4, **{EWL: 2.4})
        ex_1_broken.add_edge(2, 3, **{EWL: 4.0})
        ex_1_broken.add_edge(2, 5, **{EWL: 6.3})

        ex_1_broken.nodes[1][NWL] = 1.2  # !
        ex_1_broken.nodes[2][NWL] = 1
        ex_1_broken.nodes[3][NWL] = 1
        ex_1_broken.nodes[4][NWL] = 1
        ex_1_broken.nodes[5][NWL] = 2

        self.assertRaises(TypeError, lukes_partitioning, ex_1_broken,
                          byte_block_size, node_weight=NWL, edge_weight=EWL)

    # first test from the Lukes original paper
    def test_paper_1(self, float_ew=False, explicit_node_wt=True):

        limit = 3

        if float_ew:
            shift = 0.001
        else:
            shift = 0

        ground_truth = {frozenset([1, 4]),
                        frozenset([2, 3, 5])}

        example_1 = nx.DiGraph()

        example_1.add_edge(1, 2, **{EWL: 3 + shift})
        example_1.add_edge(1, 4, **{EWL: 2 + shift})
        example_1.add_edge(2, 3, **{EWL: 4 + shift})
        example_1.add_edge(2, 5, **{EWL: 6 + shift})

        if explicit_node_wt:
            nx.set_node_attributes(example_1, 1, NWL)
            wtu = NWL
        else:
            wtu = None

        clusters_1 = {frozenset(x) for x in
                      lukes_partitioning(example_1, limit,
                                         node_weight=wtu, edge_weight=EWL)}

        self.assertEqual(clusters_1, ground_truth)

        example_1_undirected = nx.Graph(example_1)
        clusters_1_undirected = \
            {frozenset(x) for x in
             lukes_partitioning(example_1_undirected, limit,
                                node_weight=wtu, edge_weight=EWL)}

        self.assertEqual(clusters_1_undirected, ground_truth)

    # second test from the Lukes original paper
    def test_paper_2(self, explicit_edge_wt=True):

        byte_block_size = 32
        ground_truth = {frozenset(['education', 'bs', 'ms', 'phd']),
                        frozenset(['name', 'home_address']),
                        frozenset(['telephone', 'home', 'office', 'no1', 'no2']),
                        }

        example_2 = nx.DiGraph()

        if explicit_edge_wt:
            edic = {EWL: 1}
            wtu = EWL
        else:
            edic = {}
            wtu = None

        example_2.add_edge('name', 'home_address', **edic)
        example_2.add_edge('name', 'education', **edic)
        example_2.add_edge('education', 'bs', **edic)
        example_2.add_edge('education', 'ms', **edic)
        example_2.add_edge('education', 'phd', **edic)
        example_2.add_edge('name', 'telephone', **edic)
        example_2.add_edge('telephone', 'home', **edic)
        example_2.add_edge('telephone', 'office', **edic)
        example_2.add_edge('office', 'no1', **edic)
        example_2.add_edge('office', 'no2', **edic)

        example_2.nodes['name'][NWL] = 20
        example_2.nodes['education'][NWL] = 10
        example_2.nodes['bs'][NWL] = 1
        example_2.nodes['ms'][NWL] = 1
        example_2.nodes['phd'][NWL] = 1
        example_2.nodes['home_address'][NWL] = 8
        example_2.nodes['telephone'][NWL] = 8
        example_2.nodes['home'][NWL] = 8
        example_2.nodes['office'][NWL] = 4
        example_2.nodes['no1'][NWL] = 1
        example_2.nodes['no2'][NWL] = 1

        clusters_2 = {frozenset(x) for x in
                      lukes_partitioning(example_2, byte_block_size,
                                         node_weight=NWL, edge_weight=wtu)}

        self.assertEqual(clusters_2, ground_truth)

        example_2_undirected = nx.Graph(example_2)
        clusters_2_undirected = \
            {frozenset(x) for x in
             lukes_partitioning(example_2_undirected, byte_block_size,
                                node_weight=NWL, edge_weight=wtu)}

        self.assertEqual(clusters_2_undirected, ground_truth)


if __name__ == '__main__':

    etc = ErrorTestCase()
    etc.test_tree()
    etc.test_int()
    etc.test_paper_1(False, True)
    etc.test_paper_1(True, False)
    etc.test_paper_1(True, True)
    etc.test_paper_1(False, False)
    etc.test_paper_2(False)
    etc.test_paper_2(True)
