from nose import SkipTest
from nose.tools import assert_true

import networkx as nx

class TestConvertPandas(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        try:
            import pandas as pd
        except ImportError:
            raise SkipTest('Pandas not available.')

    def __init__(self, ):
        global pd
        import pandas as pd

        self.r = pd.np.random.RandomState(seed=5)
        ints = self.r.random_integers(1, 10, size=(3,2))
        a = ['A', 'B', 'C']
        b = ['D', 'A', 'E']
        df = pd.DataFrame(ints, columns=['weight', 'cost'])
        df[0] = a # Column label 0 (int)
        df['b'] = b # Column label 'b' (str)
        self.df = df

    def assert_equal(self, G1, G2):
        assert_true( nx.is_isomorphic(G1, G2, edge_match=lambda x, y: x == y ))

    def test_from_dataframe_all_attr(self, ):
        Gtrue = nx.Graph([('E', 'C', {'cost': 9, 'weight': 10}),
                               ('B', 'A', {'cost': 1, 'weight': 7}),
                               ('A', 'D', {'cost': 7, 'weight': 4})])
        G=nx.from_pandas_dataframe(self.df, 0, 'b', True)
        self.assert_equal(G, Gtrue)

    def test_from_dataframe_multi_attr(self, ):
        Gtrue = nx.Graph([('E', 'C', {'cost': 9, 'weight': 10}),
                               ('B', 'A', {'cost': 1, 'weight': 7}),
                               ('A', 'D', {'cost': 7, 'weight': 4})])
        G=nx.from_pandas_dataframe(self.df, 0, 'b', ['weight', 'cost'])
        self.assert_equal(G, Gtrue)

    def test_from_dataframe_one_attr(self, ):
        Gtrue = nx.Graph([('E', 'C', {'weight': 10}),
                               ('B', 'A', {'weight': 7}),
                               ('A', 'D', {'weight': 4})])
        G=nx.from_pandas_dataframe(self.df, 0, 'b', 'weight')
        self.assert_equal(G, Gtrue)

    def test_from_dataframe_no_attr(self, ):
        Gtrue = nx.Graph([('E', 'C', {}),
                               ('B', 'A', {}),
                               ('A', 'D', {})])
        G=nx.from_pandas_dataframe(self.df, 0, 'b',)
        self.assert_equal(G, Gtrue)
