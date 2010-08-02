#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestTriangles:

    def test_empty(self):
        G = nx.Graph()
        assert_equal(list(nx.triangles(G).values()),[])

    def test_path(self):
        G = nx.path_graph(10)
        assert_equal(list(nx.triangles(G).values()),
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        assert_equal(nx.triangles(G),
                     {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 
                      5: 0, 6: 0, 7: 0, 8: 0, 9: 0})
    def test_cubical(self):
        G = nx.cubical_graph()
        assert_equal(list(nx.triangles(G).values()),
                     [0, 0, 0, 0, 0, 0, 0, 0])
        assert_equal(nx.triangles(G,1),0)
        assert_equal(list(nx.triangles(G,[1,2]).values()),[0, 0])
        assert_equal(nx.triangles(G,1),0)
        assert_equal(nx.triangles(G,[1,2]),{1: 0, 2: 0})

    def test_k5(self):
        G = nx.complete_graph(5)
        assert_equal(list(nx.triangles(G).values()),[6, 6, 6, 6, 6])
        assert_equal(sum(nx.triangles(G).values())/3.0,10)
        assert_equal(nx.triangles(G,1),6)
        G.remove_edge(1,2)
        assert_equal(list(nx.triangles(G).values()),[5, 3, 3, 5, 5])
        assert_equal(nx.triangles(G,1),3)


class TestClustering:

    def test_clustering(self):
        G = nx.Graph()
        assert_equal(list(nx.clustering(G).values()),[])
        assert_equal(nx.clustering(G),{})

    def test_path(self):
        G = nx.path_graph(10)
        assert_equal(list(nx.clustering(G).values()),
                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        assert_equal(nx.clustering(G),
                     {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 
                      5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0})

    def test_cubical(self):
        G = nx.cubical_graph()
        assert_equal(list(nx.clustering(G).values()),
                     [0, 0, 0, 0, 0, 0, 0, 0])
        assert_equal(nx.clustering(G,1),0)
        assert_equal(list(nx.clustering(G,[1,2]).values()),[0, 0])
        assert_equal(nx.clustering(G,1),0)
        assert_equal(nx.clustering(G,[1,2]),{1: 0, 2: 0})

    def test_k5(self):
        G = nx.complete_graph(5)
        assert_equal(list(nx.clustering(G).values()),[1, 1, 1, 1, 1])
        assert_equal(nx.average_clustering(G),1)
        G.remove_edge(1,2)
        assert_equal(list(nx.clustering(G).values()),
                     [5./6., 1.0, 1.0, 5./6., 5./6.])
        assert_equal(nx.clustering(G,[1,4]),{1: 1.0, 4: 0.83333333333333337})


class TestTransitivity:

    def test_transitivity(self):
        G = nx.Graph()
        assert_equal(nx.transitivity(G),0.0)

    def test_path(self):
        G = nx.path_graph(10)
        assert_equal(nx.transitivity(G),0.0)

    def test_cubical(self):
        G = nx.cubical_graph()
        assert_equal(nx.transitivity(G),0.0)

    def test_k5(self):
        G = nx.complete_graph(5)
        assert_equal(nx.transitivity(G),1.0)
        G.remove_edge(1,2)
        assert_equal(nx.transitivity(G),0.875)

    def test_clustering_transitivity(self):
        # check that weighted average of clustering is transitivity
        G = nx.complete_graph(5)
        G.remove_edge(1,2)
        t1=nx.transitivity(G)
        (cluster_d2,weights)=nx.clustering(G,weights=True)
        trans=[]
        for v in G.nodes():
            trans.append(cluster_d2[v]*weights[v])
        t2=sum(trans)
        assert_almost_equal(abs(t1-t2),0)
