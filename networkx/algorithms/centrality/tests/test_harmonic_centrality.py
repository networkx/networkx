"""
Tests for degree centrality.
"""
from nose.tools import *
import networkx as nx
import harmonic

class TestClosenessCentrality:
    def setUp(self):
        self.P3 = nx.path_graph(3)
        self.P4 = nx.path_graph(4)
        self.K5 = nx.complete_graph(5)

        self.C4=nx.cycle_graph(4)
        self.C5=nx.cycle_graph(5)


        self.T=nx.balanced_tree(r=2, h=2)

        self.Gb = nx.DiGraph()
        self.Gb.add_edges_from([(0,1), (0,2), (0,4), (2,1),
                                (2,3), (4,3)])

        self.CD5=nx.DiGraph()



    def test_p3_harmonic(self):
        c=harmonic.harmonic_centrality(self.P3)
        d={0: 1.5,
           1: 2,
           2: 1.5}
        for n in sorted(self.P3):
            assert_almost_equal(c[n],d[n],places=3)

    def test_p4_harmonic(self):
        c=harmonic.harmonic_centrality(self.P4)
        d={0: 1.8333333,
           1: 2.5,
           2: 2.5,
           3: 1.8333333}
        for n in sorted(self.P4):
            assert_almost_equal(c[n],d[n],places=3)



    def clique_complete(self):
        HC=harmonic.harmonic_centrality(self.K5)
        d={0: 4,
           1: 4,
           2: 4,
           3: 4,
           4: 4}
        for n in sorted(self.P3):
            assert_almost_equal(HC[n],d[n],places=3)



    def cycle_C4(self):
        HC4=harmonic.harmonic_centrality(self.C4)
        d={0: 2.5,
           1: 2.5,
           2: 2.5,
           3: 2.5,}
        for n in sorted(self.C4):
            assert_almost_equal(HC4[n],d[n],places=3)

    def cycle_C5(self):
        HC5=harmonic.harmonic_centrality(self.C5)
        d={0: 3,
           1: 3,
           2: 3,
           3: 3,
           4: 3,
           5: 4}
        for n in sorted(self.P3):
            assert_almost_equal(HC5[n],d[n],places=3)

    def bal_tree(self):
        HC5=harmonic.harmonic_centrality(self.C4)
        d={0: 3,
           1: 3,
           2: 3,
           3: 3,
           4: 3}
        for n in sorted(self.P3):
            assert_almost_equal(HC5[n],d[n],places=3)



    def exampleGraph(self):
        mygraph=harmonic.harmonic_centrality(self.Gb)
        d={0: 0,
           1: 2,
           2: 1,
           3: 2.5,
           4: 1}
        for n in sorted(self.Gb):
            assert_almost_equal(mygraph[n],d[n],places=3)


    def test_weighted_harmonic(self):
        XG=nx.DiGraph()
        XG.add_weighted_edges_from([('a','b',10), ('d','c',5), ('a','c',1),
                                    ('e','f',2), ('f','c',1), ('a','f',3),
                                    ])
        c=harmonic.harmonic_centrality(XG,distance='weight')
        sp=nx.all_pairs_dijkstra_path_length(XG.reverse() if XG.is_directed() else XG,weight='weight')
        d={'a': 0,
           'b': 0.1,
           'c': 2.533,
           'd': 0,
           'e': 0,
           'f': 0.83333}
        for n in sorted(XG):
            assert_almost_equal(c[n],d[n],places=3)





if __name__ == "__main__":
    a=TestClosenessCentrality()

    a.setUp()
    print "Testing p3"
    a.test_p3_harmonic()
    print "Testing p4"
    a.test_p4_harmonic()
    print "test K5"
    a.clique_complete()
    print "test cycle c4"
    a.cycle_C4()
    print "test cycle c5"
    a.cycle_C5()
    print "test weighted harmonic"
    a.test_weighted_harmonic()
    print "test a nice example"
    a.exampleGraph()
