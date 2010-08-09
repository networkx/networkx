from nose.tools import *
import networkx as nx


class TestAtlas(object):
    def setUp(self):
        self.GAG=nx.graph_atlas_g()

    def test_sizes(self):
        G=self.GAG[0]
        assert_equal(G.number_of_nodes(),0)
        assert_equal(G.number_of_edges(),0)

        G=self.GAG[7]
        assert_equal(G.number_of_nodes(),3)
        assert_equal(G.number_of_edges(),3)

    def test_names(self):
        i=0
        for g in self.GAG:
            name=g.name
            assert_equal(int(name[1:]),i)
            i+=1

    def test_monotone_nodes(self):
        # check for monotone increasing number of nodes
        previous=self.GAG[0]
        for g in self.GAG:
            assert_false(len(g)-len(previous) > 1)
            previous=g.copy()

    def test_monotone_nodes(self):
        # check for monotone increasing number of edges
        # (for fixed number of nodes)
        previous=self.GAG[0]
        for g in self.GAG:
            if len(g)==len(previous):             
                assert_false(g.size()-previous.size() > 1)
            previous=g.copy()

    def test_monotone_degree_sequence(self):
        # check for monotone increasing degree sequence
        # (for fixed number f nodes and edges)
        # note that 111223 < 112222
        previous=self.GAG[0]
        for g in self.GAG:
            if len(g)==0: 
                continue
            if len(g)==len(previous) & g.size()==previous.size():
                deg_seq=sorted(g.degree().values())
                previous_deg_seq=sorted(previous.degree().values())
                assert_true(previous_deg_seq < deg_seq)
                previous=g.copy()


