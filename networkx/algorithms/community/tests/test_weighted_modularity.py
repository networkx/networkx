"""Tests for the weighted_modularity module"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import unittest


# Third party
import networkx as nx
import nose.tools as nt
import numpy as np
import numpy.testing as npt

# Our own

from networkx.algorithms.community import weighted_modularity as wm


def get_test_data():
    """ grabs local txt file with adj matrices
    Returns
    =======
    graph : networkx graph
    communities : list of sets
    """
    n = 40
    mat = np.ones((n,n))
    communities = []
    for i in xrange(0,n,10):
        mat[i:i+10, i:i+10] = i/5 + 1
        communities.append(set(range(i,i+10)))
    np.fill_diagonal(mat, np.array( 10*[0] + 90*[1]))
    graph = nx.from_numpy_matrix(mat)
    return graph, communities

class TestWeightedPartition(unittest.TestCase):

    def setUp(self):
        ## generate a default graph and communities
        graph, communities = get_test_data()
        self.graph = graph
        self.communities = communities

    def test_init(self):
        part = wm.WeightedPartition(self.graph)
        self.assertEqual(type(part.degrees), type({}))
        npt.assert_array_almost_equal(part.total_edge_weight, 1350.0)
        # generated communities
        comm = [set([node]) for node in self.graph.nodes()]
        self.assertEqual(part.communities, comm)
        # test communities cannot be replaced by garbage
        with self.assertRaises(TypeError):
            part.communities = 11
        # doesnt work if nodes are missing from partition
        with self.assertRaises(ValueError):
            part.communities = [set([1,2,3])]
        # but we can pass a valid community partition
        part.communities = comm
        self.assertEqual(part.communities, comm)

    def test_communities_degree(self):
        ## if no community, method will raise error
        part = wm.WeightedPartition(self.graph)
        part = wm.WeightedPartition(self.graph, self.communities)
        cdegree = part.communities_degree()
        self.assertEqual(round(cdegree[0]), 390.0)


    def test_set_communities(self):
        part = wm.WeightedPartition(self.graph, self.communities)
        self.assertEqual(part.communities, self.communities)
        with self.assertRaises(TypeError):
            # raise error if not list of sets
            part.set_communities(part.communities[0])
        with self.assertRaises(TypeError):
            part.set_communities('a')
        with self.assertRaises(ValueError):
            ## missing nodes
            comm = self.graph.nodes()[:-3]
            part.set_communities([set(comm)])

    def test_allnodes_in_communities(self):
        """checks communities contain all nodes
        with no repetition"""
        part = wm.WeightedPartition(self.graph)
        self.assertTrue(part._allnodes_in_communities(self.communities))
        self.assertFalse(part._allnodes_in_communities([self.communities[0]]))


    def test_get_node_community(self):
        part = wm.WeightedPartition(self.graph, self.communities)
        self.assertEqual(part.get_node_community(0), 0)
        self.assertEqual(part.get_node_community(self.graph.nodes()[-1]),3)
        with self.assertRaises(ValueError):
            part.get_node_community(-1)
        part = wm.WeightedPartition(self.graph)
        self.assertEqual(part.get_node_community(0), 0)

    def test_node_degree(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        node = 0
        res = part.node_degree(node)
        npt.assert_almost_equal(res, 39)

    def test_modularity(self):
        part = wm.WeightedPartition(self.graph, self.communities)
        npt.assert_almost_equal(part.modularity(), 0.2818107)


    def test_degree_by_community(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        ## summ of all links in or out of communities
        ## since one per scommunity, just weighted degree of each node
        tot_per_comm = part.degree_by_community()
        degw = self.graph.degree(weight='weight').values()
        self.assertEqual(tot_per_comm, degw)
        ## This isnt true of we have communities with multiple nodes
        part_2comm = wm.WeightedPartition(self.graph, self.communities)
        self.assertEqual(part_2comm == degw, False)

    def test_degree_within_community(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        weights = part.degree_within_community()
        ## this inlcudes self links so
        self.assertEqual(weights[0], 0.0) #no self-edge
        self.assertEqual(weights[-1], 1.0) # self edge



    def test_node_degree_by_community(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        node = 0
        node2comm_weights = part.node_degree_by_community(node)
        # self loops not added to weight
        # so communities made only of node should be zero
        npt.assert_equal(node2comm_weights[0],0)
        # this should be equal to weight between two nodes
        neighbor = 1
        expected = self.graph[node][neighbor]['weight']
        npt.assert_equal(node2comm_weights[neighbor],expected)
        part = wm.WeightedPartition(self.graph, self.communities)
        node2comm_weights = part.node_degree_by_community(node)
        npt.assert_equal(len(node2comm_weights), len(part.communities))


class TestLouvainCommunityDetection(unittest.TestCase):

    def setUp(self):
        ## generate a default graph and communities
        graph, communities = get_test_data()
        self.graph = graph
        self.communities = communities
        self.louvain = wm.LouvainCommunityDetection(graph)
        self.louvain_comm = wm.LouvainCommunityDetection(graph, communities)

    def test_init(self):
        louvain = self.louvain
        self.assertEqual(louvain.graph, self.graph)
        self.assertEqual(louvain.initial_communities, None)
        self.assertEqual(louvain.minthr, 0.0000001)


    def test_communities_without_node(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        node = 0
        updated_comm = self.louvain._communities_without_node(part, node)
        self.assertEqual(updated_comm[0], set([]))
        part = wm.WeightedPartition(self.graph, self.communities)
        updated_comm = self.louvain_comm._communities_without_node(part, node)
        ## make sure we dont break communities from original partition
        self.assertEqual(part.communities, self.communities)
        self.assertEqual(0 not in updated_comm[0], True)

    def test_communities_nodes_alledgesw(self):
        part = wm.WeightedPartition(self.graph, self.communities)
        node = 0
        weights = self.louvain_comm._communities_nodes_alledgesw(part, node)
        npt.assert_almost_equal(weights[0], 351.0)
        ## test with possible empty node set
        part = wm.WeightedPartition(self.graph)
        weights = self.louvain._communities_nodes_alledgesw(part, node)
        self.assertEqual(weights[0], 0)
        # other communities are made up of just one node
        self.assertEqual(weights[1], self.graph.degree(weight='weight')[1])


    def test_calc_delta_modularity(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        node = 0
        change = self.louvain._calc_delta_modularity(node, part)
        self.assertEqual(len(change), len(part.communities))
        # change is an array
        self.assertEqual(change.shape[0], len(part.communities))
        self.assertEqual(change[0] < change[1], True)
        # this is one comm per node, so once removed from own
        # comm, this delta_weight will be zero
        self.assertEqual(change[node] , 0)

    def test_move_node(self):
        part = wm.WeightedPartition(self.graph) # one comm per node
        #move first node to second community
        node = 0
        comm = 1
        newpart = self.louvain._move_node(part, node, comm)
        self.assertEqual(set([0,1]) in newpart.communities, True)
        ## what happens if node or comm missing
        with self.assertRaises(ValueError):
            newpart = self.louvain._move_node(part, -1, comm)
        invalid_communities = len(part.communities) + 1
        with self.assertRaises(IndexError):
            newpart = self.louvain._move_node(part, node, invalid_communities)

    def test_gen_dendogram(self):
        graph = nx.Graph()
        nodeslist = [0,1,2,3,4]
        graph.add_nodes_from(nodeslist, weight=True)
        louvain = wm.LouvainCommunityDetection(graph)
        self.assertRaises(IOError, louvain._gen_dendogram)

    def test_run(self):
        karate = nx.karate_club_graph()
        louvain = wm.LouvainCommunityDetection(karate)
        final_partitions = louvain.run()
        self.assertEqual(final_partitions[-1].modularity() > .38,
                         True)
        self.assertEqual(len(final_partitions), 2)


    def test_combine(self):

        first = [set([0,1,2]), set([3,4,5]), set([6,7])]
        second = [set([0,2]), set([1])]
        npt.assert_raises(ValueError, self.louvain._combine, second, first)
        res = self.louvain._combine(first, second)
        npt.assert_equal(res, [set([0,1,2,6,7]), set([3,4,5])])

def test_meta_graph():
    graph, communities = get_test_data()
    part = wm.WeightedPartition(graph)
    metagraph,_ = wm.meta_graph(part)
    ## each node is a comm, so no change to metagraph
    npt.assert_equal(metagraph.nodes(), graph.nodes())
    ## two communitties
    part = wm.WeightedPartition(graph, communities)
    metagraph,mapping = wm.meta_graph(part)
    npt.assert_equal(metagraph.nodes(), [0,1,2,3])
    ## metagraph always has self edges
    npt.assert_equal(True , all([(x,x) in metagraph.edges() for x in range(4)]))
    # mapping should map new node 0 to communities[0]
    npt.assert_equal(mapping[0], communities[0])
    ## weight should not be lost between graphs
    npt.assert_almost_equal(metagraph.size(weight='weight'),
        graph.size(weight='weight'))
