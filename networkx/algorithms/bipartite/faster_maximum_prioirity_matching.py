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

import doctest
import logging
import random
import random as rd
import time
from typing import Dict, List, Union

import networkx as nx

logging.basicConfig(filename="my_logger.log", level=logging.INFO, filemode="w")
logger = logging.getLogger()

def find_maximum_priority_matching_bipartite(G: nx.Graph):
    """
    "Faster Maximium Priority Matchings in Bipartite Graphs" by Tarjan, Robert E.

    Programmers: Roi Meshulam and Liroy Melamed

    Our find_maximum_priority_matching_bipartite gets bipartite graph and returns the maximum priority matching

    :param G: nx.Graph
    :return: A list of edges

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6']
    >>> edges = [('1', '2'), ('1', '4'), ('3', '6'),('5', '6')]
    >>> nodes_attrs = {'1': {"priority": 1, "Group": 1},'2': {"priority": 3, "Group": 2},'3': {"priority": 2, "Group": 1},'4': {"priority": 4, "Group": 2},'5': {"priority": 5, "Group": 1},'6': {"priority": 6, "Group": 2}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> find_maximum_priority_matching_bipartite(G)
    [('1', '2'), ('3', '6')]

    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6']
    >>> edges = [('1', '2'), ('1', '3'), ('2', '4'), ('3', '4'), ('4', '5'), ('4', '6')]
    >>> nodes_attrs = {'1': {"priority": 1, "Group": 1},'2': {"priority": 2, "Group": 1},'3': {"priority": 3, "Group": 1},'4': {"priority": 4, "Group": 2},'5': {"priority": 5, "Group": 2},'6': {"priority": 6, "Group": 2}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> find_maximum_priority_matching_bipartite(G)
    [('1', '2'), ('3', '4')]

    >>> G = nx.Graph()
    >>> n = 20
    >>> x = random.randint(1,n)
    >>> for i in range(n):
    ...     G.add_node(str(i))

    >>> for node in G.nodes:
    ...     if str(node) != '0':
    ...        G.nodes[node]['priority']= random.randint(2,n)
    >>> G.nodes['0']['priority']= 1
    >>> G.nodes['0']['Group']= 1
    >>> nx.set_node_attributes(G,{'1':{'Group':2}})

    >>> G.add_edge('0','1')

    >>> for i in range(2,n):
    ...    if i<=x:
    ...        nx.set_node_attributes(G,{str(i):{"Group":1}})
    ...    else:
    ...        nx.set_node_attributes(G,{str(i):{"Group":2}})

    >>> for u in range(x):
    ...    for v in range(x+1,n):
    ...        p = rd.random()
    ...        if(p>0.95):
    ...            G.add_edge(str(u),str(v))

    >>> matching = find_maximum_priority_matching_bipartite(G)
    >>> check = False
    >>> for element in matching:
    ...    if '0' in element:
    ...        check=True
    >>> print(check)
    True
    """
    logger.info("Find max prioirity matching for bipartite G")
    for node in G.nodes:
        nx.set_node_attributes(G, {node: {"isMatched": False}})

    matched_edges = nx.maximal_matching(G)
    logger.info("Find maximal matching for G %s", str(matched_edges))
    for (u, v) in G.edges:
        if (u, v) in matched_edges:
            nx.set_edge_attributes(G, {(u, v): {"isMatched": True}})
            nx.set_node_attributes(G, {u: {"isMatched": True}})
            nx.set_node_attributes(G, {v: {"isMatched": True}})
        else:
            nx.set_edge_attributes(G, {(u, v): {"isMatched": False}})
    # The algorithm maximizes the matching for each prioirty
    priority_size = G.number_of_nodes()
    for priority in range(1, priority_size + 1):
        matching_info = nx.get_edge_attributes(G, "isMatched")
        # our matching
        m1 = []
        m2 = []
        m3 = []
        # m1 is the first matching in prioirty i before we run the algorithm
        for edge in matching_info:
            if matching_info[edge] == True:
                m1.append(edge)
        # loop condition indicates if there are more augmenting paths
        loop_condition = True
        while loop_condition:
            logger.info("searching for augmenting path for prioirity %s", str(priority))
            result = augmenting_path_v1(G, m1, priority)
            logger.info("new matching %s", str(result[0]))
            # update the matching
            m1 = result[0]
            loop_condition = result[1]
        # update the matching
        m2 = m1
        loop_condition = True
        while loop_condition:
            logger.info("searching for augmenting path for prioirity %s", str(priority))
            result = augmenting_path_v2(G, m2, priority)
            logger.info("new matching %s", str(result[0]))
            # update the matching
            m2 = result[0]
            loop_condition = result[1]
        # update the matching
        m3 = m2
        # update the matching in G
        for edge in G.edges:
            if (edge[0], edge[1]) in m3:
                nx.set_edge_attributes(G, {edge: {"isMatched": True}})
            elif (edge[1], edge[0]) in m3:
                nx.set_edge_attributes(G, {edge: {"isMatched": True}})
            else:
                nx.set_edge_attributes(G, {edge: {"isMatched": False}})
    # The final matching
    matching = m3
    return matching


def augmenting_path_v1(G: nx.Graph, m1: list, priority: int):
    """
    "Faster Maximium Priority Matchings in Bipartite Graphs" by Tarjan, Robert E.

    Programmers: Roi Meshulam and Liroy Melamed

    Our augmenting_path_v1 is a private function that gets bipartite graph , curr matching and the curr prioirity and find an augmenting path and increase the matching

    :param G: nx.Graph , m1 : list , prioirity: int
    :return: A list of edges and bool

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6']
    >>> edges = [('1', '2'), ('1', '4'), ('3', '6'),('5', '6')]
    >>> nodes_attrs = {'1': {"priority": 1, "Group": 1,"isMatched": True},'2': {"priority": 3, "Group": 2,"isMatched": False},'3': {"priority": 2, "Group": 1,"isMatched": False},'4': {"priority": 4, "Group": 2,"isMatched": True},'5': {"priority": 5, "Group": 1,"isMatched": True},'6': {"priority": 6, "Group": 2,"isMatched": True}    }
    >>> edges_attrs = {('1', '2'): {"isMatched": False ,"flow":0}, ('1', '4'): {"isMatched": True ,"flow":0}, ('3', '6'): {"isMatched": False ,"flow":0},('5','6'):{"isMatched":True ,"flow":0}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> augmenting_path_v1(G,[('1' , '4'), ('5', '6')],2)
    ([('1', '4'), ('3', '6')], True)

    """
    # reset the flow attr in each edge
    for edge in G.edges:
        nx.set_edge_attributes(G, {edge: {"flow": 0}})
    flow_info = nx.get_edge_attributes(G, "flow")
    m2 = []
    # if path count is 0 there are no more augmenting paths
    path_count = 0
    # Temp graph is a direct graph according to the instruction of the algo
    # if we want to use cython:
    # temp_graph = algo2_library.generate_diGraph(G,m1,priority,True)
    temp_graph = generate_diGraph(G, m1, priority, True)
    # all the paths from node 's' to node 't'
    paths = nx.all_simple_paths(temp_graph, source="s", target="t")
    # update path_count
    for path in paths:
        path_count = path_count + 1
    # there are no more augmenting paths for V1 Group
    if path_count == 0:
        return (m1, False)
    # there are more augmenting paths
    else:
        # take the first path from paths
        paths = nx.all_simple_paths(temp_graph, source="s", target="t")
        temp = []
        for path in paths:
            # temp is the path without 's' and 't'
            for i in range(1, len(path) - 1):
                temp.append(path[i])
            # change all attr "flow" to 1 for each edge in temp_graph that in the path
            for j in range(0, len(temp) - 1):
                if (temp[j], temp[j + 1]) in flow_info:
                    nx.set_edge_attributes(G, {(temp[j], temp[j + 1]): {"flow": 1}})
                else:
                    nx.set_edge_attributes(G, {(temp[j + 1], temp[j]): {"flow": 1}})
            # info
            flow_info = nx.get_edge_attributes(G, "flow")
            Group_info = nx.get_node_attributes(G, "Group")

            for edge in G.edges:
                # update the new matching
                if Group_info[edge[0]] == 1 and Group_info[edge[1]] == 2:
                    u = edge[0]
                    v = edge[1]
                    if (u, v) in temp_graph.edges and flow_info[(u, v)] == 1:
                        m2.append((u, v))
                    if (v, u) in temp_graph.edges and flow_info[(u, v)] == 0:
                        m2.append((u, v))

                else:
                    v = edge[0]
                    u = edge[1]

                    if (u, v) in temp_graph.edges and flow_info[(v, u)] == 1:
                        m2.append((v, u))
                    if (v, u) in temp_graph.edges and flow_info[(v, u)] == 0:
                        m2.append((v, u))
            # return the new matching and that there are maybe more augmenting paths
            return (m2, True)


def augmenting_path_v2(G: nx.Graph, m2: list, priority: int):
    """
    "Faster Maximium Priority Matchings in Bipartite Graphs" by Tarjan, Robert E.

    Programmers: Roi Meshulam and Liroy Melamed

    Our augmenting_path_v2 is a private function that gets bipartite graph , curr matching and the curr prioirity and find an augmenting path and increase the matching

    :param G: nx.Graph , m1 : list , prioirity: int
    :return: A list of edges and bool

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6']
    >>> edges = [('1', '2'), ('1', '4'), ('3', '6'),('5', '6')]
    >>> nodes_attrs = {'1': {"priority": 1, "Group": 1,"isMatched": True},'2': {"priority": 3, "Group": 2,"isMatched": False},'3': {"priority": 2, "Group": 1,"isMatched": False},'4': {"priority": 4, "Group": 2,"isMatched": True},'5': {"priority": 5, "Group": 1,"isMatched": True},'6': {"priority": 6, "Group": 2,"isMatched": True}    }
    >>> edges_attrs = {('1', '2'): {"isMatched": False ,"flow":0}, ('1', '4'): {"isMatched": True ,"flow":0}, ('3', '6'): {"isMatched": False ,"flow":0},('5','6'):{"isMatched":True ,"flow":0}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> augmenting_path_v2(G,[('1' , '4'), ('5', '6')],2)
    ([('1', '4'), ('5', '6')], False)

    """

    # reset the flow attr in each edge
    for edge in G.edges:
        nx.set_edge_attributes(G, {edge: {"flow": 0}})
    # info
    flow_info = nx.get_edge_attributes(G, "flow")
    # the new matching
    m3 = []
    # if path count is 0 there are no more augmenting paths
    path_count = 0
    # Temp graph is a direct graph according to the instruction of the algo
    # if we want to use cython:
    # temp_graph = algo2_library.generate_diGraph(G, m2, priority, False)
    temp_graph = generate_diGraph(G, m2, priority, False)
    # all the paths from node 's' to node 't'
    paths = nx.all_simple_paths(temp_graph, source="s", target="t")
    # update path_count
    for path in paths:
        path_count = path_count + 1
    # there are no more augmenting paths for V1 Group
    if path_count == 0:
        return (m2, False)
    # there are more augmenting paths
    else:
        # take the first path from paths
        paths = nx.all_simple_paths(temp_graph, source="s", target="t")
        temp = []
        # temp is the path without 's' and 't'
        for path in paths:
            for i in range(1, len(path) - 1):
                temp.append(path[i])
            for j in range(0, len(temp) - 1):
                # change all attr "flow" to 1 for each edge in temp_graph that in the path
                if (temp[j], temp[j + 1]) in flow_info:
                    nx.set_edge_attributes(G, {(temp[j], temp[j + 1]): {"flow": 1}})
                else:
                    nx.set_edge_attributes(G, {(temp[j + 1], temp[j]): {"flow": 1}})
            # info
            flow_info = nx.get_edge_attributes(G, "flow")
            Group_info = nx.get_node_attributes(G, "Group")
            # update the new matching
            for edge in G.edges:
                if Group_info[edge[0]] == 1 and Group_info[edge[1]] == 2:
                    u = edge[0]
                    v = edge[1]
                    if (u, v) in temp_graph.edges and flow_info[(u, v)] == 1:
                        m3.append((u, v))
                    if (v, u) in temp_graph.edges and flow_info[(u, v)] == 0:
                        m3.append((u, v))

                else:
                    v = edge[0]
                    u = edge[1]
                    if (u, v) in temp_graph.edges and flow_info[(v, u)] == 1:
                        m3.append((v, u))
                    if (v, u) in temp_graph.edges and flow_info[(v, u)] == 0:
                        m3.append((v, u))
            # return the new matching and that there are maybe more augmenting paths
            return (m3, True)


def generate_diGraph(G: nx.Graph, m: list, priority: int, flag: bool):
    """
    "Faster Maximium Priority Matchings in Bipartite Graphs" by Tarjan, Robert E.

    Programmers: Roi Meshulam and Liroy Melamed

    Our generate_diGraph is a private function that gets bipartite graph , curr matching ,the curr prioirity and flag and generate a new direct graph according to
    the algorithm's instructions

    :param G: nx.Graph , m1 : list , prioirity: int
    :return: A list of edges and bool

    """
    ans = nx.DiGraph()
    # info
    priority_info = nx.get_node_attributes(G, "priority")
    Gruop_info = nx.get_node_attributes(G, "Group")
    matching_info = nx.get_node_attributes(G, "isMatched")

    # generate graph for augmenting_path_v1
    if flag is True:
        # add new nodes 's' and 't' and add edges to the relevant nodes in V1
        ans.add_node("s")
        ans.add_node("t")
        for node in G.nodes:
            ans.add_node(node)
            if (
                Gruop_info[node] == 1
                and matching_info[node] is False
                and priority_info[node] == priority
            ):
                ans.add_edges_from([("s", node)])
            if (
                Gruop_info[node] == 1
                and matching_info[node] is True
                and priority_info[node] > priority
            ):
                ans.add_edges_from([(node, "t")])

        # add the edges from G with the right direction
        for edge in G.edges:
            if Gruop_info[edge[0]] == 1 and Gruop_info[edge[1]] == 2:
                u = edge[0]
                v = edge[1]

                if (u, v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v, u) in m:
                    ans.add_edges_from([(v, u)])
                # {u,v} is not a matching edge
                else:
                    ans.add_edges_from([(u, v)])

            else:
                v = edge[0]
                u = edge[1]

                if (u, v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v, u) in m:
                    ans.add_edges_from([(v, u)])
                    # {u,v} is not a matching edge
                else:
                    ans.add_edges_from([(u, v)])

        return ans

    # flag is false , generate graph for augmenting_path_v2
    else:
        # add new nodes 's' and 't' and add edges to the relevant nodes in V2
        ans.add_node("s")
        ans.add_node("t")
        for node in G.nodes:
            ans.add_node(node)
            if (
                Gruop_info[node] == 2
                and matching_info[node] is True
                and priority_info[node] > priority
            ):
                ans.add_edges_from([("s", node)])
            if (
                Gruop_info[node] == 2
                and matching_info[node] is False
                and priority_info[node] == priority
            ):
                ans.add_edges_from([(node, "t")])
        # add the edges from G with the right direction
        for edge in G.edges:
            if Gruop_info[edge[0]] == 1 and Gruop_info[edge[1]] == 2:
                u = edge[0]
                v = edge[1]

                if (u, v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v, u) in m:
                    ans.add_edges_from([(v, u)])
                else:
                    ans.add_edges_from([(u, v)])

            else:
                v = edge[0]
                u = edge[1]

                if (u, v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v, u) in m:
                    ans.add_edges_from([(v, u)])
                else:
                    ans.add_edges_from([(u, v)])

        return ans
    
def reverse_path(G: nx.Graph, path):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our reverse_path is a private function. The function gets graph and path and reverse the matching and the non matching
    edges.

    :param G: nx.Graph , List: edges
    :return: void

    Tests:

    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"isMatched": False},'2': {"isMatched": True},'3': {"isMatched": True},'4': {"isMatched": True},'5': {"isMatched": True},'6': {"isMatched": True},'7': {"isMatched": True},'8': {"isMatched": False},'9': {"isMatched": True},'10': {"isMatched": True},'11': {"isMatched": True},'12': {"isMatched": True}}
    >>> edges_attrs = {('1', '2'):{"isMatched":False},('2', '3'):{"isMatched":True},('3', '4'):{"isMatched":False},('4', '5'):{"isMatched":True},('5', '6'):{"isMatched":False},('6', '7'):{"isMatched":True},('7', '8'):{"isMatched":False},('7', '3'):{"isMatched":False},('7', '9'):{"isMatched":False}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> reverse_path(G , ['1','2','3'])
    >>> matching_edges = nx.get_edge_attributes(G, "isMatched")
    >>> print(matching_edges[('1', '2')])
    True
    >>> print(matching_edges[('2', '3')])
    False

    >>> reverse_path(G , ['8','7','6'])
    >>> matching_edges = nx.get_edge_attributes(G, "isMatched")
    >>> print(matching_edges[('7', '8')])
    True
    >>> print(matching_edges[('6', '7')])
    False

    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"priority": 1 , "isMatched":False},'2': {"priority": 2, "isMatched":True},'3': {"priority": 1, "isMatched":True},'4': {"priority": 1, "isMatched":True},'5': {"priority": 1, "isMatched":True},'6': {"priority": 1, "isMatched":True},'7': {"priority": 1, "isMatched":True},'8': {"priority": 1, "isMatched":False},'9': {"priority": 2, "isMatched":True},'10': {"priority": 1, "isMatched":True},'11': {"priority": 1, "isMatched":True},'12': {"priority": 1, "isMatched":True}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False},('2', '3'): {"isMatched": True},('3', '4'): {"isMatched": False},('3', '6'): {"isMatched": False}, ('4', '5'): {"isMatched": True},('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True},('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False},('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False},('10', '12'): {"isMatched": False},('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> matching_edges = nx.get_edge_attributes(G, 'isMatched')
    >>> matching_info = nx.get_edge_attributes(G, 'isMatched')
    >>> reverse_path(G , ['8','9','10','12','11','7','6','3','2','1'])
    >>> matching_edges = nx.get_edge_attributes(G, "isMatched")
    >>> print(matching_edges[('8', '9')])
    True
    >>> print(matching_edges[('9', '10')])
    False
    >>> print(matching_edges[('10', '12')])
    True
    >>> print(matching_edges[('11', '12')])
    False
    >>> print(matching_edges[('7', '11')])
    True
    >>> print(matching_edges[('6', '7')])
    False
    >>> print(matching_edges[('3', '6')])
    True
    >>> print(matching_edges[('2', '3')])
    False
    >>> print(matching_edges[('1', '2')])
    True



    """

    matching_nodes = nx.get_node_attributes(G, "isMatched")
    matching_edges = nx.get_edge_attributes(G, "isMatched")
    for i in range(0, len(path) - 1):
        if (path[i], path[i + 1]) in matching_edges:
            nx.set_edge_attributes(
                G,
                {
                    (path[i], path[i + 1]): {
                        "isMatched": not matching_edges[(path[i], path[i + 1])]
                    }
                },
            )
        else:
            nx.set_edge_attributes(
                G,
                {
                    (path[i + 1], path[i]): {
                        "isMatched": not matching_edges[(path[i + 1], path[i])]
                    }
                },
            )

    nx.set_node_attributes(G, {path[0]: {"isMatched": not matching_nodes[path[0]]}})
    nx.set_node_attributes(G, {path[-1]: {"isMatched": not matching_nodes[path[-1]]}})


if __name__ == "__main__":
    print(doctest.testmod())
