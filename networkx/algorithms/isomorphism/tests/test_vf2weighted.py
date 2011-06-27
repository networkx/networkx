"""
    Tests for VF2 isomorphism algorithm for weighted graphs.
"""

from nose.tools import assert_true, assert_false
import networkx as nx

def test_simple():
    # 16 simple tests
    w = 'weight'
    edges = [(0,0,1),(0,0,1.5),(0,1,2),(1,0,3)]
    for g1 in [nx.Graph(),
               nx.DiGraph(),
               nx.MultiGraph(),
               nx.MultiDiGraph(),
               ]:

        g1.add_weighted_edges_from(edges)
        g2 = g1.subgraph(g1.nodes())
        assert_true( nx.is_isomorphic(g1,g2,weight=w) )

        for mod1, mod2 in [(False, True), (True, False), (True, True)]:
            # mod1 tests a regular edge
            # mod2 tests a selfloop
            if g2.is_multigraph():
                if mod1:
                    data1 = {0:{'weight':10}}
                if mod2:
                    data2 = {0:{'weight':1},1:{'weight':2.5}}
            else:
                if mod1:
                    data1 = {'weight':10}
                if mod2:
                    data2 = {'weight':2.5}

            g2 = g1.subgraph(g1.nodes())
            if mod1:
                if not g1.is_directed():
                    g2.adj[1][0] = data1
                    g2.adj[0][1] = data1
                else:
                    g2.succ[1][0] = data1
                    g2.pred[0][1] = data1
            if mod2:
                if not g1.is_directed():
                    g2.adj[0][0] = data2
                else:
                    g2.succ[0][0] = data2
                    g2.pred[0][0] = data2

            assert_false(nx.is_isomorphic(g1,g2,weight=w))

def test_weightkey():
    g1 = nx.DiGraph()
    g2 = nx.DiGraph()

    g1.add_edge('A','B', weight=1)
    g2.add_edge('C','D', weight=0)

    assert_true(  nx.is_isomorphic(g1, g2) )
    assert_true(  nx.is_isomorphic(g1, g2, weight='nonexistent attribute') )
    assert_false( nx.is_isomorphic(g1, g2, weight='weight') )

    g2 = nx.DiGraph()
    g2.add_edge('C','D')
    assert_true( nx.is_isomorphic(g1, g2, weight='weight') )

class TestNodeMatch_Graph(object):
    def setUp(self):
        self.g1 = nx.Graph()
        self.g2 = nx.Graph()
        self.build()

    def build(self):
        def nm(n1_attrs, n2_attrs):
            return n1_attrs.get('color', '') == n2_attrs.get('color', '')
        self.nm = nm

        self.g1.add_node('A', color='red')
        self.g2.add_node('C', color='blue')

        self.g1.add_edge('A','B', weight=1)
        self.g2.add_edge('C','D', weight=1)

    def test_noweight_nocolor(self):
        assert_true(  nx.is_isomorphic(self.g1, self.g2) )

    def test_color1(self):
        assert_false(  nx.is_isomorphic(self.g1, self.g2, node_match=self.nm) )

    def test_color2(self):
        self.g1.node['A']['color'] = 'blue'
        assert_true(  nx.is_isomorphic(self.g1, self.g2, node_match=self.nm) )

    def test_weight1(self):
        assert_true(  nx.is_isomorphic(self.g1, self.g2, weight='weight') )

    def test_weight2(self):
        self.g1.add_edge('A', 'B', weight=2)
        assert_false(  nx.is_isomorphic(self.g1, self.g2, weight='weight') )

    def test_colorsandweights1(self):
        iso = nx.is_isomorphic(self.g1, self.g2,
                               node_match=self.nm, weight='weight')
        assert_false(iso)

    def test_colorsandweights2(self):
        self.g1.node['A']['color'] = 'blue'
        iso = nx.is_isomorphic(self.g1, self.g2,
                               node_match=self.nm, weight='weight')
        assert_true(iso)

    def test_colorsandweights3(self):
        # make the weights disagree
        self.g1.add_edge('A', 'B', weight=2)
        assert_false(  nx.is_isomorphic(self.g1, self.g2,
                                        node_match=self.nm, weight='weight') )

class TestEdgeMatch_MultiGraph(object):
    def setUp(self):
        self.g1 = nx.MultiGraph()
        self.g2 = nx.MultiGraph()
        self.GM = nx.MultiGraphMatcher
        self.build()

    def build(self):
        g1 = self.g1
        g2 = self.g2

        # We will assume integer weights only.
        g1.add_edge('A', 'B', color='green', weight=0)
        g1.add_edge('A', 'B', color='red', weight=1)
        g1.add_edge('A', 'B', color='red', weight=2)

        g2.add_edge('C', 'D', color='green', weight=1)
        g2.add_edge('C', 'D', color='red', weight=0)
        g2.add_edge('C', 'D', color='red', weight=2)

    def test_weights_only(self):
        assert_true( nx.is_isomorphic(self.g1, self.g2, weight='weight') )

    def test_colors_only(self):
        def em(g1_attrs, g2_attrs):
            attr = 'color'
            default = ''
            return g1_attrs.get(attr, default) == g2_attrs.get(attr, default)
        gm = self.GM(self.g1, self.g2, edge_match=em)
        assert_true( gm.is_isomorphic() )

    def test_colorsandweights1(self):
        def em(g1_attrs, g2_attrs):
            attrs = [('color', ''), ('weight', 1)]

            data1 = set([])
            for eattrs in g1_attrs.values():
                eattrs = eattrs.items()
                x = tuple( g1_attrs.get(attr, d) for attr, d in eattrs )
                data1.add( tuple(x) )

            data2 = set([])
            for eattrs in g2_attrs.values():
                eattrs = eattrs.items()
                x = tuple( g2_attrs.get(attr, d) for attr, d in eattrs )
                data2.add( tuple(x) )

            return data1 == data2

        gm = self.GM(self.g1, self.g2, edge_match=em)
        assert_false( gm.is_isomorphic() )

    def test_colorsandweights2(self):
        # same as test_colorsandweights1, but using the factory function
        attrs = {'color': '', 'weight': 1}
        em = nx.isomorphism.multi_attrcompare_factory_setlike(attrs)
        gm = self.GM(self.g1, self.g2, edge_match=em)
        assert_false( gm.is_isomorphic() )

class TestEdgeMatch_DiGraph(TestNodeMatch_Graph):
    def setUp(self):
        self.g1 = nx.DiGraph()
        self.g2 = nx.DiGraph()
        self.build()

class TestEdgeMatch_MultiDiGraph(TestEdgeMatch_MultiGraph):
    def setUp(self):
        self.g1 = nx.MultiDiGraph()
        self.g2 = nx.MultiDiGraph()
        self.GM = nx.MultiDiGraphMatcher
        self.build()

