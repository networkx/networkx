"""
Tests for degree centrality.
"""
from nose.tools import *
import networkx as nx

class TestClosenessCentrality:
    def setUp(self):

        self.K = nx.krackhardt_kite_graph()
        self.P3 = nx.path_graph(3)
        self.P4 = nx.path_graph(4)
        self.K5 = nx.complete_graph(5)

        self.C4=nx.cycle_graph(4)
        self.T=nx.balanced_tree(r=2, h=2)
        self.Gb = nx.Graph()
        self.Gb.add_edges_from([(0,1), (0,2), (1,3), (2,3), 
                                (2,4), (4,5), (3,5)])


        F = nx.Graph() # Florentine families
        F.add_edge('Acciaiuoli','Medici')
        F.add_edge('Castellani','Peruzzi')
        F.add_edge('Castellani','Strozzi')
        F.add_edge('Castellani','Barbadori')
        F.add_edge('Medici','Barbadori')
        F.add_edge('Medici','Ridolfi')
        F.add_edge('Medici','Tornabuoni')
        F.add_edge('Medici','Albizzi')
        F.add_edge('Medici','Salviati')
        F.add_edge('Salviati','Pazzi')
        F.add_edge('Peruzzi','Strozzi')
        F.add_edge('Peruzzi','Bischeri')
        F.add_edge('Strozzi','Ridolfi')
        F.add_edge('Strozzi','Bischeri')
        F.add_edge('Ridolfi','Tornabuoni')
        F.add_edge('Tornabuoni','Guadagni')
        F.add_edge('Albizzi','Ginori')
        F.add_edge('Albizzi','Guadagni')
        F.add_edge('Bischeri','Guadagni')
        F.add_edge('Guadagni','Lamberteschi')    
        self.F = F


    def test_k5_closeness(self):
        c=nx.closeness_centrality(self.K5)
        d={0: 1.000,
           1: 1.000,
           2: 1.000,
           3: 1.000,
           4: 1.000}
        for n in sorted(self.K5):
            assert_almost_equal(c[n],d[n],places=3)

    def test_p3_closeness(self):
        c=nx.closeness_centrality(self.P3)
        d={0: 0.667,
           1: 1.000,
           2: 0.667}
        for n in sorted(self.P3):
            assert_almost_equal(c[n],d[n],places=3)

    def test_krackhardt_closeness(self):
        c=nx.closeness_centrality(self.K)
        d={0: 0.529,
           1: 0.529,
           2: 0.500,
           3: 0.600,
           4: 0.500,
           5: 0.643,
           6: 0.643,
           7: 0.600,
           8: 0.429,
           9: 0.310}
        for n in sorted(self.K):
            assert_almost_equal(c[n],d[n],places=3)

    def test_florentine_families_closeness(self):
        c=nx.closeness_centrality(self.F)
        d={'Acciaiuoli':    0.368,
           'Albizzi':       0.483,
           'Barbadori':     0.4375,
           'Bischeri':      0.400,
           'Castellani':    0.389,
           'Ginori':        0.333,
           'Guadagni':      0.467,
           'Lamberteschi':  0.326,
           'Medici':        0.560,
           'Pazzi':         0.286,
           'Peruzzi':       0.368,
           'Ridolfi':       0.500,
           'Salviati':      0.389,
           'Strozzi':       0.4375,
           'Tornabuoni':    0.483}
        for n in sorted(self.F):
            assert_almost_equal(c[n],d[n],places=3)

    def test_weighted_closeness(self):
        XG=nx.Graph()
        XG.add_weighted_edges_from([('s','u',10), ('s','x',5), ('u','v',1),
                                    ('u','x',2), ('v','y',1), ('x','u',3),
                                    ('x','v',5), ('x','y',2), ('y','s',7),
                                    ('y','v',6)])
        c=nx.closeness_centrality(XG,weighted_edges=True)
        d={'y': 0.200,
           'x': 0.286,
           's': 0.138,
           'u': 0.235,
           'v': 0.200}
        for n in sorted(XG):
            assert_almost_equal(c[n],d[n],places=3)

