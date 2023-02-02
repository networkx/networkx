"""
Programmers: Roi Meshulam and Liroy Melamed

This file is implemation of "Faster Maximum Prioirity Matching in bipartite graphs" from the article that
written by Jonathan Turner.

A maximum priority matching is a matching in an undirected graph that maximizes a priority
score defined with respect to given vertex priorities. An earlier paper showed how to find
maximum priority matchings in unweighted graphs. This paper describes an algorithm for
bipartite graphs that is faster when the number of distinct priority classes is limited. For graphs
with k distinct priority classes it runs in O(kmn1/2) time, where n is the number of vertices in the
graph and m is the number of edges. 

link to the article: "https://openscholarship.wustl.edu/cgi/viewcontent.cgi?article=1511&context=cse_research"

more details about this algo can be found in the following link: "http://myusername.pythonanywhere.com/"

"""
import pytest
import unittest
import random
import random as rd

import networkx as nx

# from networkx import convert_node_labels_to_integers as cnlti
# from .. import faster_maximum_prioirity_matching
from networkx.algorithms.bipartite.faster_maximum_prioirity_matching import (
    find_maximum_priority_matching_bipartite,
    augmenting_path_v1,
    augmenting_path_v2,
    reverse_path,

)

class TestFasterMaximumPriorityMatching(unittest.TestCase):
    def test_find_maximum_priority_matching_bipartite(self):
        G = nx.Graph()
        edges = [
            ("1", "2"),
            ("1", "4"),
            ("3", "6"),
            ("5", "6"),
        ]
        nodes_attrs = {
            "1": {"priority": 1},
            "2": {"priority": 3},
            "3": {"priority": 2},
            "4": {"priority": 4},
            "5": {"priority": 5},
            "6": {"priority": 6},
        }
        G.add_nodes_from(["1","3","5"], bipartite = 0)
        G.add_nodes_from(["2","4","6"], bipartite = 1)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert (
            find_maximum_priority_matching_bipartite(
                G
            )
            == [("1", "2"), ("3", "6")]
        )
        G = nx.Graph()
        edges = [
            ("1", "2"),
            ("1", "3"),
            ("2", "4"),
            ("3", "4"),
            ("4", "5"),
            ("4", "6"),
        ]
        nodes_attrs = {
            "1": {"priority": 1,},
            "2": {"priority": 2,},
            "3": {"priority": 3,},
            "4": {"priority": 4,},
            "5": {"priority": 5,},
            "6": {"priority": 6,},
        }
        G.add_nodes_from(['1','2','3'],bipartite =0)
        G.add_nodes_from(['4','5','6'],bipartite =1)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert (
            find_maximum_priority_matching_bipartite(
                G
            )
            == [("1", "2"), ("3", "4")]
        )

        G = nx.Graph()
        n = 20
        x = random.randint(1, n)
        for i in range(n):
            G.add_node(str(i))

        for node in G.nodes:
            if str(node) != "0":
                G.nodes[node]["priority"] = random.randint(2, n)
        G.nodes["0"]["priority"] = 1
        G.nodes["0"]["bipartite"] = 1
        nx.set_node_attributes(G, {"1": {"bipartite": 1}})
        G.add_edge("0", "1")
        for i in range(2, n):
            if i <= x:
                nx.set_node_attributes(G, {str(i): {"bipartite": 0}})
            else:
                nx.set_node_attributes(G, {str(i): {"bipartite": 1}})

        for u in range(x):
            for v in range(x + 1, n):
                p = rd.random()
                if p > 0.95:
                    G.add_edge(str(u), str(v))

        matching = (
            find_maximum_priority_matching_bipartite(
                G
            )
        )
        check = False
        for element in matching:
            if "0" in element:
                check = True
        assert check == True

    def test_augmenting_path_v1(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [("1", "2"), ("1", "4"), ("3", "6"), ("5", "6")]
        nodes_attrs = {
            "1": {"priority": 1, "bipartite": 0, "isMatched": True},
            "2": {"priority": 3, "bipartite": 1, "isMatched": False},
            "3": {"priority": 2, "bipartite": 0, "isMatched": False},
            "4": {"priority": 4, "bipartite": 1, "isMatched": True},
            "5": {"priority": 5, "bipartite": 0, "isMatched": True},
            "6": {"priority": 6, "bipartite": 1, "isMatched": True},
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False, "flow": 0},
            ("1", "4"): {"isMatched": True, "flow": 0},
            ("3", "6"): {"isMatched": False, "flow": 0},
            ("5", "6"): {"isMatched": True, "flow": 0},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert augmenting_path_v1(
            G, [("1", "4"), ("5", "6")], 2
        ) == ([("1", "4"), ("3", "6")], True)

    def test_augmenting_path_v2(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [("1", "2"), ("1", "4"), ("3", "6"), ("5", "6")]
        nodes_attrs = {
            "1": {"priority": 1, "bipartite": 0, "isMatched": True},
            "2": {"priority": 3, "bipartite": 1, "isMatched": False},
            "3": {"priority": 2, "bipartite": 0, "isMatched": False},
            "4": {"priority": 4, "bipartite": 1, "isMatched": True},
            "5": {"priority": 5, "bipartite": 0, "isMatched": True},
            "6": {"priority": 6, "bipartite": 1, "isMatched": True},
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False, "flow": 0},
            ("1", "4"): {"isMatched": True, "flow": 0},
            ("3", "6"): {"isMatched": False, "flow": 0},
            ("5", "6"): {"isMatched": True, "flow": 0},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert augmenting_path_v2(
            G, [("1", "4"), ("5", "6")], 2
        ) == ([("1", "4"), ("5", "6")], False)

if __name__ == '__main__':
    unittest.main()
    
