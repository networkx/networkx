from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

import networkx as nx
#   Testing these classes
#from networkx import (NodeView, EdgeView, OutEdgeView, InEdgeView,
#      MultiEdgeView, OutMultiEdgeView, InMultiEdgeView,
#      DegreeView, DiDegreeView, OutDegreeView, InDegreeView,
#      MultiDegreeView, DiMultiDegreeView, OutMultiDegreeView, InMultiDegreeView)

## Nodes
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
        nv = nx.NodeView(self.G, data=True)
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
        nv = nx.NodeView(self.G)
        assert_equal(len(nv), 9)
        self.G.remove_node(7)
        assert_equal(len(nv), 8)
        self.G.add_node(9)
        assert_equal(len(nv), 9)

    def test_and(self):
        # print("G & H nodes:", gnv & hnv)
        nv = nx.NodeView(self.G)
        some_nodes = {n for n in range(5,12)}
        assert_equal(nv & some_nodes, {n for n in range(5,9)})

    def test_or(self):
        # print("G | H nodes:", gnv | hnv)
        nv = nx.NodeView(self.G)
        some_nodes = {n for n in range(5,12)}
        assert_equal(nv | some_nodes, {n for n in range(12)})

    def test_xor(self):
        # print("G ^ H nodes:", gnv ^ hnv)
        nv = nx.NodeView(self.G)
        some_nodes = {n for n in range(5,12)}
        assert_equal(nv ^ some_nodes, {0, 1, 2, 3, 4, 9, 10, 11})

    def test_sub(self):
        # print("G - H nodes:", gnv - hnv)
        nv = nx.NodeView(self.G)
        some_nodes = {n for n in range(5,12)}
        assert_equal(nv - some_nodes, {n for n in range(5)})


## Edges
class test_edges(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.eview = nx.EdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_iter(self):
        ev = self.eview(self.G)
        for u,v in ev:
            pass
        iev = iter(ev)
        assert_equal(next(iev), (0,1))
        assert_not_equal(iter(ev), ev)
        assert_equal(iter(iev), iev)

    def test_iterdata(self):
        G = self.G.copy()
        ev = self.eview(G, data=True)
        for u, v, d in ev:
            pass
        assert_equal(d, {})
        ev = self.eview(G, data='foo', default=1)
        for u, v, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2, 3), foo='bar')
        ev = self.eview(G, data=True)
        for e in ev:
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], {'foo': 'bar'})
                assert_equal(len(e), 3)
                checked = True
                break
        assert_true(checked)
        ev = self.eview(G, data='foo', default=1)
        for e in ev:
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], 'bar')
                assert_equal(len(e), 3)
                checked_wt = True
                break
        assert_true(checked_wt)

    def test_contains(self):
        ev = self.eview(self.G)
        assert_true((1, 2) in ev or (2, 1) in ev)
        assert_false((1, 4) in ev)

    def test_len(self):
        ev = self.eview(self.G)
        num_ed = 9 if self.G.is_multigraph() else 8
        print(ev)
        print(len(ev))
        print(type(len(ev)))
        print(type(num_ed))
        assert_equal(len(ev), num_ed)
        ev = self.eview(self.G, data='foo')
        assert_equal(len(ev), num_ed)


    def test_and(self):
        # print("G & H edges:", gnv & hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        if not self.G.is_directed():
            assert_equal(ev & some_edges, {(0, 1), (1, 0)})
        else:
            assert_true((ev & some_edges) in ({(0, 1)}, {(1, 0)}))
        return

    def test_or(self):
        # print("G | H edges:", gnv | hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (0, 2)}
        result1 = {(n, n+1) for n in range(8)}
        result1.update(some_edges)
        result2 = {(n+1, n) for n in range(8)}
        result2.update(some_edges)
        assert_true((ev | some_edges) in (result1, result2))

    def test_xor(self):
        # print("G ^ H edges:", gnv ^ hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        if not self.G.is_directed():
            result = {(n, n+1) for n in range(1, 8)}
            result.update({(0, 2)})
            assert_equal(ev ^ some_edges, result)
        else:
            result1 = {(n, n+1) for n in range(8)}
            result1.update({(0, 2)})
            result2 = {(n, n+1) for n in range(1, 8)}
            result2.update({(1, 0), (0, 2)})
            assert_true((ev ^ some_edges) in (result1, result2))
        return

    def test_sub(self):
        # print("G - H edges:", gnv - hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        result1 = {(n, n + 1) for n in range(8)}
        result1.remove((0, 1))
        result2 = {(n + 1, n) for n in range(8)}
        result2.remove((1, 0))
        assert_true((ev - some_edges) in (result1, result2))




class test_directed_edges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = nx.OutEdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

class test_inedges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = nx.InEdgeView
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

class test_multiedges(test_edges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiGraph())
        self.G.add_edge(1, 2, key=3, foo='bar')
        self.eview = nx.MultiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge
    def test_iterkeys(self):
        eView = self.eview
        G = self.G.copy()
        ev = eView(G, keys=True)
        for u, v, k in ev:
            pass
        assert_equal(k, 0)
        ev = eView(G, keys=True, data="foo", default=1)
        for u, v, k, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2, 3, 0), foo='bar')
        ev = eView(G, keys=True, data=True)
        for e in ev:
            if set(e[:2]) == {2,3}:
                assert_equal(e[2], 0)
                assert_equal(e[3], {'foo': 'bar'})
                assert_equal(len(e), 4)
                checked = True
                break
        assert_true(checked)
        ev = eView(G, keys=True, data='foo', default=1)
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
        ev = eView(G, keys=True)
        for e in ev:
            assert_equal(len(e), 3)
        elist = sorted([(i, i+1, 0) for i in range(8)] + [(1, 2, 3)])
        assert_equal(sorted(list(ev)), elist)
        # test order of arguments:graph, nbunch, data, keys, default
        ev = eView(G, (1, 2), 'foo', True, 1)
        for e in ev:
            if set(e[:2]) == {1,2}:
                assert_true(e[2] in {0,3})
                if e[2] == 3:
                    assert_equal(e[3], 'bar')
                else:  # e[2] == 0
                    assert_equal(e[3], 1)
        if G.is_directed():
            assert_equal(len(list(ev)), 3)
        else:
            assert_equal(len(list(ev)), 4)

class test_directed_multiedges(test_multiedges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiDiGraph())
        self.G.add_edge(1, 2, key=3, foo='bar')
        self.eview = nx.OutMultiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge

class test_in_multiedges(test_multiedges):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiDiGraph())
        self.G.add_edge(1, 2, key=3, foo='bar')
        self.eview = nx.InMultiEdgeView
        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge


## Degrees
class test_degreeview(object):
    GRAPH = nx.Graph
    dview = nx.DegreeView
    def setup(self):
        self.G = nx.path_graph(9, self.GRAPH())
        self.G.add_edge(1, 3, foo=2)
        self.G.add_edge(1, 3, foo=3)
        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_iter(self):
        dv = self.dview(self.G)
        for n,d in dv:
            pass
        idv = iter(dv)
        assert_not_equal(iter(dv), dv)
        assert_equal(iter(idv), idv)
        assert_equal(next(idv), (0, dv[0]))
        assert_equal(next(idv), (1, dv[1]))
        # weighted
        dv = self.dview(self.G, weight='foo')
        for n,d in dv:
            pass
        idv = iter(dv)
        assert_not_equal(iter(dv), dv)
        assert_equal(iter(idv), idv)
        assert_equal(next(idv), (0, dv[0]))
        assert_equal(next(idv), (1, dv[1]))

    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 3)
        assert_equal(dv[2], 2)
        assert_equal(dv[3], 3)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 5)
        assert_equal(dv[2], 2)
        assert_equal(dv[3], 5)

    def test_len(self):
        dv = self.dview(self.G)
        assert_equal(len(dv), 9)

class test_didegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.DiDegreeView

class test_outdegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.OutDegreeView
    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 2)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 1)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 4)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 1)

class test_indegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.InDegreeView
    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 0)
        assert_equal(dv[1], 1)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 2)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 0)
        assert_equal(dv[1], 1)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 4)

class test_multidegreeview(test_degreeview):
    GRAPH = nx.MultiGraph
    dview = nx.MultiDegreeView
    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 4)
        assert_equal(dv[2], 2)
        assert_equal(dv[3], 4)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 7)
        assert_equal(dv[2], 2)
        assert_equal(dv[3], 7)

class test_dimultidegreeview(test_multidegreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.DiMultiDegreeView

class test_outmultidegreeview(test_degreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.OutMultiDegreeView
    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 3)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 1)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 1)
        assert_equal(dv[1], 6)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 1)

class test_inmultidegreeview(test_degreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.InMultiDegreeView
    def test_getitem(self):
        dv = self.dview(self.G)
        assert_equal(dv[0], 0)
        assert_equal(dv[1], 1)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 3)
        dv = self.dview(self.G, weight='foo')
        assert_equal(dv[0], 0)
        assert_equal(dv[1], 1)
        assert_equal(dv[2], 1)
        assert_equal(dv[3], 6)


