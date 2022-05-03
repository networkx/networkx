import pytest

import networkx as nx
import Rainbow_matching as rm

def test_easy_cases():

    G = nx.Graph()

    #The empty graph
    Res = rm.rainbow_matching(G, 1)
    assert list(Res.edges) == []


    G.add_nodes_from([1, 3])
    G.add_edge(1, 2, color = "red")
    G.add_edge(2, 3, color="red")

    Res = rm.rainbow_matching(G, 1)
    assert list(Res.edges) == [(1,2)]
    Res = rm.rainbow_matching(G, 2)
    assert list(Res.edges) == []

def test_normal_cases():
    G = nx.Graph()

    G.add_nodes_from([1, 3])
    G.add_edge(1, 2, color="red")
    G.add_edge(2, 3, color="blue")

    assert list(rm.rainbow_matching(G, 1)) == [(1,2)]
    assert list(rm.rainbow_matching(G, 2)) == []

    G.add_node(4)
    G.add_edge(3, 4, color="red")
    assert list(rm.rainbow_matching(G, 1)) == [(1,2)]
    assert list(rm.rainbow_matching(G, 2)) == []

    G.add_nodes_from([5, 6])
    G.edges[2, 3]['color'] = "red"
    G.edges[3, 4]['color'] = "blue"
    G.add_edge(4, 5, color="blue")
    G.add_edge(5, 6, color="yellow")

    assert list(rm.rainbow_matching(G, 1)) == [(1,2)]
    assert list(rm.rainbow_matching(G, 2)) == [(1,2), (3,4)]
    assert list(rm.rainbow_matching(G, 3)) == [(1,2), (3,4), (5,6)]


    #more colors than "k"
    G.edges[1, 2]['color'] = "blue"
    G.edges[2, 3]['color'] = "yellow"
    G.edges[3, 4]['color'] = "blue"
    G.edges[4, 5]['color'] = "red"
    G.edges[5, 6]['color'] = "black"

    assert list(rm.rainbow_matching(G, 1)) == [(1,2)]
    assert list(rm.rainbow_matching(G, 2)) == [(1,2), (4,5)]
    assert list(rm.rainbow_matching(G, 3)) == []

    G.edges[1, 2]['color'] = "red"
    G.edges[2, 3]['color'] = "blue"
    G.edges[3, 4]['color'] = "yellow"
    G.edges[4, 5]['color'] = "green"
    G.edges[5, 6]['color'] = "white"

    assert list(rm.rainbow_matching(G, 3)) == [(1,2), (3,4), (5,6)]
    assert list(rm.rainbow_matching(G, 5)) == []

    G.add_nodes_from([7, 14])
    G.edges[1, 2]['color'] = "red"
    G.edges[2, 3]['color'] = "blue"
    G.edges[3, 4]['color'] = "red"
    G.edges[4, 5]['color'] = "yellow"
    G.edges[5, 6]['color'] = "green"
    G.add_edge(6, 7, color="yellow")
    G.add_edge(7, 8, color="black")
    G.add_edge(8, 9, color="red")
    G.add_edge(9, 10, color="green")
    G.add_edge(10, 11, color="white")
    G.add_edge(11, 12, color="white")
    G.add_edge(12, 13, color="yellow")
    G.add_edge(13, 14, color="black")

    assert list(rm.rainbow_matching(G, 4)) == [(1,2), (4,5), (7,8), (9,10)]
    assert list(rm.rainbow_matching(G, 5)) == [(1,2), (4,5), (7,8), (9,10), (11,12)]
    assert list(rm.rainbow_matching(G, 6)) == []
