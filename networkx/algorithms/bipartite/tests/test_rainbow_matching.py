import pytest

import networkx as nx
import Rainbow_matching as rm

def test_easy_cases():

    G = nx.Graph()

    #The empty graph
    assert rm.rainbow_matching(G, 1) == 0


    G.add_nodes_from([1, 3])
    G.add_edge(1, 2, color = "red")
    G.add_edge(2, 3, color="red")

    assert rm.rainbow_matching(G, 1) == 1
    assert rm.rainbow_matching(G, 2) == 0

def test_normal_cases():
    G = nx.Graph()

    G.add_nodes_from([1, 3])
    G.add_edge(1, 2, color="red")
    G.add_edge(2, 3, color="blue")

    assert rm.rainbow_matching(G, 1) == 1
    assert rm.rainbow_matching(G, 2) == 0

    G.add_node(4)
    G.add_edge(3, 4, color="red")
    assert rm.rainbow_matching(G, 1) == 1
    assert rm.rainbow_matching(G, 2) == 0

    G.add_nodes_from([5, 6])
    G.edges[2, 3]['color'] = "red"
    G.edges[3, 4]['color'] = "blue"
    G.add_edge(4, 5, color="blue")
    G.add_edge(5, 6, color="yellow")

    assert rm.rainbow_matching(G, 1) == 1
    assert rm.rainbow_matching(G, 2) == 1
    assert rm.rainbow_matching(G, 3) == 1


    #more colors than "k"
    G.edges[1, 2]['color'] = "blue"
    G.edges[2, 3]['color'] = "yellow"
    G.edges[3, 4]['color'] = "blue"
    G.edges[4, 5]['color'] = "red"
    G.edges[5, 6]['color'] = "black"

    assert rm.rainbow_matching(G, 1) == 1
    assert rm.rainbow_matching(G, 2) == 1
    assert rm.rainbow_matching(G, 3) == 0

    G.edges[1, 2]['color'] = "red"
    G.edges[2, 3]['color'] = "blue"
    G.edges[3, 4]['color'] = "yellow"
    G.edges[4, 5]['color'] = "green"
    G.edges[5, 6]['color'] = "white"

    assert rm.rainbow_matching(G, 3) == 1
    assert rm.rainbow_matching(G, 5) == 0

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

    assert rm.rainbow_matching(G, 4) == 1
    assert rm.rainbow_matching(G, 5) == 1
    assert rm.rainbow_matching(G, 6) == 0