from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

import networkx as nx
from networkx import (NodeView, EdgeView, DiEdgeView, InDiEdgeView,
                      MultiEdgeView, MultiDiEdgeView, InMultiDiEdgeView)

class test_nodeview(object):
    def setup(self):
        self.G = nx.path_graph(9)

    def test_str(self):
        nv = nx.NodeView(self.G)
        assert_equal(str(nv), "[0, 1, 2, 3, 4, 5, 6, 7, 8]")

    def test_contains(self):
        nv = nx.NodeView(self.G)
        assert_true(7 in nv)
        assert_false(9 in nv)
        self.G.remove_node(7)
        self.G.add_node(9)
        assert_false(7 in nv)
        assert_true(9 in nv)

    def test_contains_data(self):
        nv = nx.NodeView(self.G, data=True)
        self.G.node[3]['foo']='bar'
        assert_true((7,{}) in nv)
        assert_true((3,{'foo': 'bar'}) in nv)
        assert_true(7 in nv)
        assert_false(9 in nv)
        self.G.remove_node(7)
        self.G.add_node(9)
        assert_false(7 in nv)
        assert_true(9 in nv)

    def test_iter(self):
        nv = nx.NodeView(self.G)
        for i,n in enumerate(nv):
            assert_equal(i, n)
        inv = iter(nv)
        assert_equal(next(inv), 0)
        assert_not_equal(iter(nv), nv)
        assert_equal(iter(inv), inv)
        inv2 = iter(nv)
        next(inv2)
        assert_equal(list(inv), list(inv2))

    def test_iter_data(self):
        nv = NodeView(self.G, data=True)
        for i,(n,d) in enumerate(nv):
            assert_equal(i, n)
            assert_equal(d, {})
        inv = iter(nv)
        assert_equal(next(inv), (0, {}))
        self.G.node[3]['foo']='bar'
        for n, d in nv:
            if n == 3:
                assert_equal(d, {'foo': 'bar'})
                break

    def test_len(self):
        nv = NodeView(self.G)
        assert_equal(len(nv), 9)
        self.G.remove_node(7)
        assert_equal(len(nv), 8)
        self.G.add_node(9)
        assert_equal(len(nv), 9)

    def test_and(self):
        pass
    def test_or(self):
        pass
    def test_xor(self):
        pass
    def test_sub(self):
        pass

class test_edges(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.eview = EdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge
    # print("G & H edges:", gnv & hnv)
    # print("G - H edges:", gnv - hnv)
    # print("G | H edges:", gnv | hnv)
    # print("G ^ H edges:", gnv ^ hnv)
    def test_iter(self):
        ev = self.eview(self.G)
        print(type(ev))
        print(type(self.G))
        print(list(ev))
        for u,v in ev:
            pass
        print(list(ev))
        iev = iter(ev)
        assert_equal(next(iev), (0,1))
        assert_not_equal(iter(ev), ev)
        assert_equal(iter(iev), iev)
    def test_iterdata(self):
        EdgeView = self.eview
        G = self.G.copy()
        ev = EdgeView(G, data=True)
        for u, v, d in ev:
            pass
        assert_equal(d, {})
        ev = EdgeView(G, data='foo', default=1)
        for u, v, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2,3), foo='bar')
        ev = EdgeView(G, data=True)
        for e in ev:
            if set(e[:2]) == {2,3}:
                print(e)
                print(G.adj)
                assert_equal(e[2], {'foo': 'bar'})
                assert_equal(len(e), 3)
                checked = True
                break
        assert_true(checked)
        ev = EdgeView(G, data='foo', default=1)
        for e in ev:
            if set(e[:2]) == {2,3}:
                assert_equal(e[2], 'bar')
                assert_equal(len(e), 3)
                checked_wt = True
                break
        assert_true(checked_wt)

class test_directed_edges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = DiEdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

class test_inedges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = InDiEdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

class test_multiedges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiGraph())
        self.G.add_edge(1, 2, key=3, attr_dict={'foo': 'bar'})
        self.eview = MultiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge
    def test_iterkeys(self):
        EdgeView = self.eview
        G = self.G.copy()
        ev = EdgeView(G, keys=True)
        for u, v, k in ev:
            pass
        assert_equal(k, 0)
        ev = EdgeView(G, keys=True, data="foo", default=1)
        for u, v, k, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2, 3, 0), foo='bar')
        ev = EdgeView(G, keys=True, data=True)
        for e in ev:
            if set(e[:2]) == {2,3}:
                assert_equal(e[2], 0)
                assert_equal(e[3], {'foo': 'bar'})
                assert_equal(len(e), 4)
                checked = True
                break
        assert_true(checked)
        ev = EdgeView(G, keys=True, data='foo', default=1)
        for e in ev:
            if set(e[:2]) == {1,2} and e[2] == 3:
                assert_equal(e[3], 'bar')
            if set(e[:2]) == {1,2} and e[2] == 0:
                assert_equal(e[3], 1)
            if set(e[:2]) == {2,3}:
                assert_equal(e[2], 0)
                assert_equal(e[3], 'bar')
                assert_equal(len(e), 4)
                checked_wt = True
        assert_true(checked_wt)
        ev = EdgeView(G, keys=True)
        for e in ev:
            assert_equal(len(e), 3)
        elist = sorted([(i, i+1, 0) for i in range(8)] + [(1, 2, 3)])
        assert_equal(sorted(list(ev)), elist)


class test_directed_multiedges(test_multiedges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiDiGraph())
        self.G.add_edge(1, 2, key=3, attr_dict={'foo': 'bar'})
        self.eview = MultiDiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge

class test_in_multiedges(test_multiedges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiDiGraph())
        self.G.add_edge(1, 2, key=3, attr_dict={'foo': 'bar'})
        self.eview = InMultiDiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge

