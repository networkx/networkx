#!/usr/bin/env python
from nose.tools import *
from networkx import *
from networkx.convert import *
from networkx.algorithms.operators import *
from networkx.generators.classic import barbell_graph,cycle_graph
from networkx.testing import *

class TestRelabel():
    def test_convert_node_labels_to_integers(self):
        # test that empty graph converts fine for all options
        G=empty_graph()
        H=convert_node_labels_to_integers(G,100)
        assert_equal(H.name, '(empty_graph(0))_with_int_labels')
        assert_equal(H.nodes(), [])
        assert_equal(H.edges(), [])

        for opt in ["default", "sorted", "increasing degree",
                    "decreasing degree"]:
            G=empty_graph()
            H=convert_node_labels_to_integers(G,100, ordering=opt)
            assert_equal(H.name, '(empty_graph(0))_with_int_labels')
            assert_equal(H.nodes(), [])
            assert_equal(H.edges(), [])

        G=empty_graph()
        G.add_edges_from([('A','B'),('A','C'),('B','C'),('C','D')])
        G.name="paw"
        H=convert_node_labels_to_integers(G)
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))

        H=convert_node_labels_to_integers(G,1000)
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))
        assert_equal(H.nodes(), [1000, 1001, 1002, 1003])

        H=convert_node_labels_to_integers(G,ordering="increasing degree")
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))
        assert_equal(degree(H,0), 1)
        assert_equal(degree(H,1), 2)
        assert_equal(degree(H,2), 2)
        assert_equal(degree(H,3), 3)

        H=convert_node_labels_to_integers(G,ordering="decreasing degree")
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))
        assert_equal(degree(H,0), 3)
        assert_equal(degree(H,1), 2)
        assert_equal(degree(H,2), 2)
        assert_equal(degree(H,3), 1)

        H=convert_node_labels_to_integers(G,ordering="increasing degree",
                                          label_attribute='label')
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))
        assert_equal(degree(H,0), 1)
        assert_equal(degree(H,1), 2)
        assert_equal(degree(H,2), 2)
        assert_equal(degree(H,3), 3)

        # check mapping
        assert_equal(H.node[3]['label'],'C')
        assert_equal(H.node[0]['label'],'D')
        assert_true(H.node[1]['label']=='A' or H.node[2]['label']=='A')
        assert_true(H.node[1]['label']=='B' or H.node[2]['label']=='B')

    def test_convert_to_integers2(self):
        G=empty_graph()
        G.add_edges_from([('C','D'),('A','B'),('A','C'),('B','C')])
        G.name="paw"
        H=convert_node_labels_to_integers(G,ordering="sorted")
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))

        H=convert_node_labels_to_integers(G,ordering="sorted",
                                          label_attribute='label')
        assert_equal(H.node[0]['label'],'A')
        assert_equal(H.node[1]['label'],'B')
        assert_equal(H.node[2]['label'],'C')
        assert_equal(H.node[3]['label'],'D')

    @raises(nx.NetworkXError)
    def test_convert_to_integers_raise(self):
        G = nx.Graph()
        H=convert_node_labels_to_integers(G,ordering="increasing age")


    def test_relabel_nodes_copy(self):
        G=empty_graph()
        G.add_edges_from([('A','B'),('A','C'),('B','C'),('C','D')])
        mapping={'A':'aardvark','B':'bear','C':'cat','D':'dog'}
        H=relabel_nodes(G,mapping)
        assert_equal(sorted(H.nodes()), ['aardvark', 'bear', 'cat', 'dog'])

    def test_relabel_nodes_function(self):
        G=empty_graph()
        G.add_edges_from([('A','B'),('A','C'),('B','C'),('C','D')])
        # function mapping no longer encouraged but works
        def mapping(n):
            return ord(n)
        H=relabel_nodes(G,mapping)
        assert_equal(sorted(H.nodes()), [65, 66, 67, 68])

    def test_relabel_nodes_graph(self):
        G=Graph([('A','B'),('A','C'),('B','C'),('C','D')])
        mapping={'A':'aardvark','B':'bear','C':'cat','D':'dog'}
        H=relabel_nodes(G,mapping)
        assert_equal(sorted(H.nodes()), ['aardvark', 'bear', 'cat', 'dog'])

    def test_relabel_nodes_digraph(self):
        G=DiGraph([('A','B'),('A','C'),('B','C'),('C','D')])
        mapping={'A':'aardvark','B':'bear','C':'cat','D':'dog'}
        H=relabel_nodes(G,mapping,copy=False)
        assert_equal(sorted(H.nodes()), ['aardvark', 'bear', 'cat', 'dog'])

    def test_relabel_nodes_multigraph(self):
        G=MultiGraph([('a','b'),('a','b')])
        mapping={'a':'aardvark','b':'bear'}
        G=relabel_nodes(G,mapping,copy=False)
        assert_equal(sorted(G.nodes()), ['aardvark', 'bear'])
        assert_edges_equal(sorted(G.edges()),
                           [('aardvark', 'bear'), ('aardvark', 'bear')])

    def test_relabel_nodes_multidigraph(self):
        G=MultiDiGraph([('a','b'),('a','b')])
        mapping={'a':'aardvark','b':'bear'}
        G=relabel_nodes(G,mapping,copy=False)
        assert_equal(sorted(G.nodes()), ['aardvark', 'bear'])
        assert_equal(sorted(G.edges()),
                     [('aardvark', 'bear'), ('aardvark', 'bear')])

    def test_relabel_isolated_nodes_to_same(self):
        G=Graph()
        G.add_nodes_from(range(4))
        mapping={1:1}
        H=relabel_nodes(G, mapping, copy=False)
        assert_equal(sorted(H.nodes()), list(range(4)))

    @raises(KeyError)
    def test_relabel_nodes_missing(self):
        G=Graph([('A','B'),('A','C'),('B','C'),('C','D')])
        mapping={0:'aardvark'}
        G=relabel_nodes(G,mapping,copy=False)


    def test_relabel_toposort(self):
        K5=nx.complete_graph(4)
        G=nx.complete_graph(4)
        G=nx.relabel_nodes(G,dict( [(i,i+1) for i in range(4)]),copy=False)
        nx.is_isomorphic(K5,G)
        G=nx.complete_graph(4)
        G=nx.relabel_nodes(G,dict( [(i,i-1) for i in range(4)]),copy=False)
        nx.is_isomorphic(K5,G)


    def test_relabel_selfloop(self):
        G = nx.DiGraph([(1, 1), (1, 2), (2, 3)])
        G = nx.relabel_nodes(G, {1: 'One', 2: 'Two', 3: 'Three'}, copy=False)
        assert_equal(sorted(G.nodes()),['One','Three','Two'])
        G = nx.MultiDiGraph([(1, 1), (1, 2), (2, 3)])
        G = nx.relabel_nodes(G, {1: 'One', 2: 'Two', 3: 'Three'}, copy=False)
        assert_equal(sorted(G.nodes()),['One','Three','Two'])
        G = nx.MultiDiGraph([(1, 1)])
        G = nx.relabel_nodes(G, {1: 0}, copy=False)
        assert_equal(G.nodes(), [0])
