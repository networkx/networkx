"""
Programmers: Roi Meshulam and Liroy Melamed

This file is implemation of "Maximum Prioirity Matching" from the article that
written by Jonathan Turner.

Let G=(V,E) be an undirected graph with n vertices and m edges, in which each vertex u is
assigned an integer priority in [1,n], with 1 being the ``highest'' priority. Let M be a matching of G.
We define the priority score of M to be an n-ary integer in which the i-th most-significant digit is
the number of vertices with priority i that are incident to an edge in M. We describe a variation of
the augmenting path method (Edmonds' algorithm) that finds a matching with maximum priority
score in O(mn) time. 

link to the article: "https://openscholarship.wustl.edu/cgi/viewcontent.cgi?article=1509&context=cse_research#:~:text=A%20maximum%20priority%20matching%20is%20a%20matching%20that%20has%20a,in%20internet%20routers%20%5B7%5D."

more details about this algo can be found in the following link: "http://myusername.pythonanywhere.com/"

"""

import random
import random as rd

import networkx as nx

# from networkx import convert_node_labels_to_integers as cnlti
from .. import maximum_priority_matching


class Test_maximum_priority_matching:
    def test_find_prioirity_score(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = []
        nodes_attrs = {
            "1": {"priority": 1},
            "2": {"priority": 8},
            "3": {"priority": 6},
            "4": {"priority": 5},
            "5": {"priority": 2},
            "6": {"priority": 4},
            "7": {"priority": 3},
            "8": {"priority": 1},
            "9": {"priority": 7},
        }
        matching = []
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert maximum_priority_matching.find_priority_score(G, matching) == "000000000"

        # Test with a graph that has all matching edges
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {"priority": 1},
            "2": {"priority": 8},
            "3": {"priority": 6},
            "4": {"priority": 5},
            "5": {"priority": 2},
            "6": {"priority": 4},
            "7": {"priority": 3},
            "8": {"priority": 1},
            "9": {"priority": 7},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        matching = [('1', '2'), ('3', '4'), ('5', '6'), ('7', '8')]
        assert maximum_priority_matching.find_priority_score(G, matching) == "211111010"

    def test_find_maximum_prioirity_matching(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {"priority": 1},
            "2": {"priority": 8},
            "3": {"priority": 6},
            "4": {"priority": 5},
            "5": {"priority": 2},
            "6": {"priority": 4},
            "7": {"priority": 3},
            "8": {"priority": 1},
            "9": {"priority": 7},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert maximum_priority_matching.find_maximum_priority_matching(G) == [
            ("1", "2"),
            ("3", "4"),
            ("5", "6"),
            ("7", "8"),
        ]

        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {"priority": 1},
            "2": {"priority": 2},
            "3": {"priority": 1},
            "4": {"priority": 1},
            "5": {"priority": 1},
            "6": {"priority": 1},
            "7": {"priority": 1},
            "8": {"priority": 1},
            "9": {"priority": 2},
            "10": {"priority": 1},
            "11": {"priority": 1},
            "12": {"priority": 1},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        maximum_priority_matching.find_maximum_priority_matching(G) == [
            ("1", "2"),
            ("3", "6"),
            ("4", "5"),
            ("7", "11"),
            ("8", "9"),
            ("10", "12"),
        ]

        G = nx.Graph()
        for i in range(50):
            G.add_node(str(i))

        for node in G.nodes:
            G.nodes[node]["priority"] = random.randint(1, 50)
        G.add_node("test")
        G.nodes["test"]["priority"] = 1
        edges = nx.erdos_renyi_graph(50, 0.005).edges()
        for u, v in edges:
            G.add_edge(str(u), str(v))

        G.add_edge("test", "1")
        matching = maximum_priority_matching.find_maximum_priority_matching(G)
        check = False
        for element in matching:
            if "test" in element:
                check = True
        assert check == True

    def test_find_augmenting_paths(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": None,
                "priority": 8,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": None,
                "priority": 6,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": None,
                "priority": 5,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": None,
                "priority": 4,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": None,
                "priority": 3,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 7,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "6"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "3"): {"isMatched": False},
            ("7", "8"): {"isMatched": False},
            ("7", "9"): {"isMatched": False},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)

        assert maximum_priority_matching.prepare_for_algo(G, 1) == (
            [("1", "2"), ("8", "7")],
            ["1", "8"],
        )
        assert maximum_priority_matching.find_augmenting_paths(G, 1) == True
        assert maximum_priority_matching.prepare_for_algo(G, 1) == ([("8", "7")], ["8"])
        assert maximum_priority_matching.find_augmenting_paths(G, 1) == True
        assert maximum_priority_matching.prepare_for_algo(G, 1) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 1) == False
        assert maximum_priority_matching.prepare_for_algo(G, 2) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 2) == False
        assert maximum_priority_matching.prepare_for_algo(G, 3) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 3) == False
        assert maximum_priority_matching.prepare_for_algo(G, 4) == (
            [("6", "5"), ("6", "7")],
            ["6"],
        )
        assert maximum_priority_matching.find_augmenting_paths(G, 4) == True
        assert maximum_priority_matching.prepare_for_algo(G, 4) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 4) == False
        assert maximum_priority_matching.prepare_for_algo(G, 5) == (
            [("4", "3"), ("4", "5")],
            ["4"],
        )
        assert maximum_priority_matching.find_augmenting_paths(G, 5) == True
        assert maximum_priority_matching.prepare_for_algo(G, 5) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 5) == False
        assert maximum_priority_matching.prepare_for_algo(G, 6) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 6) == False
        assert maximum_priority_matching.prepare_for_algo(G, 7) == ([("9", "7")], ["9"])
        assert maximum_priority_matching.find_augmenting_paths(G, 7) == False
        assert maximum_priority_matching.prepare_for_algo(G, 8) == ([], [])
        assert maximum_priority_matching.find_augmenting_paths(G, 8) == False

    def test_shrink_graph(self):

        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": "4",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "11": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "12": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.shrink_graph(
            G, {"nodes": ["5", "4", "3", "6", "7"]}, "B0"
        ) == [
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
        ]
        assert maximum_priority_matching.shrink_graph(
            G, {"nodes": ["11", "10", "12"]}, "B1"
        ) == [
            (False, "B1"),
            (False, "B1"),
            (False, "B1"),
        ]

    def test_prepare_for_algo(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": None,
                "priority": 8,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": None,
                "priority": 6,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": None,
                "priority": 5,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": None,
                "priority": 4,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": None,
                "priority": 3,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 7,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "6"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "3"): {"isMatched": False},
            ("7", "8"): {"isMatched": False},
            ("7", "9"): {"isMatched": False},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.prepare_for_algo(G, 1) == (
            [("1", "2"), ("8", "7")],
            ["1", "8"],
        )
        assert maximum_priority_matching.prepare_for_algo(G, 2) == ([], [])
        assert maximum_priority_matching.prepare_for_algo(G, 3) == ([], [])
        assert maximum_priority_matching.prepare_for_algo(G, 4) == ([], [])
        assert maximum_priority_matching.prepare_for_algo(G, 5) == ([], [])
        assert maximum_priority_matching.prepare_for_algo(G, 6) == ([], [])
        assert maximum_priority_matching.prepare_for_algo(G, 7) == ([("9", "7")], ["9"])
        assert maximum_priority_matching.prepare_for_algo(G, 8) == ([], [])

        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 5,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": None,
                "priority": 8,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": None,
                "priority": 3,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": None,
                "priority": 7,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": None,
                "priority": 4,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 6,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 9,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "6"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "3"): {"isMatched": False},
            ("7", "8"): {"isMatched": False},
            ("7", "9"): {"isMatched": False},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.prepare_for_algo(G, 1) == ([], [])

    def test_find_path(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": False,
                "blossomsID": "B0",
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": False,
                "blossomsID": "B0",
            },
            "5": {
                "parent": "4",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": False,
                "blossomsID": "B0",
            },
            "6": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": False,
                "blossomsID": "B0",
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": False,
                "blossomsID": "B0",
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "11": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "12": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.find_path(
            G,
            {
                "B0": {
                    "nodes": ["5", "4", "3", "6", "7"],
                    "root": "1",
                    "isPositive": True,
                    "Base": "3",
                }
            },
            "7",
            "11",
            True,
        ) == ["1", "2", "3", "6", "7", "11"]

    def test_find_path_first_cond(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 8,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 6,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": None,
                "priority": 5,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": None,
                "priority": 4,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": None,
                "priority": 3,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 7,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "6"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "3"): {"isMatched": False},
            ("7", "8"): {"isMatched": False},
            ("7", "9"): {"isMatched": False},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.find_path_first_cond(G, "3") == ["1", "2", "3"]
        # create a graph with a simple tree structure
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5"]
        edges = [("1", "2"), ("1", "3"), ("2", "4"), ("3", "5")]
        nodes_attrs = {
            "1": {"parent": None, "root": "1"},
            "2": {"parent": "1", "root": "1"},
            "3": {"parent": "1", "root": "1"},
            "4": {"parent": "2", "root": "1"},
            "5": {"parent": "3", "root": "1"},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)

        # test the function with various node ids
        assert maximum_priority_matching.find_path_first_cond(G, "1") == ["1"]
        assert maximum_priority_matching.find_path_first_cond(G, "2") == ["1", "2"]
        assert maximum_priority_matching.find_path_first_cond(G, "3") == ["1", "3"]
        assert maximum_priority_matching.find_path_first_cond(G, "4") == ["1", "2", "4"]
        assert maximum_priority_matching.find_path_first_cond(G, "5") == ["1", "3", "5"]

    def test_find_blossom(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": "4",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": "8",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": "9",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "11": {
                "parent": "10",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "12": {
                "parent": "11",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        blossoms = {}
        maximum_priority_matching.find_blossom(G, blossoms, "5", "7")
        (
            {
                "nodes": ["5", "4", "3", "6", "7"],
                "root": "1",
                "isPositive": True,
                "Base": "3",
            },
            "B0",
        )
        assert len(blossoms) == 1
        external_info = nx.get_node_attributes(G, "isExternal")
        blossoms_id = nx.get_node_attributes(G, "blossomsID")
        assert external_info["5"] == True
        assert external_info["4"] == True
        assert external_info["3"] == True
        assert external_info["6"] == True
        assert external_info["7"] == True
        assert blossoms_id["4"] == -1
        assert blossoms_id["5"] == -1
        assert blossoms_id["3"] == -1
        assert blossoms_id["6"] == -1
        assert blossoms_id["7"] == -1
        assert external_info["10"] == True
        assert external_info["11"] == True
        assert external_info["12"] == True
        assert blossoms_id["10"] == -1
        assert blossoms_id["11"] == -1
        assert blossoms_id["12"] == -1

        maximum_priority_matching.shrink_graph(G, blossoms["B0"], "B0") == [
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
            (False, "B0"),
        ]
        external_info = nx.get_node_attributes(G, "isExternal")
        blossoms_id = nx.get_node_attributes(G, "blossomsID")
        assert external_info["5"] == False
        assert external_info["4"] == False
        assert external_info["3"] == False
        assert external_info["6"] == False
        assert external_info["7"] == False
        assert blossoms_id["4"] == "B0"
        assert blossoms_id["5"] == "B0"
        assert blossoms_id["3"] == "B0"
        assert blossoms_id["6"] == "B0"
        assert blossoms_id["7"] == "B0"

        assert maximum_priority_matching.find_blossom(G, blossoms, "10", "12") == (
            {
                "nodes": ["10", "11", "12"],
                "root": "8",
                "isPositive": True,
                "Base": "10",
            },
            "B1",
        )
        assert len(blossoms) == 2
        assert maximum_priority_matching.shrink_graph(G, blossoms["B1"], "B1") == [
            (False, "B1"),
            (False, "B1"),
            (False, "B1"),
        ]
        external_info = nx.get_node_attributes(G, "isExternal")
        blossoms_id = nx.get_node_attributes(G, "blossomsID")
        external_info["10"] == False
        external_info["11"] == False
        external_info["12"] == False
        blossoms_id["10"] == "B1"
        blossoms_id["11"] == "B1"
        blossoms_id["12"] == "B1"

    def test_find_path_in_blossom(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "4": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "5": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "6": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "7": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isBolssom": False,
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": "9",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "11": {
                "parent": "10",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "12": {
                "parent": "11",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        blossom = {"nodes": ["5", "4", "3", "6", "7"], "Base": "3"}
        assert maximum_priority_matching.find_path_in_blossom(
            G, blossom, False, "7"
        ) == (
            ["7", "6", "3"],
            "2",
        )
        blossom = {"nodes": ["11", "10", "12"], "Base": "10"}
        assert maximum_priority_matching.find_path_in_blossom(
            G, blossom, False, "11"
        ) == (
            ["11", "12", "10"],
            "9",
        )

        G1 = nx.Graph()
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "5": {
                "parent": "7",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": True,
                "blossomsID": "B0",
            },
            "6": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": "12",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "11": {
                "parent": "10",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "12": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": True},
            ("2", "3"): {"isMatched": False},
            ("3", "4"): {"isMatched": True},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": False},
            ("5", "7"): {"isMatched": True},
            ("6", "7"): {"isMatched": False},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": True},
            ("9", "10"): {"isMatched": False},
            ("10", "11"): {"isMatched": True},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": False},
        }
        G1.add_nodes_from(nodes)
        G1.add_edges_from(edges)
        nx.set_node_attributes(G1, nodes_attrs)
        nx.set_edge_attributes(G1, edges_attrs)
        blossom = {"nodes": ["5", "4", "3", "6", "7"], "Base": "6"}
        assert maximum_priority_matching.find_path_in_blossom(
            G1, blossom, False, "7"
        ) == (
            ["7", "5", "4", "3", "6"],
            None,
        )

        blossom = {"nodes": ["11", "10", "12"], "Base": "12"}
        assert maximum_priority_matching.find_path_in_blossom(
            G1, blossom, False, "11"
        ) == (
            ["11", "10", "12"],
            None,
        )

    def test_find_path_to_base(self):
        list = ["5", "4", "3", "6", "7"]
        u = "7"
        base = "3"
        assert maximum_priority_matching.paths_to_base(list, u, base) == (
            ["7", "5", "4", "3"],
            ["7", "6", "3"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["5", "4", "3", "6", "7"], "7", "3"
        ) == (
            ["7", "5", "4", "3"],
            ["7", "6", "3"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["5", "4", "3", "6", "7"], "5", "3"
        ) == (
            ["5", "4", "3"],
            ["5", "7", "6", "3"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["5", "4", "3", "6", "7"], "4", "3"
        ) == (
            ["4", "3"],
            ["4", "5", "7", "6", "3"],
        )
        assert maximum_priority_matching.paths_to_base(["1", "2", "3"], "2", "1") == (
            ["2", "3", "1"],
            ["2", "1"],
        )
        assert maximum_priority_matching.paths_to_base(["1", "2", "3"], "1", "1") == (
            ["1"],
            ["1"],
        )
        assert maximum_priority_matching.paths_to_base(["1", "2", "3"], "3", "1") == (
            ["3", "1"],
            ["3", "2", "1"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["1", "2", "3", "4"], "1", "1"
        ) == (["1"], ["1"])
        assert maximum_priority_matching.paths_to_base(
            ["1", "2", "3", "4"], "2", "1"
        ) == (
            ["2", "3", "4", "1"],
            ["2", "1"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["1", "2", "3", "4"], "3", "1"
        ) == (
            ["3", "4", "1"],
            ["3", "2", "1"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["1", "2", "3", "4"], "4", "1"
        ) == (
            ["4", "1"],
            ["4", "3", "2", "1"],
        )
        assert maximum_priority_matching.paths_to_base(
            ["1", "2", "3", "4", "5"], "5", "3"
        ) == (
            ["5", "1", "2", "3"],
            ["5", "4", "3"],
        )

    def test_find_path_to_root(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "2",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "5": {
                "parent": "4",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "6": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "1",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "1",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": "8",
                "priority": 2,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": "9",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "11": {
                "parent": "10",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "8",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "12": {
                "parent": "11",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "8",
                "isExternal": False,
                "blossomsID": "B1",
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.find_path_to_root(
            G,
            {
                "B0": {
                    "nodes": ["5", "4", "3", "6", "7"],
                    "root": "1",
                    "isPositive": True,
                    "Base": "3",
                }
            },
            "7",
            "11",
        ) == ["1", "2", "3", "6", "7"]
        assert maximum_priority_matching.find_path_to_root(
            G,
            {
                "B1": {
                    "nodes": ["12", "11", "10"],
                    "root": "8",
                    "isPositive": True,
                    "Base": "10",
                }
            },
            "11",
            "7",
        ) == ["8", "9", "10", "12", "11"]
        # cases when the base's blossom does not have parent and the base is the root in some tree
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "2": {
                "parent": "1",
                "priority": 2,
                "isMatched": False,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "3": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "4": {
                "parent": "3",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "5": {
                "parent": "4",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "6": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "7": {
                "parent": "6",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "6",
                "isExternal": False,
                "blossomsID": "B0",
            },
            "8": {
                "parent": None,
                "priority": 1,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "9": {
                "parent": None,
                "priority": 2,
                "isMatched": True,
                "isPositive": None,
                "isReachable": False,
                "root": None,
                "isExternal": True,
                "blossomsID": -1,
            },
            "10": {
                "parent": "12",
                "priority": 1,
                "isMatched": True,
                "isPositive": False,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "11": {
                "parent": "10",
                "priority": 1,
                "isMatched": True,
                "isPositive": True,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
            "12": {
                "parent": None,
                "priority": 1,
                "isMatched": False,
                "isPositive": True,
                "isReachable": True,
                "root": "12",
                "isExternal": False,
                "blossomsID": "B1",
            },
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": True},
            ("2", "3"): {"isMatched": False},
            ("3", "4"): {"isMatched": True},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": False},
            ("5", "7"): {"isMatched": True},
            ("6", "7"): {"isMatched": False},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": True},
            ("9", "10"): {"isMatched": False},
            ("10", "11"): {"isMatched": True},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": False},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert maximum_priority_matching.find_path_to_root(
            G,
            {
                "B0": {
                    "nodes": ["5", "4", "3", "6", "7"],
                    "root": "1",
                    "isPositive": True,
                    "Base": "6",
                }
            },
            "7",
            "11",
        ) == ["7", "5", "4", "3", "6"]
        assert maximum_priority_matching.find_path_to_root(
            G,
            {
                "B1": {
                    "nodes": ["12", "11", "10"],
                    "root": "8",
                    "isPositive": True,
                    "Base": "12",
                }
            },
            "11",
            "7",
        ) == ["11", "10", "12"]

    def test_reverse_path(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("4", "5"),
            ("5", "6"),
            ("6", "7"),
            ("7", "8"),
            ("7", "9"),
            ("7", "3"),
        ]
        nodes_attrs = {
            "1": {"isMatched": False},
            "2": {"isMatched": True},
            "3": {"isMatched": True},
            "4": {"isMatched": True},
            "5": {"isMatched": True},
            "6": {"isMatched": True},
            "7": {"isMatched": True},
            "8": {"isMatched": False},
            "9": {"isMatched": True},
            "10": {"isMatched": True},
            "11": {"isMatched": True},
            "12": {"isMatched": True},
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "6"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "8"): {"isMatched": False},
            ("7", "3"): {"isMatched": False},
            ("7", "9"): {"isMatched": False},
        }

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        maximum_priority_matching.reverse_path(G, ["1", "2", "3"])
        matching_edges = nx.get_edge_attributes(G, "isMatched")
        assert matching_edges[("1", "2")] == True
        assert matching_edges[("2", "3")] == False
        maximum_priority_matching.reverse_path(G, ["8", "7", "6"])
        matching_edges = nx.get_edge_attributes(G, "isMatched")
        assert matching_edges[("7", "8")] == True
        assert matching_edges[("6", "7")] == False

        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        edges = [
            ("1", "2"),
            ("2", "3"),
            ("3", "4"),
            ("3", "6"),
            ("4", "5"),
            ("5", "7"),
            ("6", "7"),
            ("7", "11"),
            ("8", "9"),
            ("9", "10"),
            ("10", "11"),
            ("10", "12"),
            ("11", "12"),
        ]
        nodes_attrs = {
            "1": {"priority": 1, "isMatched": False},
            "2": {"priority": 2, "isMatched": True},
            "3": {"priority": 1, "isMatched": True},
            "4": {"priority": 1, "isMatched": True},
            "5": {"priority": 1, "isMatched": True},
            "6": {"priority": 1, "isMatched": True},
            "7": {"priority": 1, "isMatched": True},
            "8": {"priority": 1, "isMatched": False},
            "9": {"priority": 2, "isMatched": True},
            "10": {"priority": 1, "isMatched": True},
            "11": {"priority": 1, "isMatched": True},
            "12": {"priority": 1, "isMatched": True},
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False},
            ("2", "3"): {"isMatched": True},
            ("3", "4"): {"isMatched": False},
            ("3", "6"): {"isMatched": False},
            ("4", "5"): {"isMatched": True},
            ("5", "7"): {"isMatched": False},
            ("6", "7"): {"isMatched": True},
            ("7", "11"): {"isMatched": False},
            ("8", "9"): {"isMatched": False},
            ("9", "10"): {"isMatched": True},
            ("10", "11"): {"isMatched": False},
            ("10", "12"): {"isMatched": False},
            ("11", "12"): {"isMatched": True},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        matching_edges = nx.get_edge_attributes(G, "isMatched")
        matching_info = nx.get_edge_attributes(G, "isMatched")
        maximum_priority_matching.reverse_path(
            G, ["8", "9", "10", "12", "11", "7", "6", "3", "2", "1"]
        )
        matching_edges[("8", "9")] == True
        matching_edges[("9", "10")] == False
        matching_edges[("10", "12")] == True
        matching_edges[("11", "12")] == False
        matching_edges[("7", "11")] == True
        matching_edges[("6", "7")] == False
        matching_edges[("3", "6")] == True
        matching_edges[("2", "3")] == False
        matching_edges[("1", "2")] == True
