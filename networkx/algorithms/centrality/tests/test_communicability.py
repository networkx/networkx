from collections import defaultdict
from nose.tools import *
from nose import SkipTest
import networkx as nx
from networkx.algorithms.centrality.communicability_alg import *

class TestCommunicability:
    @classmethod
    def setupClass(cls):
        global numpy
        global scipy
        try:
            import numpy
        except ImportError:
             raise SkipTest('NumPy not available.')
        try:
            import scipy
        except ImportError:
             raise SkipTest('SciPy not available.')


    def test_communicability_centrality(self):
        answer={0: 1.5430806348152433, 1: 1.5430806348152433}
        result=communicability_centrality(nx.path_graph(2))
        for k,v in result.items():
            assert_almost_equal(answer[k],result[k],places=7)

        answer1={'1': 1.6445956054135658,
                 'Albert': 2.4368257358712189,
                 'Aric': 2.4368257358712193,
                 'Dan':3.1306328496328168,
                 'Franck': 2.3876142275231915}
        G1=nx.Graph([('Franck','Aric'),('Aric','Dan'),('Dan','Albert'),
                     ('Albert','Franck'),('Dan','1'),('Franck','Albert')])
        result1=communicability_centrality(G1)
        for k,v in result1.items():
            assert_almost_equal(answer1[k],result1[k],places=7)
        result1=communicability_centrality_exp(G1)
        for k,v in result1.items():
            assert_almost_equal(answer1[k],result1[k],places=7)

    def test_communicability_betweenness_centrality(self):
        answer={0: 0.07017447951484615, 1: 0.71565598701107991,
                2: 0.71565598701107991, 3: 0.07017447951484615}
        result=communicability_betweenness_centrality(nx.path_graph(4))
        for k,v in result.items():
            assert_almost_equal(answer[k],result[k],places=7)

        answer1={'1': 0.060039074193949521,
                 'Albert': 0.315470761661372,
                 'Aric': 0.31547076166137211,
                 'Dan': 0.68297778678316201,
                 'Franck': 0.21977926617449497}
        G1=nx.Graph([('Franck','Aric'),
                     ('Aric','Dan'),('Dan','Albert'),('Albert','Franck'),
                     ('Dan','1'),('Franck','Albert')])
        result1=communicability_betweenness_centrality(G1)
        for k,v in result1.items():
            assert_almost_equal(answer1[k],result1[k],places=7)

    def test_communicability(self):
        answer={0 :{0: 1.5430806348152435,
                    1: 1.1752011936438012
                    },
                1 :{0: 1.1752011936438012,
                    1: 1.5430806348152435
                    }
                }
#        answer={(0, 0): 1.5430806348152435,
#                (0, 1): 1.1752011936438012,
#                (1, 0): 1.1752011936438012,
#                (1, 1): 1.5430806348152435}

        result=communicability(nx.path_graph(2))
        for k1,val in result.items():
            for k2 in val:
                assert_almost_equal(answer[k1][k2],result[k1][k2],places=7)

    def test_communicability2(self):

        answer_orig ={('1', '1'): 1.6445956054135658,
                 ('1', 'Albert'): 0.7430186221096251,
                 ('1', 'Aric'): 0.7430186221096251,
                 ('1', 'Dan'): 1.6208126320442937,
                 ('1', 'Franck'): 0.42639707170035257,
                 ('Albert', '1'): 0.7430186221096251,
                 ('Albert', 'Albert'): 2.4368257358712189,
                 ('Albert', 'Aric'): 1.4368257358712191,
                 ('Albert', 'Dan'): 2.0472097037446453,
                 ('Albert', 'Franck'): 1.8340111678944691,
                 ('Aric', '1'): 0.7430186221096251,
                 ('Aric', 'Albert'): 1.4368257358712191,
                 ('Aric', 'Aric'): 2.4368257358712193,
                 ('Aric', 'Dan'): 2.0472097037446457,
                 ('Aric', 'Franck'): 1.8340111678944691,
                 ('Dan', '1'): 1.6208126320442937,
                 ('Dan', 'Albert'): 2.0472097037446453,
                 ('Dan', 'Aric'): 2.0472097037446457,
                 ('Dan', 'Dan'): 3.1306328496328168,
                 ('Dan', 'Franck'): 1.4860372442192515,
                 ('Franck', '1'): 0.42639707170035257,
                 ('Franck', 'Albert'): 1.8340111678944691,
                 ('Franck', 'Aric'): 1.8340111678944691,
                 ('Franck', 'Dan'): 1.4860372442192515,
                 ('Franck', 'Franck'): 2.3876142275231915}

        answer=defaultdict(dict)
        for (k1,k2),v in answer_orig.items():
            answer[k1][k2]=v

        G1=nx.Graph([('Franck','Aric'),('Aric','Dan'),('Dan','Albert'),
                     ('Albert','Franck'),('Dan','1'),('Franck','Albert')])

        result=communicability(G1)
        for k1,val in result.items():
            for k2 in val:
                assert_almost_equal(answer[k1][k2],result[k1][k2],places=7)

        result=communicability_exp(G1)
        for k1,val in result.items():
            for k2 in val:
                assert_almost_equal(answer[k1][k2],result[k1][k2],places=7)


    def test_estrada_index(self):
        answer=1041.2470334195475
        result=estrada_index(nx.karate_club_graph())
        assert_almost_equal(answer,result,places=7)
