#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestWeightedPath:

    def setUp(self):
        from networkx import convert_node_labels_to_integers as cnlti
        self.grid=cnlti(nx.grid_2d_graph(4,4),first_label=1,ordering="sorted")
        self.cycle=nx.cycle_graph(7)
        self.directed_cycle=nx.cycle_graph(7,create_using=nx.DiGraph())
        self.XG=nx.DiGraph()
        self.XG.add_weighted_edges_from([('s','u',10) ,('s','x',5) ,
                                         ('u','v',1) ,('u','x',2) ,
                                         ('v','y',1) ,('x','u',3) ,
                                         ('x','v',5) ,('x','y',2) ,
                                         ('y','s',7) ,('y','v',6)])
        self.MXG=nx.MultiDiGraph(self.XG)
        self.MXG.add_edge('s','u',weight=15)
        self.XG2=nx.DiGraph()
        self.XG2.add_weighted_edges_from([[1,4,1],[4,5,1],
                                          [5,6,1],[6,3,1],
                                          [1,3,50],[1,2,100],[2,3,100]])

        self.XG3=nx.Graph()
        self.XG3.add_weighted_edges_from([ [0,1,2],[1,2,12],
                                           [2,3,1],[3,4,5],
                                           [4,5,1],[5,0,10] ])

        self.XG4=nx.Graph()
        self.XG4.add_weighted_edges_from([ [0,1,2],[1,2,2],
                                           [2,3,1],[3,4,1],
                                           [4,5,1],[5,6,1],
                                           [6,7,1],[7,0,1] ])
        self.MXG4=nx.MultiGraph(self.XG4)
        self.MXG4.add_edge(0,1,weight=3)
        self.G=nx.DiGraph()  # no weights
        self.G.add_edges_from([('s','u'), ('s','x'),
                          ('u','v'), ('u','x'),
                          ('v','y'), ('x','u'),
                          ('x','v'), ('x','y'),
                          ('y','s'), ('y','v')])

    def test_dijkstra(self):
        (D,P)= nx.single_source_dijkstra(self.XG,'s')
        assert_equal(P['v'], ['s', 'x', 'u', 'v'])
        assert_equal(D['v'],9)

        assert_equal(nx.single_source_dijkstra_path(self.XG,'s')['v'],
                     ['s', 'x', 'u', 'v'])
        assert_equal(nx.single_source_dijkstra_path_length(self.XG,'s')['v'],9)

        assert_equal(nx.single_source_dijkstra(self.XG,'s')[1]['v'],
                     ['s', 'x', 'u', 'v'])

        assert_equal(nx.single_source_dijkstra_path(self.MXG,'s')['v'],
                     ['s', 'x', 'u', 'v'])

        GG=self.XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG['u']['x']['weight']=2
        (D,P)= nx.single_source_dijkstra(GG,'s')
        assert_equal(P['v'] , ['s', 'x', 'u', 'v'])
        assert_equal(D['v'],8)     # uses lower weight of 2 on u<->x edge
        assert_equal(nx.dijkstra_path(GG,'s','v'), ['s', 'x', 'u', 'v'])
        assert_equal(nx.dijkstra_path_length(GG,'s','v'),8)

        assert_equal(nx.dijkstra_path(self.XG2,1,3), [1, 4, 5, 6, 3])
        assert_equal(nx.dijkstra_path(self.XG3,0,3), [0, 1, 2, 3])
        assert_equal(nx.dijkstra_path_length(self.XG3,0,3),15)
        assert_equal(nx.dijkstra_path(self.XG4,0,2), [0, 1, 2])
        assert_equal(nx.dijkstra_path_length(self.XG4,0,2), 4)
        assert_equal(nx.dijkstra_path(self.MXG4,0,2), [0, 1, 2])
        assert_equal(nx.single_source_dijkstra(self.G,'s','v')[1]['v'],
                     ['s', 'u', 'v'])
        assert_equal(nx.single_source_dijkstra(self.G,'s')[1]['v'],
                     ['s', 'u', 'v'])

        assert_equal(nx.dijkstra_path(self.G,'s','v'), ['s', 'u', 'v'])
        assert_equal(nx.dijkstra_path_length(self.G,'s','v'), 2)

        # NetworkXError: node s not reachable from moon
        assert_raises(nx.NetworkXNoPath,nx.dijkstra_path,self.G,'s','moon')
        assert_raises(nx.NetworkXNoPath,nx.dijkstra_path_length,self.G,'s','moon')

        assert_equal(nx.dijkstra_path(self.cycle,0,3),[0, 1, 2, 3])
        assert_equal(nx.dijkstra_path(self.cycle,0,4), [0, 6, 5, 4])

        assert_equal(nx.single_source_dijkstra(self.cycle,0,0),({0:0}, {0:[0]}) )

    def test_bidirectional_dijkstra(self):
        assert_equal(nx.bidirectional_dijkstra(self.XG, 's', 'v'),
                     (9, ['s', 'x', 'u', 'v']))
        (dist,path) = nx.bidirectional_dijkstra(self.G,'s','v')
        assert_equal(dist,2)
        # skip this test, correct path could also be ['s','u','v']
#        assert_equal(nx.bidirectional_dijkstra(self.G,'s','v'),
#                     (2, ['s', 'x', 'v']))
        assert_equal(nx.bidirectional_dijkstra(self.cycle,0,3),
                     (3, [0, 1, 2, 3]))
        assert_equal(nx.bidirectional_dijkstra(self.cycle,0,4),
                     (3, [0, 6, 5, 4]))
        assert_equal(nx.bidirectional_dijkstra(self.XG3,0,3),
                     (15, [0, 1, 2, 3]))
        assert_equal(nx.bidirectional_dijkstra(self.XG4,0,2),
                     (4, [0, 1, 2]))

        # need more tests here
        assert_equal(nx.dijkstra_path(self.XG,'s','v'),
                     nx.single_source_dijkstra_path(self.XG,'s')['v'])


    @raises(nx.NetworkXNoPath)
    def test_bidirectional_dijkstra_no_path(self):
        G = nx.Graph()
        G.add_path([1,2,3])
        G.add_path([4,5,6])
        path = nx.bidirectional_dijkstra(G,1,6)

    def test_dijkstra_predecessor(self):
        G=nx.path_graph(4)
        assert_equal(nx.dijkstra_predecessor_and_distance(G,0),
                     ({0: [], 1: [0], 2: [1], 3: [2]}, {0: 0, 1: 1, 2: 2, 3: 3}))
        G=nx.grid_2d_graph(2,2)
        pred,dist=nx.dijkstra_predecessor_and_distance(G,(0,0))
        assert_equal(sorted(pred.items()),
                     [((0, 0), []), ((0, 1), [(0, 0)]),
                      ((1, 0), [(0, 0)]), ((1, 1), [(0, 1), (1, 0)])])
        assert_equal(sorted(dist.items()),
                     [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 2)])

        XG=nx.DiGraph()
        XG.add_weighted_edges_from([('s','u',10) ,('s','x',5) ,
                                    ('u','v',1) ,('u','x',2) ,
                                    ('v','y',1) ,('x','u',3) ,
                                    ('x','v',5) ,('x','y',2) ,
                                    ('y','s',7) ,('y','v',6)])
        (P,D)= nx.dijkstra_predecessor_and_distance(XG,'s')
        assert_equal(P['v'],['u'])
        assert_equal(D['v'],9)
        (P,D)= nx.dijkstra_predecessor_and_distance(XG,'s',cutoff=8)
        assert_false('v' in D)

    def test_single_source_dijkstra_path_length(self):
        pl = nx.single_source_dijkstra_path_length
        assert_equal(pl(self.MXG4,0)[2], 4)
        spl = pl(self.MXG4,0,cutoff=2)
        assert_false(2 in spl)

    def test_bidirectional_dijkstra_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge('a', 'b', weight=10)
        G.add_edge('a', 'b', weight=100)
        dp= nx.bidirectional_dijkstra(G, 'a', 'b')
        assert_equal(dp,(10, ['a', 'b']))


    def test_dijkstra_pred_distance_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge('a', 'b', key='short',foo=5, weight=100)
        G.add_edge('a', 'b', key='long',bar=1, weight=110)
        p,d= nx.dijkstra_predecessor_and_distance(G, 'a')
        assert_equal(p,{'a': [], 'b': ['a']})
        assert_equal(d,{'a': 0, 'b': 100})

    def test_negative_edge_cycle(self):
        G = nx.cycle_graph(5, create_using = nx.DiGraph())
        assert_equal(nx.negative_edge_cycle(G), False)
        G.add_edge(8, 9, weight = -7)
        G.add_edge(9, 8, weight = 3)
        assert_equal(nx.negative_edge_cycle(G), True)
        assert_raises(ValueError,nx.single_source_dijkstra_path_length,G,8)
        assert_raises(ValueError,nx.single_source_dijkstra,G,8)
        assert_raises(ValueError,nx.dijkstra_predecessor_and_distance,G,8)
        G.add_edge(9,10)
        assert_raises(ValueError,nx.bidirectional_dijkstra,G,8,10)

    def test_bellman_ford(self):
        # single node graph
        G = nx.DiGraph()
        G.add_node(0)
        assert_equal(nx.bellman_ford(G, 0), ({0: None}, {0: 0}))
        assert_raises(KeyError, nx.bellman_ford, G, 1)

        # negative weight cycle
        G = nx.cycle_graph(5, create_using = nx.DiGraph())
        G.add_edge(1, 2, weight = -7)
        for i in range(5):
            assert_raises(nx.NetworkXUnbounded, nx.bellman_ford, G, i)
        G = nx.cycle_graph(5)  # undirected Graph
        G.add_edge(1, 2, weight = -3)
        for i in range(5):
            assert_raises(nx.NetworkXUnbounded, nx.bellman_ford, G, i)
        # no negative cycle but negative weight
        G = nx.cycle_graph(5, create_using = nx.DiGraph())
        G.add_edge(1, 2, weight = -3)
        assert_equal(nx.bellman_ford(G, 0),
                     ({0: None, 1: 0, 2: 1, 3: 2, 4: 3},
                      {0: 0, 1: 1, 2: -2, 3: -1, 4: 0}))

        # not connected
        G = nx.complete_graph(6)
        G.add_edge(10, 11)
        G.add_edge(10, 12)
        assert_equal(nx.bellman_ford(G, 0),
                     ({0: None, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                      {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}))

        # not connected, with a component not containing the source that
        # contains a negative cost cycle.
        G = nx.complete_graph(6)
        G.add_edges_from([('A', 'B', {'load': 3}),
                          ('B', 'C', {'load': -10}),
                          ('C', 'A', {'load': 2})])
        assert_equal(nx.bellman_ford(G, 0, weight = 'load'),
                     ({0: None, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                      {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}))

        # multigraph
        P, D = nx.bellman_ford(self.MXG,'s')
        assert_equal(P['v'], 'u')
        assert_equal(D['v'], 9)
        P, D = nx.bellman_ford(self.MXG4, 0)
        assert_equal(P[2], 1)
        assert_equal(D[2], 4)

        # other tests
        (P,D)= nx.bellman_ford(self.XG,'s')
        assert_equal(P['v'], 'u')
        assert_equal(D['v'], 9)

        G=nx.path_graph(4)
        assert_equal(nx.bellman_ford(G,0),
                     ({0: None, 1: 0, 2: 1, 3: 2}, {0: 0, 1: 1, 2: 2, 3: 3}))
        assert_equal(nx.bellman_ford(G, 3),
                    ({0: 1, 1: 2, 2: 3, 3: None}, {0: 3, 1: 2, 2: 1, 3: 0}))

        G=nx.grid_2d_graph(2,2)
        pred,dist=nx.bellman_ford(G,(0,0))
        assert_equal(sorted(pred.items()),
                     [((0, 0), None), ((0, 1), (0, 0)),
                      ((1, 0), (0, 0)), ((1, 1), (0, 1))])
        assert_equal(sorted(dist.items()),
                     [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 2)])

