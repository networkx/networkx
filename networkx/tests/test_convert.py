#!/usr/bin/env python

"""Convert
=======
"""

from nose.tools import *
from networkx import *
from networkx.convert import *
from networkx.algorithms.operators import *
from networkx.generators.classic import barbell_graph,cycle_graph

class TestConvert():
    def test_simple_graphs(self):
        for dest, source in [(to_dict_of_dicts, from_dict_of_dicts),
                             (to_dict_of_lists, from_dict_of_lists)]:
            G=barbell_graph(10,3)
            dod=dest(G)

            # Dict of [dicts, lists]
            GG=source(dod)
            assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
            assert_equal(sorted(G.edges()), sorted(GG.edges()))
            GW=from_whatever(dod)
            assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
            assert_equal(sorted(G.edges()), sorted(GW.edges()))
            GI=Graph(dod)
            assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
            assert_equal(sorted(G.edges()), sorted(GI.edges()))

            # With nodelist keyword
            P4=path_graph(4)
            P3=path_graph(3)
            dod=dest(P4,nodelist=[0,1,2])
            Gdod=Graph(dod)
            assert_equal(sorted(Gdod.nodes()), sorted(P3.nodes()))
            assert_equal(sorted(Gdod.edges()), sorted(P3.edges()))

    def test_digraphs(self):
        for dest, source in [(to_dict_of_dicts, from_dict_of_dicts),
                             (to_dict_of_lists, from_dict_of_lists)]:
            G=cycle_graph(10)

            # Dict of [dicts, lists]
            dod=dest(G)
            GG=source(dod)
            assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
            assert_equal(sorted(G.edges()), sorted(GG.edges()))
            GW=from_whatever(dod)
            assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
            assert_equal(sorted(G.edges()), sorted(GW.edges()))
            GI=Graph(dod)
            assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
            assert_equal(sorted(G.edges()), sorted(GI.edges()))

            G=cycle_graph(10,create_using=DiGraph())
            dod=dest(G)
            GG=source(dod, create_using=DiGraph())
            assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
            assert_equal(sorted(G.edges()), sorted(GG.edges()))
            GW=from_whatever(dod, create_using=DiGraph())
            assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
            assert_equal(sorted(G.edges()), sorted(GW.edges()))
            GI=DiGraph(dod)
            assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
            assert_equal(sorted(G.edges()), sorted(GI.edges()))

    def test_graph(self):
        G=cycle_graph(10)
        e=G.edges()
        source=[u for u,v in e]
        dest=[v for u,v in e]
        ex=zip(source,dest,source)
        G=Graph()
        G.add_weighted_edges_from(ex)
        
        # Dict of dicts
        dod=to_dict_of_dicts(G)
        GG=from_dict_of_dicts(dod,create_using=Graph())
        assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
        assert_equal(sorted(G.edges()), sorted(GG.edges()))
        GW=from_whatever(dod,create_using=Graph())
        assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
        assert_equal(sorted(G.edges()), sorted(GW.edges()))
        GI=Graph(dod)
        assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
        assert_equal(sorted(G.edges()), sorted(GI.edges()))

        # Dict of lists
        dol=to_dict_of_lists(G)
        GG=from_dict_of_lists(dol,create_using=Graph())
        # dict of lists throws away edge data so set it to none
        enone=[(u,v,{}) for (u,v,d) in G.edges(data=True)]
        assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
        assert_equal(enone, sorted(GG.edges(data=True)))
        GW=from_whatever(dol,create_using=Graph())
        assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
        assert_equal(enone, sorted(GW.edges(data=True)))
        GI=Graph(dol)
        assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
        assert_equal(enone, sorted(GI.edges(data=True)))


    def test_with_multiedges_self_loops(self):
        G=cycle_graph(10)
        e=G.edges()
        source,dest = list(zip(*e))
        ex=list(zip(source,dest,source))
        XG=Graph()
        XG.add_weighted_edges_from(ex)
        XGM=MultiGraph()
        XGM.add_weighted_edges_from(ex)
        XGM.add_edge(0,1,weight=2) # multiedge
        XGS=Graph()
        XGS.add_weighted_edges_from(ex)
        XGS.add_edge(0,0,weight=100) # self loop

        # Dict of dicts
        # with self loops, OK
        dod=to_dict_of_dicts(XGS)
        GG=from_dict_of_dicts(dod,create_using=Graph())
        assert_equal(sorted(XGS.nodes()), sorted(GG.nodes()))
        assert_equal(sorted(XGS.edges()), sorted(GG.edges()))
        GW=from_whatever(dod,create_using=Graph())
        assert_equal(sorted(XGS.nodes()), sorted(GW.nodes()))
        assert_equal(sorted(XGS.edges()), sorted(GW.edges()))
        GI=Graph(dod)
        assert_equal(sorted(XGS.nodes()), sorted(GI.nodes()))
        assert_equal(sorted(XGS.edges()), sorted(GI.edges()))

        # Dict of lists
        # with self loops, OK
        dol=to_dict_of_lists(XGS)
        GG=from_dict_of_lists(dol,create_using=Graph())
        # dict of lists throws away edge data so set it to none
        enone=[(u,v,{}) for (u,v,d) in XGS.edges(data=True)]
        assert_equal(sorted(XGS.nodes()), sorted(GG.nodes()))
        assert_equal(enone, sorted(GG.edges(data=True)))
        GW=from_whatever(dol,create_using=Graph())
        assert_equal(sorted(XGS.nodes()), sorted(GW.nodes()))
        assert_equal(enone, sorted(GW.edges(data=True)))
        GI=Graph(dol)
        assert_equal(sorted(XGS.nodes()), sorted(GI.nodes()))
        assert_equal(enone, sorted(GI.edges(data=True)))

        # Dict of dicts
        # with multiedges, OK
        dod=to_dict_of_dicts(XGM)
        GG=from_dict_of_dicts(dod,create_using=MultiGraph(),
                              multigraph_input=True)
        assert_equal(sorted(XGM.nodes()), sorted(GG.nodes()))
        assert_equal(sorted(XGM.edges()), sorted(GG.edges()))
        GW=from_whatever(dod,create_using=MultiGraph(),multigraph_input=True)
        assert_equal(sorted(XGM.nodes()), sorted(GW.nodes()))
        assert_equal(sorted(XGM.edges()), sorted(GW.edges()))
        GI=MultiGraph(dod)  # convert can't tell whether to duplicate edges!
        assert_equal(sorted(XGM.nodes()), sorted(GI.nodes()))
        #assert_not_equal(sorted(XGM.edges()), sorted(GI.edges()))
        assert_false(sorted(XGM.edges()) == sorted(GI.edges()))
        GE=from_dict_of_dicts(dod,create_using=MultiGraph(),
                              multigraph_input=False)  
        assert_equal(sorted(XGM.nodes()), sorted(GE.nodes()))
        assert_not_equal(sorted(XGM.edges()), sorted(GE.edges()))
        GI=MultiGraph(XGM)
        assert_equal(sorted(XGM.nodes()), sorted(GI.nodes()))
        assert_equal(sorted(XGM.edges()), sorted(GI.edges()))
        GM=MultiGraph(G)
        assert_equal(sorted(GM.nodes()), sorted(G.nodes()))
        assert_equal(sorted(GM.edges()), sorted(G.edges()))

        # Dict of lists
        # with multiedges, OK, but better write as DiGraph else you'll
        # get double edges
        dol=to_dict_of_lists(G)
        GG=from_dict_of_lists(dol,create_using=MultiGraph())
        assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
        assert_equal(sorted(G.edges()), sorted(GG.edges()))
        GW=from_whatever(dol,create_using=MultiGraph())
        assert_equal(sorted(G.nodes()), sorted(GW.nodes()))
        assert_equal(sorted(G.edges()), sorted(GW.edges()))
        GI=MultiGraph(dol)
        assert_equal(sorted(G.nodes()), sorted(GI.nodes()))
        assert_equal(sorted(G.edges()), sorted(GI.edges()))

    def test_edgelists(self):
        P=path_graph(4)
        e=[(0,1),(1,2),(2,3)]
        G=Graph(e)
        assert_equal(sorted(G.nodes()), sorted(P.nodes()))
        assert_equal(sorted(G.edges()), sorted(P.edges()))
        assert_equal(sorted(G.edges(data=True)), sorted(P.edges(data=True)))

        e=[(0,1,{}),(1,2,{}),(2,3,{})]
        G=Graph(e)
        assert_equal(sorted(G.nodes()), sorted(P.nodes()))
        assert_equal(sorted(G.edges()), sorted(P.edges()))
        assert_equal(sorted(G.edges(data=True)), sorted(P.edges(data=True)))

        e=((n,n+1) for n in range(3))
        G=Graph(e)
        assert_equal(sorted(G.nodes()), sorted(P.nodes()))
        assert_equal(sorted(G.edges()), sorted(P.edges()))
        assert_equal(sorted(G.edges(data=True)), sorted(P.edges(data=True)))

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
                                          discard_old_labels=False)
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))
        assert_equal(degree(H,0), 1)
        assert_equal(degree(H,1), 2)
        assert_equal(degree(H,2), 2)
        assert_equal(degree(H,3), 3)
        mapping=H.node_labels
        assert_equal(mapping['C'], 3)
        assert_equal(mapping['D'], 0)
        assert_true(mapping['A']==1 or mapping['A']==2)
        assert_true(mapping['B']==1 or mapping['B']==2)

        G=empty_graph()
        G.add_edges_from([('C','D'),('A','B'),('A','C'),('B','C')])
        G.name="paw"
        H=convert_node_labels_to_integers(G,ordering="sorted")
        degH=H.degree().values()
        degG=G.degree().values()
        assert_equal(sorted(degH), sorted(degG))

        H=convert_node_labels_to_integers(G,ordering="sorted",
                                          discard_old_labels=False)
        mapping=H.node_labels
        assert_equal(mapping['A'], 0)
        assert_equal(mapping['B'], 1)
        assert_equal(mapping['C'], 2)
        assert_equal(mapping['D'], 3)

        assert_raises(networkx.exception.NetworkXError,
                      convert_node_labels_to_integers, G, 
                      ordering="increasing age")

    def test_relabel(self):
        G=empty_graph()
        G.add_edges_from([('A','B'),('A','C'),('B','C'),('C','D')])
        mapping={'A':'aardvark','B':'bear','C':'cat','D':'dog'}
        H=relabel_nodes(G,mapping)
        assert_equal(sorted(H.nodes()), ['aardvark', 'bear', 'cat', 'dog'])
        
        def mapping(n):
            return ord(n)

        H=relabel_nodes(G,mapping)
        assert_equal(sorted(H.nodes()), [65, 66, 67, 68])

"""convert_data_structure
G1.has_edge('B', 'A')
False
UG=Graph(G1)
sorted(UG.edges())
[('A', 'B'), ('A', 'C'), ('A', 'D')]
UG.has_edge('B', 'A')
True
DG=DiGraph(UG)
DG.adj==UG.adj
True
DG.remove_edge('A','B')
number_of_edges(DG)
5
UG.remove_edge('A','B')
number_of_edges(UG)
2
"""

