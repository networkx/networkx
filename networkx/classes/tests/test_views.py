from nose.tools import assert_equal, assert_not_equal, \
        assert_true, assert_false, assert_raises

import networkx as nx


# Nodes
class test_nodeview(object):
    def setup(self):
        self.G = nx.path_graph(9)

    def test_pickle(self):
        import pickle
        nv = self.G.nodes()  # nx.NodeView(self.G)
        pnv = pickle.loads(pickle.dumps(nv, -1))
        assert_equal(nv, pnv)
        assert_equal(nv.__slots__, pnv.__slots__)

    def test_repr(self):
        nv = self.G.nodes()  # nx.NodeView(self.G)
        assert_equal(str(nv), "NodeView((0, 1, 2, 3, 4, 5, 6, 7, 8))")

    def test_contains(self):
        nv = self.G.nodes()  # nx.NodeView(self.G)
        assert_true(7 in nv)
        assert_false(9 in nv)
        self.G.remove_node(7)
        self.G.add_node(9)
        assert_false(7 in nv)
        assert_true(9 in nv)

    def test_contains_data(self):
        nvd = self.G.nodes(data=True)  # nx.NodeView(self.G, data=True)
        self.G.node[3]['foo'] = 'bar'
        assert_true((7, {}) in nvd)
        assert_true((3, {'foo': 'bar'}) in nvd)
        nvdf = self.G.nodes(data='foo', default='biz')
        assert_true((7, 'biz') in nvdf)
        assert_true((3, 'bar') in nvdf)
        assert_true((3, nvdf[3]) in nvdf)

    def test_getitem(self):
        nvd = self.G.nodes(data=True)  # nx.NodeView(self.G, data=True)
        self.G.node[3]['foo'] = 'bar'
        assert_equal(nvd[3], {'foo': 'bar'})
        nvdf = self.G.nodes(data='foo', default='biz')
        assert_true(nvdf[7], 'biz')
        assert_equal(nvdf[3], 'bar')

    def test_iter(self):
        nv = self.G.nodes()  # nx.NodeView(self.G)
        for i, n in enumerate(nv):
            assert_equal(i, n)
        inv = iter(nv)
        assert_equal(next(inv), 0)
        assert_not_equal(iter(nv), nv)
        assert_equal(iter(inv), inv)
        inv2 = iter(nv)
        next(inv2)
        assert_equal(list(inv), list(inv2))
        # odd case where NodeView calls NodeDataView with data=False
        nnv = nv(data=False)
        for i, n in enumerate(nnv):
            assert_equal(i, n)

    def test_iter_data(self):
        nv = self.G.nodes(data=True)  # nx.NodeView(self.G, data=True)
        for i, (n, d) in enumerate(nv):
            assert_equal(i, n)
            assert_equal(d, {})
        inv = iter(nv)
        assert_equal(next(inv), (0, {}))
        self.G.node[3]['foo'] = 'bar'
        for n, d in nv:
            if n == 3:
                assert_equal(d, {'foo': 'bar'})
                break

    def test_len(self):
        nv = self.G.nodes()  # nx.NodeView(self.G)
        assert_equal(len(nv), 9)
        self.G.remove_node(7)
        assert_equal(len(nv), 8)
        self.G.add_node(9)
        assert_equal(len(nv), 9)

    def test_and(self):
        # print("G & H nodes:", gnv & hnv)
        nv = self.G.nodes()  # nx.NodeView(self.G)
        some_nodes = {n for n in range(5, 12)}
        assert_equal(nv & some_nodes, {n for n in range(5, 9)})
        assert_equal(some_nodes & nv, {n for n in range(5, 9)})

    def test_or(self):
        # print("G | H nodes:", gnv | hnv)
        nv = self.G.nodes()  # nx.NodeView(self.G)
        some_nodes = {n for n in range(5, 12)}
        assert_equal(nv | some_nodes, {n for n in range(12)})
        assert_equal(some_nodes | nv, {n for n in range(12)})

    def test_xor(self):
        # print("G ^ H nodes:", gnv ^ hnv)
        nv = self.G.nodes()  # nx.NodeView(self.G)
        some_nodes = {n for n in range(5, 12)}
        assert_equal(nv ^ some_nodes, {0, 1, 2, 3, 4, 9, 10, 11})
        assert_equal(some_nodes ^ nv, {0, 1, 2, 3, 4, 9, 10, 11})

    def test_sub(self):
        # print("G - H nodes:", gnv - hnv)
        nv = self.G.nodes()  # nx.NodeView(self.G)
        some_nodes = {n for n in range(5, 12)}
        assert_equal(nv - some_nodes, {n for n in range(5)})
        assert_equal(some_nodes - nv, {n for n in range(9, 12)})


# Edges Data View
class test_edgedataview(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.eview = nx.EdgeView

        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_iterdata(self):
        G = self.G.copy()
        evr = self.eview(G)
        ev = evr(data=True)
        for u, v, d in ev:
            pass
        assert_equal(d, {})
        ev = evr(data='foo', default=1)
        for u, v, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2, 3), foo='bar')
        ev = evr(data=True)
        for e in ev:
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], {'foo': 'bar'})
                assert_equal(len(e), 3)
                checked = True
                break
        assert_true(checked)
        ev = evr(data='foo', default=1)
        for e in ev:
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], 'bar')
                assert_equal(len(e), 3)
                checked_wt = True
                break
        assert_true(checked_wt)

    def test_iter(self):
        evr = self.eview(self.G)
        ev = evr()
        for u, v in ev:
            pass
        iev = iter(ev)
        assert_equal(next(iev), (0, 1))
        assert_not_equal(iter(ev), ev)
        assert_equal(iter(iev), iev)

    def test_contains(self):
        evr = self.eview(self.G)
        ev = evr()
        if self.G.is_directed():
            assert_true((1, 2) in ev and (2, 1) not in ev)
        else:
            assert_true((1, 2) in ev and (2, 1) in ev)
        assert_false((1, 4) in ev)
        assert_false((1, 90) in ev)
        assert_false((90, 1) in ev)

    def test_len(self):
        evr = self.eview(self.G)
        ev = evr()
        num_ed = 9 if self.G.is_multigraph() else 8
        assert_equal(len(ev), num_ed)
        ev = evr(data='foo')
        assert_equal(len(ev), num_ed)


# Edges
class test_edgeview(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.eview = nx.EdgeView

        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "EdgeView([(0, 1), (1, 2), (2, 3), (3, 4), " + \
            "(4, 5), (5, 6), (6, 7), (7, 8)])"
        assert_equal(str(ev), rep)

    def test_call(self):
        ev = self.eview(self.G)
        assert_equal(id(ev), id(ev()))
        assert_not_equal(id(ev), id(ev(data=True)))
        assert_not_equal(id(ev), id(ev(nbunch=1)))

    def test_iter(self):
        ev = self.eview(self.G)
        for u, v in ev:
            pass
        iev = iter(ev)
        assert_equal(next(iev), (0, 1))
        assert_not_equal(iter(ev), ev)
        assert_equal(iter(iev), iev)

    def test_contains(self):
        ev = self.eview(self.G)
        edv = ev()
        if self.G.is_directed():
            assert_true((1, 2) in ev and (2, 1) not in ev)
            assert_true((1, 2) in edv and (2, 1) not in edv)
        else:
            assert_true((1, 2) in ev and (2, 1) in ev)
            assert_true((1, 2) in edv and (2, 1) in edv)
        assert_false((1, 4) in ev)
        assert_false((1, 4) in edv)
        # edge not in graph
        assert_false((1, 90) in ev)
        assert_false((90, 1) in ev)
        assert_false((1, 90) in edv)
        assert_false((90, 1) in edv)

    def test_len(self):
        ev = self.eview(self.G)
        num_ed = 9 if self.G.is_multigraph() else 8
        assert_equal(len(ev), num_ed)
        ev = ev(data='foo')
        assert_equal(len(ev), num_ed)

    def test_and(self):
        # print("G & H edges:", gnv & hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        if self.G.is_directed():
            assert_true(some_edges & ev, {(0, 1)})
            assert_true(ev & some_edges, {(0, 1)})
        else:
            assert_equal(ev & some_edges, {(0, 1), (1, 0)})
            assert_equal(some_edges & ev, {(0, 1), (1, 0)})
        return

    def test_or(self):
        # print("G | H edges:", gnv | hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        result1 = {(n, n+1) for n in range(8)}
        result1.update(some_edges)
        result2 = {(n+1, n) for n in range(8)}
        result2.update(some_edges)
        assert_true((ev | some_edges) in (result1, result2))
        assert_true((some_edges | ev) in (result1, result2))

    def test_xor(self):
        # print("G ^ H edges:", gnv ^ hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        if self.G.is_directed():
            result = {(n, n+1) for n in range(1, 8)}
            result.update({(1, 0), (0, 2)})
            assert_equal(ev ^ some_edges, result)
        else:
            result = {(n, n+1) for n in range(1, 8)}
            result.update({(0, 2)})
            assert_equal(ev ^ some_edges, result)
        return

    def test_sub(self):
        # print("G - H edges:", gnv - hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1), (1, 0), (0, 2)}
        result = {(n, n + 1) for n in range(8)}
        result.remove((0, 1))
        assert_true(ev - some_edges, result)


class test_directed_edges(test_edgeview):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = nx.OutEdgeView

        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "OutEdgeView([(0, 1), (1, 2), (2, 3), (3, 4), " + \
            "(4, 5), (5, 6), (6, 7), (7, 8)])"
        assert_equal(str(ev), rep)


class test_inedges(test_edgeview):
    def setup(self):
        self.G = nx.path_graph(9, nx.DiGraph())
        self.eview = nx.InEdgeView

        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "InEdgeView([(0, 1), (1, 2), (2, 3), (3, 4), " + \
            "(4, 5), (5, 6), (6, 7), (7, 8)])"
        assert_equal(str(ev), rep)


class test_multiedges(test_edgeview):
    def setup(self):
        self.G = nx.path_graph(9, nx.MultiGraph())
        self.G.add_edge(1, 2, key=3, foo='bar')
        self.eview = nx.MultiEdgeView

        def modify_edge(G, e, **kwds):
            if len(e) == 2:
                e = e + (0,)
            G.edge[e[0]][e[1]][e[2]].update(kwds)
        self.modify_edge = modify_edge

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "MultiEdgeView([(0, 1, 0), (1, 2, 0), (1, 2, 3), (2, 3, 0), " + \
            "(3, 4, 0), (4, 5, 0), (5, 6, 0), (6, 7, 0), (7, 8, 0)])"
        assert_equal(str(ev), rep)

    def test_call(self):
        ev = self.eview(self.G)
        assert_equal(id(ev), id(ev(keys=True)))
        assert_not_equal(id(ev), id(ev(data=True)))
        assert_not_equal(id(ev), id(ev(nbunch=1)))

    def test_iter(self):
        ev = self.eview(self.G)
        for u, v, k in ev:
            pass
        iev = iter(ev)
        assert_equal(next(iev), (0, 1, 0))
        assert_not_equal(iter(ev), ev)
        assert_equal(iter(iev), iev)

    def test_iterkeys(self):
        G = self.G.copy()
        evr = self.eview(G)
        ev = evr(keys=True)
        for u, v, k in ev:
            pass
        assert_equal(k, 0)
        ev = evr(keys=True, data="foo", default=1)
        for u, v, k, wt in ev:
            pass
        assert_equal(wt, 1)

        self.modify_edge(G, (2, 3, 0), foo='bar')
        ev = evr(keys=True, data=True)
        for e in ev:
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], 0)
                assert_equal(e[3], {'foo': 'bar'})
                assert_equal(len(e), 4)
                checked = True
                break
        assert_true(checked)
        ev = evr(keys=True, data='foo', default=1)
        for e in ev:
            if set(e[:2]) == {1, 2} and e[2] == 3:
                assert_equal(e[3], 'bar')
            if set(e[:2]) == {1, 2} and e[2] == 0:
                assert_equal(e[3], 1)
            if set(e[:2]) == {2, 3}:
                assert_equal(e[2], 0)
                assert_equal(e[3], 'bar')
                assert_equal(len(e), 4)
                checked_wt = True
        assert_true(checked_wt)
        ev = evr(keys=True)
        for e in ev:
            assert_equal(len(e), 3)
        elist = sorted([(i, i+1, 0) for i in range(8)] + [(1, 2, 3)])
        assert_equal(sorted(list(ev)), elist)
        # test order of arguments:graph, nbunch, data, keys, default
        ev = evr((1, 2), 'foo', True, 1)
        for e in ev:
            if set(e[:2]) == {1, 2}:
                assert_true(e[2] in {0, 3})
                if e[2] == 3:
                    assert_equal(e[3], 'bar')
                else:  # e[2] == 0
                    assert_equal(e[3], 1)
        if G.is_directed():
            assert_equal(len(list(ev)), 3)
        else:
            assert_equal(len(list(ev)), 4)

    def test_or(self):
        # print("G | H edges:", gnv | hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1, 0), (1, 0, 0), (0, 2, 0)}
        result = {(n, n+1, 0) for n in range(8)}
        result.update(some_edges)
        result.update({(1, 2, 3)})
        assert_equal(ev | some_edges, result)
        assert_equal(some_edges | ev, result)

    def test_sub(self):
        # print("G - H edges:", gnv - hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1, 0), (1, 0, 0), (0, 2, 0)}
        result = {(n, n + 1, 0) for n in range(8)}
        result.remove((0, 1, 0))
        result.update({(1, 2, 3)})
        assert_true(ev - some_edges, result)
        assert_true(some_edges - ev, result)

    def test_xor(self):
        # print("G ^ H edges:", gnv ^ hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1, 0), (1, 0, 0), (0, 2, 0)}
        if self.G.is_directed():
            result = {(n, n+1, 0) for n in range(1, 8)}
            result.update({(1, 0, 0), (0, 2, 0), (1, 2, 3)})
            assert_equal(ev ^ some_edges, result)
            assert_equal(some_edges ^ ev, result)
        else:
            result = {(n, n+1, 0) for n in range(1, 8)}
            result.update({(0, 2, 0), (1, 2, 3)})
            assert_equal(ev ^ some_edges, result)
            assert_equal(some_edges ^ ev, result)

    def test_and(self):
        # print("G & H edges:", gnv & hnv)
        ev = self.eview(self.G)
        some_edges = {(0, 1, 0), (1, 0, 0), (0, 2, 0)}
        if self.G.is_directed():
            assert_equal(ev & some_edges, {(0, 1, 0)})
            assert_equal(some_edges & ev, {(0, 1, 0)})
        else:
            assert_equal(ev & some_edges, {(0, 1, 0), (1, 0, 0)})
            assert_equal(some_edges & ev, {(0, 1, 0), (1, 0, 0)})


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

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "OutMultiEdgeView([(0, 1, 0), (1, 2, 0), (1, 2, 3), (2, 3, 0),"\
              + " (3, 4, 0), (4, 5, 0), (5, 6, 0), (6, 7, 0), (7, 8, 0)])"
        assert_equal(str(ev), rep)


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

    def test_repr(self):
        ev = self.eview(self.G)
        rep = "InMultiEdgeView([(0, 1, 0), (1, 2, 0), (1, 2, 3), (2, 3, 0), "\
              + "(3, 4, 0), (4, 5, 0), (5, 6, 0), (6, 7, 0), (7, 8, 0)])"
        assert_equal(str(ev), rep)


# Degrees
class test_degreeview(object):
    GRAPH = nx.Graph
    dview = nx.DegreeView

    def setup(self):
        self.G = nx.path_graph(6, self.GRAPH())
        self.G.add_edge(1, 3, foo=2)
        self.G.add_edge(1, 3, foo=3)

        def modify_edge(G, e, **kwds):
            G.edge[e[0]][e[1]].update(kwds)
        self.modify_edge = modify_edge

    def test_repr(self):
        dv = self.G.degree()  # nx.NodeView(self.G)
        rep = "DegreeView({0: 1, 1: 3, 2: 2, 3: 3, 4: 2, 5: 1})"
        assert_equal(str(dv), rep)

    def test_iter(self):
        dv = self.dview(self.G)
        for n, d in dv:
            pass
        idv = iter(dv)
        assert_not_equal(iter(dv), dv)
        assert_equal(iter(idv), idv)
        assert_equal(next(idv), (0, dv[0]))
        assert_equal(next(idv), (1, dv[1]))
        # weighted
        dv = self.dview(self.G, weight='foo')
        for n, d in dv:
            pass
        idv = iter(dv)
        assert_not_equal(iter(dv), dv)
        assert_equal(iter(idv), idv)
        assert_equal(next(idv), (0, dv[0]))
        assert_equal(next(idv), (1, dv[1]))

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 1)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 2), (3, 3)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 5)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 2), (3, 5)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 1)
        assert_equal(dvd[1], 5)
        assert_equal(dvd[2], 2)
        assert_equal(dvd[3], 5)

    def test_len(self):
        dv = self.dview(self.G)
        assert_equal(len(dv), 6)


class test_didegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.DiDegreeView

    def test_repr(self):
        dv = self.G.degree()  # nx.NodeView(self.G)
        rep = "DiDegreeView({0: 1, 1: 3, 2: 2, 3: 3, 4: 2, 5: 1})"
        assert_equal(str(dv), rep)


class test_outdegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.OutDegreeView

    def test_repr(self):
        dv = self.G.out_degree()  # nx.NodeView(self.G)
        rep = "OutDegreeView({0: 1, 1: 2, 2: 1, 3: 1, 4: 1, 5: 0})"
        assert_equal(str(dv), rep)

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 1)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 1), (3, 1)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 4)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 1), (3, 1)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 1)
        assert_equal(dvd[1], 4)
        assert_equal(dvd[2], 1)
        assert_equal(dvd[3], 1)


class test_indegreeview(test_degreeview):
    GRAPH = nx.DiGraph
    dview = nx.InDegreeView

    def test_repr(self):
        dv = self.G.in_degree()  # nx.NodeView(self.G)
        rep = "InDegreeView({0: 0, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1})"
        assert_equal(str(dv), rep)

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 0)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 1), (3, 2)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 0)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 1), (3, 4)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 0)
        assert_equal(dvd[1], 1)
        assert_equal(dvd[2], 1)
        assert_equal(dvd[3], 4)


class test_multidegreeview(test_degreeview):
    GRAPH = nx.MultiGraph
    dview = nx.MultiDegreeView

    def test_repr(self):
        dv = self.G.degree()  # nx.NodeView(self.G)
        rep = "MultiDegreeView({0: 1, 1: 4, 2: 2, 3: 4, 4: 2, 5: 1})"
        assert_equal(str(dv), rep)

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 1)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 2), (3, 4)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 7)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 2), (3, 7)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 1)
        assert_equal(dvd[1], 7)
        assert_equal(dvd[2], 2)
        assert_equal(dvd[3], 7)


class test_dimultidegreeview(test_multidegreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.DiMultiDegreeView

    def test_repr(self):
        dv = self.G.degree()  # nx.NodeView(self.G)
        rep = "DiMultiDegreeView({0: 1, 1: 4, 2: 2, 3: 4, 4: 2, 5: 1})"
        assert_equal(str(dv), rep)


class test_outmultidegreeview(test_degreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.OutMultiDegreeView

    def test_repr(self):
        dv = self.G.out_degree()  # nx.NodeView(self.G)
        rep = "OutMultiDegreeView({0: 1, 1: 3, 2: 1, 3: 1, 4: 1, 5: 0})"
        assert_equal(str(dv), rep)

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 1)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 1), (3, 1)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 6)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 1), (3, 1)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 1)
        assert_equal(dvd[1], 6)
        assert_equal(dvd[2], 1)
        assert_equal(dvd[3], 1)


class test_inmultidegreeview(test_degreeview):
    GRAPH = nx.MultiDiGraph
    dview = nx.InMultiDegreeView

    def test_repr(self):
        dv = self.G.in_degree()  # nx.NodeView(self.G)
        rep = "InMultiDegreeView({0: 0, 1: 1, 2: 1, 3: 3, 4: 1, 5: 1})"
        assert_equal(str(dv), rep)

    def test_nbunch(self):
        dv = self.dview(self.G)
        dvn = dv(0)
        assert_equal(dvn, 0)
        dvn = dv([2, 3])
        assert_equal(sorted(dvn), [(2, 1), (3, 3)])

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

    def test_weight(self):
        dv = self.dview(self.G)
        dvw = dv(0, weight='foo')
        assert_equal(dvw, 0)
        dvw = dv(1, weight='foo')
        assert_equal(dvw, 1)
        dvw = dv([2, 3], weight='foo')
        assert_equal(sorted(dvw), [(2, 1), (3, 6)])
        dvd = dict(dv(weight='foo'))
        assert_equal(dvd[0], 0)
        assert_equal(dvd[1], 1)
        assert_equal(dvd[2], 1)
        assert_equal(dvd[3], 6)
