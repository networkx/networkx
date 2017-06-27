from nose import SkipTest
from nose.tools import assert_true

import networkx as nx
from networkx.testing import assert_nodes_equal, assert_edges_equal

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
        mdf = pd.DataFrame([[4, 16, 'A', 'D']],
                            columns=['weight', 'cost', 0, 'b'])
        self.mdf = df.append(mdf)

    def assert_equal(self, G1, G2):
        assert_true( nx.is_isomorphic(G1, G2, edge_match=lambda x, y: x == y ))

    def test_from_dataframe_all_attr(self, ):
        Gtrue = nx.Graph([('E', 'C', {'cost': 9, 'weight': 10}),
                               ('B', 'A', {'cost': 1, 'weight': 7}),
                               ('A', 'D', {'cost': 7, 'weight': 4})])
        G=nx.from_pandas_dataframe(self.df, 0, 'b', True)
        self.assert_equal(G, Gtrue)
        # MultiGraph
        MGtrue = nx.MultiGraph(Gtrue)
        MGtrue.add_edge('A', 'D', cost=16, weight=4)
        MG=nx.from_pandas_dataframe(self.mdf, 0, 'b', True, nx.MultiGraph())
        self.assert_equal(MG, MGtrue)

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


    def test_from_datafram(self, ):
        # Pandas DataFrame
        g = nx.cycle_graph(10)
        G = nx.Graph()
        G.add_nodes_from(g)
        G.add_weighted_edges_from((u, v, u) for u,v in g.edges())
        edgelist = nx.to_edgelist(G)
        source = [s for s, t, d in edgelist]
        target = [t for s, t, d in edgelist]
        weight = [d['weight'] for s, t, d in edgelist]
        import pandas as pd
        edges = pd.DataFrame({'source': source,
                              'target': target,
                              'weight': weight})
        GG = nx.from_pandas_dataframe(edges, edge_attr='weight')
        assert_nodes_equal(sorted(G.nodes()), sorted(GG.nodes()))
        assert_edges_equal(sorted(G.edges()), sorted(GG.edges()))
        GW = nx.to_networkx_graph(edges, create_using=nx.Graph())
        assert_nodes_equal(sorted(G.nodes()), sorted(GW.nodes()))
        assert_edges_equal(sorted(G.edges()), sorted(GW.edges()))
