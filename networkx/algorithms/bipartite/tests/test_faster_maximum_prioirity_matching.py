import random
import random as rd

import networkx as nx

# from networkx import convert_node_labels_to_integers as cnlti
from .. import faster_maximum_prioirity_matching

class TestFasterMaximumPriorityMatching:
    def find_maximum_priority_matching_bipartite(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [
            ("1", "2"),
            ("1", "4"),
            ("3", "6"),
            ("5", "6"),
        ]
        nodes_attrs = {
            "1": {"priority": 1, "Group": 1},
            "2": {"priority": 3, "Group": 2},
            "3": {"priority": 2, "Group": 1},
            "4": {"priority": 4, "Group": 2},
            "5": {"priority": 5, "Group": 1},
            "6": {"priority": 6, "Group": 2},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert faster_maximum_prioirity_matching.find_maximum_priority_matching_bipartite(G) == [("1", "2"), ("3", "6")]
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [
            ("1", "2"),
            ("1", "3"),
            ("2", "4"),
            ("3", "4"),
            ("4", "5"),
            ("4", "6"),
        ]
        nodes_attrs = {
            "1": {"priority": 1, "Group": 1},
            "2": {"priority": 2, "Group": 1},
            "3": {"priority": 3, "Group": 1},
            "4": {"priority": 4, "Group": 2},
            "5": {"priority": 5, "Group": 2},
            "6": {"priority": 6, "Group": 2},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        assert faster_maximum_prioirity_matching.find_maximum_priority_matching_bipartite(G) == [
            ("1", "2"), ("3", "4")
        ]

        G = nx.Graph()
        n = 20
        x = random.randint(1, n)
        for i in range(n):
            G.add_node(str(i))

        for node in G.nodes:
            if str(node) != "0":
               G.nodes[node]["priority"] = random.randint(2, n)
        G.nodes["0"]["priority"] = 1
        G.nodes["0"]["Group"] = 1
        nx.set_node_attributes(G, {"1": {"Group": 2}})
        G.add_edge("0", "1")
        for i in range(2, n):
            if i <= x:
                nx.set_node_attributes(G, {str(i): {"Group": 1}})
            else:
                nx.set_node_attributes(G, {str(i): {"Group": 2}})

        for u in range(x):
           for v in range(x+1, n):
               p = rd.random()
               if (p > 0.95):
                    G.add_edge(str(u), str(v))

        matching = faster_maximum_prioirity_matching.find_maximum_priority_matching_bipartite(G)
        check = False
        for element in matching:
           if '0' in element:
            check = True
        assert check == True

    def augmenting_path_v1(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [("1", "2"), ("1", "4"), ("3", "6"), ("5", "6")]
        nodes_attrs = {
            "1": {"priority": 1, "Group": 1, "isMatched": True},
            "2": {"priority": 3, "Group": 2, "isMatched": False},
            "3": {"priority": 2, "Group": 1, "isMatched": False},
            "4": {"priority": 4, "Group": 2, "isMatched": True},
            "5": {"priority": 5, "Group": 1, "isMatched": True},
            "6": {"priority": 6, "Group": 2, "isMatched": True},
        }
        edges_attrs = {
            ('1', '2'): {"isMatched": False, "flow": 0},
            ('1', '4'): {"isMatched": True, "flow": 0},
            ('3', '6'): {"isMatched": False, "flow": 0},
            ('5', '6'): {"isMatched":True, "flow": 0},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert faster_maximum_prioirity_matching.augmenting_path_v1(
            G,[("1" , "4"), ("5", "6")],2
        ) == (
            [('1', '4'), ('3', '6')], True
        )
    def augmenting_path_v2(self):
        G = nx.Graph()
        nodes = ["1", "2", "3", "4", "5", "6"]
        edges = [("1", "2"), ("1", "4"), ("3", "6"), ("5", "6")]
        nodes_attrs = {
            "1": {"priority": 1, "Group": 1,"isMatched": True},
            "2": {"priority": 3, "Group": 2,"isMatched": False},
            "3": {"priority": 2, "Group": 1,"isMatched": False},
            "4": {"priority": 4, "Group": 2,"isMatched": True},
            "5": {"priority": 5, "Group": 1,"isMatched": True},
            "6": {"priority": 6, "Group": 2,"isMatched": True},
        }
        edges_attrs = {
            ("1", "2"): {"isMatched": False, "flow": 0},
            ("1", "4"): {"isMatched": True, "flow": 0},
            ("3", "6"): {"isMatched": False, "flow": 0},
            ("5", "6"): {"isMatched":True, "flow": 0},
        }
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.set_node_attributes(G, nodes_attrs)
        nx.set_edge_attributes(G, edges_attrs)
        assert faster_maximum_prioirity_matching.augmenting_path_v2(G,[("1" , "4"), ("5", "6")],2)
        ([("1", "4"), ("5", "6")], False)
