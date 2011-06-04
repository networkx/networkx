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
    def edgelists_equal(self,e1,e2):
        return sorted(sorted(e) for e in e1)==sorted(sorted(e) for e in e2)
    
        

    def test_simple_graphs(self):
        for dest, source in [(to_dict_of_dicts, from_dict_of_dicts),
                             (to_dict_of_lists, from_dict_of_lists)]:
            G=barbell_graph(10,3)
            dod=dest(G)

            # Dict of [dicts, lists]
            GG=source(dod)
            assert_equal(sorted(G.nodes()), sorted(GG.nodes()))
            assert_equal(sorted(G.edges()), sorted(GG.edges()))
            GW=to_networkx_graph(dod)
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
            GW=to_networkx_graph(dod)
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
            GW=to_networkx_graph(dod, create_using=DiGraph())
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
        GW=to_networkx_graph(dod,create_using=Graph())
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
        GW=to_networkx_graph(dol,create_using=Graph())
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
        GW=to_networkx_graph(dod,create_using=Graph())
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
        GW=to_networkx_graph(dol,create_using=Graph())
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
        GW=to_networkx_graph(dod,create_using=MultiGraph(),multigraph_input=True)
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
        GW=to_networkx_graph(dol,create_using=MultiGraph())
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

    def test_directed_to_undirected(self):
        edges1 = [(0, 1), (1, 2), (2, 0)]
        edges2 = [(0, 1), (1, 2), (0, 2)]
        assert_true(self.edgelists_equal(nx.Graph(nx.DiGraph(edges1)).edges(),edges1))
        assert_true(self.edgelists_equal(nx.Graph(nx.DiGraph(edges2)).edges(),edges1))
        assert_true(self.edgelists_equal(nx.MultiGraph(nx.DiGraph(edges1)).edges(),edges1))
        assert_true(self.edgelists_equal(nx.MultiGraph(nx.DiGraph(edges2)).edges(),edges1))

        assert_true(self.edgelists_equal(nx.MultiGraph(nx.MultiDiGraph(edges1)).edges(),
                                         edges1))
        assert_true(self.edgelists_equal(nx.MultiGraph(nx.MultiDiGraph(edges2)).edges(),
                                         edges1))

        assert_true(self.edgelists_equal(nx.Graph(nx.MultiDiGraph(edges1)).edges(),edges1))
        assert_true(self.edgelists_equal(nx.Graph(nx.MultiDiGraph(edges2)).edges(),edges1))
