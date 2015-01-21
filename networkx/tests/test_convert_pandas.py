from nose import SkipTest
from nose.tools import assert_true

import networkx as nx

class TestConvertPandas(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global np
        global pd
        try:
            import numpy as np
            import pandas as pd
        except ImportError:
            raise SkipTest('Pandas not available.')

    def __init__(self, ):
        self.r = np.random.RandomState(seed=1)
        self.ints = self.r.random_integers(0, 10, size=(2,3))
        self.index = ['A', 'B']
        self.columns = ['A', 'E', 'F']

        self.G1 = nx.Graph([('A', 'A', {'weight': 5}),
                            ('A', 'F', {'weight': 9}),
                            ('A', 'E', {'weight': 8}),
                            ('A', 'B', {'weight': 5})])

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes())==sorted(G2.nodes()) )
        assert_true( sorted(G1.edges(data=True))==sorted(G2.edges(data=True)) )

    def test_from_dataframe_remove_zeros(self, ):
        df = pd.DataFrame(self.ints, columns=self.columns, index=self.index)
        G=nx.from_pandas_dataframe(df)
        self.assert_equal(G, self.G1)

