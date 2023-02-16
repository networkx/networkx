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
import doctest
import logging
import random
import random as rd
import time
from typing import Dict, List, Union

import networkx as nx

logging.basicConfig(filename="my_logger.log", level=logging.INFO, filemode="w")
logger = logging.getLogger()


def find_priority_score(G: nx.Graph, matching: list):
    """
    "The bounded edge coloring problem and offline crossbar scheduling" by Turner, Jonathan S.

    Programmers: Roi Meshulam and Liroy Melamed

    Our find_priority_score gets graph and returns the current priority score as a string
    This Function gets the base class for undirected graphs.

    :param G: nx.Graph
    :return: A string represent the current priority matching score

    Tests:

    # Test with a graph that has no matching edges
    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = []
    >>> matching = []
    >>> nodes_attrs = {'1': {"priority":1},'2': {"priority":8},'3': {"priority":6},'4': {"priority":5},'5': {"priority":2},'6': {"priority":4},'7': {"priority":3},'8': {"priority":1},'9': {"priority":7}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> find_priority_score(G, matching)
    '000000000'

    # Test with a graph that has all matching edges
    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"priority":1},'2': {"priority":8},'3': {"priority":6},'4': {"priority":5},'5': {"priority":2},'6': {"priority":4},'7': {"priority":3},'8': {"priority":1},'9': {"priority":7}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> matching = [('1', '2'), ('3', '4'), ('5', '6'), ('7', '8')]
    >>> find_priority_score(G, matching)
    '211111010'
    """
    #  n-ary
    temp = [0]
    priority_size = G.number_of_nodes()
    score_list = temp * priority_size
    # find the maximum prioirty matching
    # matching = find_maximum_priority_matching(G)
    # inilize all node attr (ismatched) to false
    for node in G.nodes:
        nx.set_node_attributes(G, {node: {"isMatched": False}})
    # if node touch the matching change nodes' attr to true
    for element in matching:
        nx.set_node_attributes(G, {element[0]: {"isMatched": True}})
        nx.set_node_attributes(G, {element[1]: {"isMatched": True}})
    matching_info = nx.get_node_attributes(G, "isMatched")
    priority_info = nx.get_node_attributes(G, "priority")
    # update the score
    for node in G.nodes:
        if matching_info[node] is True:
            score_list[priority_info[node] - 1] = (
                score_list[priority_info[node] - 1] + 1
            )
    score = ""
    for x in score_list:
        score += str(x)
    return score


def find_maximum_priority_matching(G: nx.Graph):
    """
    We describe a variation of the augmenting path method (Edmonds’ algorithm) that
    finds a matching with maximum priority score in O(mn) time." by Turner, Jonathan S.

    Programmers: Roi Meshulam and Liroy Melamed

    Our find_maximum_priority_matching gets graph and returns the maximum priority matching as a set of edges.

    :param G: nx.Graph
    :return: A list of edges

    Tests:

    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"priority":1},'2': {"priority":8},'3': {"priority":6 },'4': {"priority":5},'5': {"priority":2 },'6': {"priority":4},'7': {"priority":3},'8': {"priority":1},'9': {"priority":7}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> find_maximum_priority_matching(G)
    [('1', '2'), ('3', '4'), ('5', '6'), ('7', '8')]

    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"priority": 1},'2': {"priority": 2},'3': {"priority": 1},'4': {"priority": 1},'5': {"priority": 1},'6': {"priority": 1},'7': {"priority": 1},'8': {"priority": 1},'9': {"priority": 2},'10': {"priority": 1},'11': {"priority": 1},'12': {"priority": 1}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> find_maximum_priority_matching(G)
    [('1', '2'), ('3', '6'), ('4', '5'), ('7', '11'), ('8', '9'), ('10', '12')]

    >>> G = nx.Graph()
    >>> for i in range(50):
    ...    G.add_node(str(i))

    >>> for node in G.nodes:
    ...     G.nodes[node]['priority']= random.randint(1,50)
    >>> G.add_node('test')
    >>> G.nodes['test']['priority']= 1
    >>> edges =nx.erdos_renyi_graph(50,0.005).edges()
    >>> for u,v in edges:
    ...     G.add_edge(str(u),str(v))

    >>> G.add_edge('test','1')
    >>> matching = find_maximum_priority_matching(G)
    >>> check = False
    >>> for element in matching:
    ...     if 'test' in element:
    ...         check=True
    >>> print(check)
    True
    """
    prioirities = nx.get_node_attributes(G, "priority")
    for node in G.nodes:
        if node not in prioirities:
            raise Exception("All nodes need to be given a 'priority' attr")
        elif prioirities[node] is None:
            raise Exception("Nodes priority should be integer")
        elif prioirities[node] > len(G.nodes) or prioirities[node] < 1:
            raise Exception("All nodes' priority attr should be between [1,len(G.nodes)]")
        else:
            nx.set_node_attributes(
                G,
                {
                    node: {
                        "parent": None,
                        "isMatched": False,
                        "isPositive": False,
                        "isReachable": False,
                        "root": None,
                        "isExternal": True,
                        "blossomsID": -1,
                    }
                },
            )
    # find a first matching and we will improve it according to the priority
    matched_edges = nx.maximal_matching(G)
    logger.info("Find maximal matching for G %s", str(matched_edges))
    # update the nodes and edges attr after the first matching
    for (u, v) in G.edges:
        if (u, v) in matched_edges:
            nx.set_edge_attributes(G, {(u, v): {"isMatched": True}})
            nx.set_node_attributes(G, {u: {"isMatched": True}})
            nx.set_node_attributes(G, {v: {"isMatched": True}})
        else:
            nx.set_edge_attributes(G, {(u, v): {"isMatched": False}})
    temp_graph = G.copy()
    priority_size = G.number_of_nodes()
    # for each priority we maximize the priority score and the matching
    for priority in range(1, priority_size + 1):
        logger.info("Searching for augmenting paths for prioirity %s", priority)
        # loop_condition indicate that there is no more augmenting paths for this priority
        loop_condition = True
        while loop_condition:
            # find an augmenting path and update the graph
            loop_condition = find_augmenting_paths(temp_graph, priority)
        logger.info("There are no more augmenting paths for prioirity %d", priority)
    matching = []
    matching_info = nx.get_edge_attributes(temp_graph, "isMatched")
    for edge in matching_info:
        if matching_info[edge] == True:
            matching.append(edge)
    return matching


def find_augmenting_paths(G: nx.Graph, Priority: int):
    """
    "Data structures and network algorithms" by Tarjan, Robert E.

    Programmers: Roi Meshulam and Liroy Melamed

    Our find_augmenting_path Function gets graph and priority and finding augmenting path in the graph

    :param G: nx.Graph
    :param Priority: integer
    :return: The augmenting path as a list

    Tests:

    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"parent": None, "priority":1 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False,"isExternal":True,"blossomsID":-1},'2': {"parent": None, "priority":8 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'3': {"parent": None, "priority":6 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'4': {"parent": None, "priority":5 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'5': {"parent": None, "priority":2 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'6': {"parent": None, "priority":4 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'7': {"parent": None, "priority":3 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'8': {"parent": None, "priority":1 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'9': {"parent": None, "priority":7 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1}}
    >>> edges_attrs ={('1', '2'): {"isMatched": False},('2', '3'): {"isMatched": True},('3', '4'): {"isMatched": False},('4', '5'): {"isMatched": True}, ('5', '6'): {"isMatched": False},('6', '7'): {"isMatched": True},('7', '3'): {"isMatched": False},('7', '8'): {"isMatched": False},('7', '9'): {"isMatched": False}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G,edges_attrs)

    >>> prepare_for_algo(G , 1)
    ([('1', '2'), ('8', '7')], ['1', '8'])
    >>> find_augmenting_paths(G,1)
    True
    >>> prepare_for_algo(G , 1)
    ([('8', '7')], ['8'])
    >>> find_augmenting_paths(G,1)
    True
    >>> prepare_for_algo(G , 1)
    ([], [])
    >>> find_augmenting_paths(G,1)
    False
    >>> prepare_for_algo(G , 2)
    ([], [])
    >>> find_augmenting_paths(G,2)
    False
    >>> prepare_for_algo(G , 3)
    ([], [])
    >>> find_augmenting_paths(G,3)
    False
    >>> prepare_for_algo(G , 4)
    ([('6', '5'), ('6', '7')], ['6'])
    >>> find_augmenting_paths(G,4)
    True
    >>> prepare_for_algo(G , 4)
    ([], [])
    >>> find_augmenting_paths(G,4)
    False
    >>> prepare_for_algo(G , 5)
    ([('4', '3'), ('4', '5')], ['4'])
    >>> find_augmenting_paths(G,5)
    True
    >>> prepare_for_algo(G , 5)
    ([], [])
    >>> find_augmenting_paths(G,5)
    False
    >>> prepare_for_algo(G , 6)
    ([], [])
    >>> find_augmenting_paths(G,6)
    False
    >>> prepare_for_algo(G , 7)
    ([('9', '7')], ['9'])
    >>> find_augmenting_paths(G,7)
    False
    >>> prepare_for_algo(G , 8)
    ([], [])
    >>> find_augmenting_paths(G,8)
    False
    """
    # dictionary of all our blossoms
    blossoms: Dict = {}
    # preparation for the algorithm
    # if we want to use cython library
    # preparation1 = preparation.prepare_for_algo(G,Priority)
    preparation1 = prepare_for_algo(G, Priority)
    roots = preparation1[1]
    # if there are no more roots so we can proceed to the next priority
    if len(roots) == 0:
        logger.info("No relevant roots")
        return False
    eligible_edges = preparation1[0]
    logger.info("Current roots: %s", str(roots))
    while eligible_edges:
        logger.info("Current eligible edges: %s", str(eligible_edges))
        # select an eligible edge and remove it from the list
        edge = eligible_edges.pop(0)
        logger.info("Selected edge: %s", str(edge))
        # all info about the original graph in order to know which condition to make
        root_list = nx.get_node_attributes(G, "root")
        reachable_list = nx.get_node_attributes(G, "isReachable")
        positive_list = nx.get_node_attributes(G, "isPositive")
        matching_list = nx.get_node_attributes(G, "isMatched")
        priority_list = nx.get_node_attributes(G, "priority")
        matching_info = nx.get_edge_attributes(G, "isMatched")
        external_info = nx.get_node_attributes(G, "isExternal")
        blossoms_info = nx.get_node_attributes(G, "blossomsID")
        parents_info = nx.get_node_attributes(G, "parent")
        # Both nodes u,v are externals
        if external_info[edge[0]] is True and external_info[edge[1]] is True:
            # B(u) is positive
            if positive_list[edge[0]] is True:
                u = edge[0]
                v = edge[1]
                # check if B(V) is positive
                if positive_list[v] is True:
                    isPositive = True
                else:
                    isPositive = False
                # check if u,v in the same tree
                if root_list[u] == root_list[v]:
                    sameTree = True
                else:
                    sameTree = False
            elif positive_list[edge[1]] is True:
                u = edge[1]
                v = edge[0]
                # if B(V) was positive, the algo was entered to the previous condition
                isPositive = False
                # check if u,v in the same tree
                if root_list[u] == root_list[v]:
                    sameTree = True
                else:
                    sameTree = False
            else:
                continue
        # both of nodes are internals
        elif external_info[edge[0]] is False and external_info[edge[1]] is False:
            blossom_id0 = blossoms_info[edge[0]]
            blossom_id1 = blossoms_info[edge[1]]
            # check if the blossom of edge[0] is positive
            if blossoms[blossom_id0]["isPositive"] is True:
                u = edge[0]
                v = edge[1]
                # check if B(v) is positive
                if blossoms[blossom_id1]["isPositive"] is True:
                    isPositive = True
                else:
                    isPositive = False
                # check if B(u) and B(V) in the same tree
                if blossoms[blossom_id0]["root"] == blossoms[blossom_id1]["root"]:
                    sameTree = True
                else:
                    sameTree = False
            # check if the blossom of edge[1] is positive
            elif blossoms[blossom_id1]["isPositive"] is True:
                u = edge[1]
                v = edge[0]
                # if B(V) was positive, the algo was entered to the previous condition
                isPositive = False
                # check if B(u) and B(V) in the same tree
                if blossoms[blossom_id0]["root"] == blossoms[blossom_id1]["root"]:
                    sameTree = True
                else:
                    sameTree = False
            else:
                continue
        # one of the nodes is internal
        else:
            # check if edge[0] is internal
            if external_info[edge[0]] is False:
                blossom_id = blossoms_info[edge[0]]
                if blossoms[blossom_id]["isPositive"] is True:
                    u = edge[0]
                    v = edge[1]
                    # check if B(v) is positive
                    if positive_list[v] is True:
                        isPositive = True
                    else:
                        isPositive = False
                    # check if B(u) and B(v) are in the same tree
                    if root_list[v] == blossoms[blossom_id]["root"]:
                        sameTree = True
                    else:
                        sameTree = False
                elif positive_list[edge[1]] is True:
                    u = edge[1]
                    v = edge[0]
                    # if B(V) was positive, the algo was entered to the previous condition
                    isPositive = False
                    # check if B(u) and B(v) are in the same tree
                    if root_list[u] == blossoms[blossom_id]["root"]:
                        sameTree = True
                    else:
                        sameTree = False
                else:
                    continue
            # edge[1] is internal
            else:
                blossom_id = blossoms_info[edge[1]]
                if positive_list[edge[0]] is True:
                    u = edge[0]
                    v = edge[1]
                    # check if B(v) is positive
                    if blossoms[blossom_id]["isPositive"] is True:
                        isPositive = True
                    else:
                        isPositive = False
                    # check if B(u) and B(v) are in the same tree
                    if root_list[u] == blossoms[blossom_id]["root"]:
                        sameTree = True
                    else:
                        sameTree = False
                elif blossoms[blossom_id]["isPositive"] is True:
                    u = edge[1]
                    v = edge[0]
                    # if B(V) was positive, the algo was entered to the previous condition
                    isPositive = False
                    # check if B(u) and B(v) are in the same tree
                    if root_list[v] == blossoms[blossom_id]["root"]:
                        sameTree = True
                    else:
                        sameTree = False
                else:
                    continue

        logger.info("u : %s", u)
        logger.info("v : %s", v)
        logger.info("B(v) is positive : %s", str(isPositive))
        logger.info("B(v) and B(u) are in the same tree : %s", str(sameTree))
        logger.info("curr blossoms list: %s", str(blossoms))
        logger.info("priority list: %s", str(priority_list))
        # if v is unreached and matched (condition 1)
        if reachable_list[v] is False and matching_list[v] is True:
            logger.info("First condition")
            # making v a child of u
            nx.set_node_attributes(
                G,
                {
                    v: {
                        "root": root_list[u],
                        "isPositive": not (positive_list[u]),
                        "isReachable": True,
                        "parent": u,
                    }
                },
            )
            # update root_list
            root_list = nx.get_node_attributes(G, "root")
            # find the matched edge between v and w (another vertex in the Graph that incident to v)
            for w in G.neighbors(v):
                if w == u:
                    continue
                if (w, v) in matching_info:
                    # if p(w)>priority and (w,v) is the matching edge it is augmenting path
                    if matching_info[(w, v)] is True and priority_list[w] > Priority:
                        logger.info("There is an augmenting path")
                        # making w a child of v
                        nx.set_node_attributes(
                            G,
                            {
                                w: {
                                    "root": root_list[v],
                                    "isPositive": not (positive_list[v]),
                                    "isReachable": True,
                                    "parent": v,
                                }
                            },
                        )
                        # find the augmenting path
                        path = find_path_to_root(G, blossoms, w, v)
                        logger.info(str(path))
                        # update the augemnting path in the Graph
                        reverse_path(G, path)
                        logger.info(
                            "update the augemnting path in the Graph and try to find more for priority %d",
                            Priority,
                        )
                        return True
                    # if (w,v) is the matching edge and the prioirty of w his even or less then Prioirty
                    if matching_info[(w, v)] is True and priority_list[w] <= Priority:
                        logger.info(
                            "It is not an augmenting path, add all incident edges to node %s to eligible edges",
                            w,
                        )
                        # make w son of v in the tree
                        nx.set_node_attributes(
                            G,
                            {
                                w: {
                                    "root": root_list[v],
                                    "isPositive": not (positive_list[v]),
                                    "isReachable": True,
                                    "parent": v,
                                }
                            },
                        )
                        # add all his incident edges in eligible_edges
                        for neighbor in G.neighbors(w):
                            if neighbor != v:
                                # if the edge between w and neighbor is not in eligible edges yet
                                if (w, neighbor) not in eligible_edges and (
                                    neighbor,
                                    w,
                                ) not in eligible_edges:
                                    eligible_edges.append((w, neighbor))
                if (v, w) in matching_info:
                    # if p(w)>priority and (v,w) is the matching edge it is augmenting path
                    if matching_info[(v, w)] is True and priority_list[w] > Priority:
                        logger.info("There is an augmenting path")
                        # making w a child of v
                        nx.set_node_attributes(
                            G,
                            {
                                w: {
                                    "root": root_list[v],
                                    "isPositive": not (positive_list[v]),
                                    "isReachable": True,
                                    "parent": v,
                                }
                            },
                        )
                        # find the augmenting path
                        path = find_path_to_root(G, blossoms, w, v)
                        logger.info(str(path))
                        # update the augemnting path in G[0]
                        reverse_path(G, path)
                        logger.info(
                            "update the augemnting path in the Graph and try to find more for priority %d",
                            Priority,
                        )
                        return True
                    # if (v,w) is the matching edge and the prioirty of w his even or less then Prioirty
                    if matching_info[(v, w)] is True and priority_list[w] <= Priority:
                        logger.info(
                            "It is not an augmenting path, add all incident edges to node %s to eligible edges",
                            w,
                        )
                        # make w son of v in the tree
                        nx.set_node_attributes(
                            G,
                            {
                                w: {
                                    "root": root_list[v],
                                    "isPositive": not (positive_list[v]),
                                    "isReachable": True,
                                    "parent": v,
                                }
                            },
                        )
                        # add all his incident edges in eligible_edges
                        for neighbor in G.neighbors(w):
                            if neighbor != v:
                                # if the edge between w and neighbor is not in eligible edges yet
                                if (w, neighbor) not in eligible_edges and (
                                    neighbor,
                                    w,
                                ) not in eligible_edges:
                                    eligible_edges.append((w, neighbor))

        # if v is unreached and unmatched (condition 2)
        elif reachable_list[v] is False and matching_list[v] is False:
            logger.info("Second condition")
            logger.info("There is an augmenting path")
            # if u is external
            # if external_info[u] is True:
            path = find_path(G, blossoms, u, v, True)
            logger.info(str(path))
            reverse_path(G, path)
            logger.info(
                "update the augemnting path in the Graph and try to find more for priority %d",
                Priority,
            )
            return True
        # if v is even and in a different tree (condition 3)
        elif isPositive is True and not sameTree:
            logger.info("Third condition")
            logger.info("There is an augmenting path")
            path = find_path(G, blossoms, u, v, False)
            logger.info(str(path))
            reverse_path(G, path)
            logger.info(
                "update the augemnting path in the Graph and try to find more for priority %d",
                Priority,
            )
            return True
        # condition 4
        elif isPositive is True and sameTree:
            logger.info("Fourth condition")
            # info
            priority_list = nx.get_node_attributes(G, "priority")
            positive_list = nx.get_node_attributes(G, "isPositive")
            logger.info("Find blossom")
            result = find_blossom(G, blossoms, u, v)
            if result == None:
                return False
            # the blossom value
            blossom = result[0]
            # the blossom key
            key = result[1]
            logger.info("blossom_key: %s", key)
            logger.info(str(blossom))
            for node in blossom["nodes"]:
                # check if there is odd node in the cycle and his priority is higher then Priority, if there is one , so we have an augmenting path
                if positive_list[node] is False and priority_list[node] > Priority:
                    logger.info("There is an augmenting path")
                    paths = paths_to_base(blossom["nodes"], node, blossom["Base"])
                    first_path = paths[0]
                    second_path = paths[1]
                    x = first_path[0]
                    y = first_path[1]
                    w = second_path[0]
                    z = second_path[1]
                    if (x, y) in matching_info or (y, x) in matching_info:
                        if (x, y) in matching_info:
                            if matching_info[(x, y)] is True:
                                path = []
                                temp = parents_info[blossom["Base"]]
                                while temp != None:
                                    path.insert(0, temp)
                                    temp = parents_info[temp]
                                for element in reversed(first_path):
                                    path.append(element)
                                logger.info(str(path))
                                reverse_path(G, path)
                                logger.info(
                                    "update the augemnting path in the Graph and try to find more for priority %d",
                                    Priority,
                                )

                                return True
                        else:
                            if matching_info[(y, x)] is True:
                                path = []
                                temp = parents_info[blossom["Base"]]
                                while temp != None:
                                    path.insert(0, temp)
                                    temp = parents_info[temp]
                                for element in reversed(first_path):
                                    path.append(element)
                                logger.info(str(path))
                                reverse_path(G, path)
                                logger.info(
                                    "update the augemnting path in the Graph and try to find more for priority %d",
                                    Priority,
                                )
                                return True
                    else:
                        if (w, z) in matching_info:
                            if matching_info[(w, z)] is True:
                                path = []
                                temp = parents_info[blossom["Base"]]
                                while temp != None:
                                    path.insert(0, temp)
                                    temp = parents_info[temp]
                                for element in reversed(first_path):
                                    path.append(element)
                                logger.info(str(path))
                                reverse_path(G, path)
                                logger.info(
                                    "update the augemnting path in the Graph and try to find more for priority %d",
                                    Priority,
                                )
                                return True
                        else:
                            if matching_info[(z, w)] is True:
                                path = []
                                temp = parents_info[blossom["Base"]]
                                while temp != None:
                                    path.insert(0, temp)
                                    temp = parents_info[temp]
                                for element in reversed(first_path):
                                    path.append(element)
                                logger.info(str(path))
                                reverse_path(G, path)
                                logger.info(
                                    "update the augemnting path in the Graph and try to find more for priority %d",
                                    Priority,
                                )
                                return True

            logger.info(
                "There isn't an augmenting path yet, add all incident edges to the odds nodes in the blossom"
            )
            # there is no augmenting path add all incident edges to the odd nodes in the bolssom
            for node in blossom["nodes"]:
                if positive_list[node] is False:
                    for neighbor in G.neighbors(node):
                        if (
                            neighbor not in blossom["nodes"]
                            and (node, neighbor) not in eligible_edges
                            and (neighbor, node) not in eligible_edges
                        ):
                            eligible_edges.append((node, neighbor))

            logger.info("shrink_blossom and continue to next edge in eligeble edges")
            # shrink the bolssom and update the graph
            shrink_graph(G, blossom, key)

        else:
            logger.info("Ignore this edge")
            continue
    return False


def shrink_graph(G: nx.Graph, blossom, key):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our shrink_graph is a private function. The function gets graph , blossom , String (the blossom key) and change the
    nodes attributes according to the blossom

    :param G: nx.Graph ,blossom: Dictionary , key: String
    :return: Tuple of two lists

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'2': {"parent": '1', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'3': {"parent": '2', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'5': {"parent": '4', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'6': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'8': {"parent": None, "priority": 1, "isMatched": False, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'9': {"parent": None, "priority": 2, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'10': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'11': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'12': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False}, ('2', '3'): {"isMatched": True}, ('3', '4'): {"isMatched": False},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": True}, ('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False}, ('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> shrink_graph(G,{'nodes':['5','4','3','6','7']},'B0')
    [(False, 'B0'), (False, 'B0'), (False, 'B0'), (False, 'B0'), (False, 'B0')]

    >>> shrink_graph(G,{'nodes':['11','10','12']},'B1')
    [(False, 'B1'), (False, 'B1'), (False, 'B1')]

    # more tests for shrink_graph are in 'find_blossom' tests

    """
    for node in blossom["nodes"]:
        nx.set_node_attributes(G, {node: {"isExternal": False, "blossomsID": key}})
    test = []
    external_info = nx.get_node_attributes(G, "isExternal")
    blossoms_info = nx.get_node_attributes(G, "blossomsID")
    for node in blossom["nodes"]:
        test.append((external_info[node], blossoms_info[node]))
    return test


def prepare_for_algo(G: nx.Graph, Priority: int):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our prepare_for_algo is a private function. The function gets graph , number (priority) and returns
    the roots list and the eligible edges

    :param G: nx.Graph , Priority: Integer
    :return: Tuple of two lists

    Tests:

    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"parent": None, "priority":1 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False,"isExternal":True,"blossomsID":-1}, '2': {"parent": None, "priority":8 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'3': {"parent": None, "priority":6 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'4': {"parent": None, "priority":5 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},   '5': {"parent": None, "priority":2 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'6': {"parent": None, "priority":4 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'7': {"parent": None, "priority":3 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'8': {"parent": None, "priority":1 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'9': {"parent": None, "priority":7 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1}}
    >>> edges_attrs ={('1', '2'): {"isMatched": False},('2', '3'): {"isMatched": True},('3', '4'): {"isMatched": False},('4', '5'): {"isMatched": True}, ('5', '6'): {"isMatched": False},('6', '7'): {"isMatched": True},('7', '3'): {"isMatched": False},('7', '8'): {"isMatched": False},('7', '9'): {"isMatched": False}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> prepare_for_algo(G , 1)
    ([('1', '2'), ('8', '7')], ['1', '8'])

    >>> prepare_for_algo(G , 2)
    ([], [])

    >>> prepare_for_algo(G , 3)
    ([], [])

    >>> prepare_for_algo(G , 4)
    ([], [])

    >>> prepare_for_algo(G , 5)
    ([], [])

    >>> prepare_for_algo(G , 6)
    ([], [])

    >>> prepare_for_algo(G , 7)
    ([('9', '7')], ['9'])

    >>> prepare_for_algo(G , 8)
    ([], [])

    >>> G = nx.Graph()
    >>> nodes=['1','2','3','4','5','6','7','8','9']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('7', '9'),('7','3')]
    >>> nodes_attrs = {'1': {"parent": None, "priority":5 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False,"isExternal":True,"blossomsID":-1}, '2': {"parent": None, "priority":1 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'3': {"parent": None, "priority":8 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'4': {"parent": None, "priority":3 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},   '5': {"parent": None, "priority":2 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'6': {"parent": None, "priority":7 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'7': {"parent": None, "priority":4 ,"isMatched": True , "isPositive":False, "isReachable": False,"root":None,"isBolssom":False,'isExternal':True,"blossomsID":-1},'8': {"parent": None, "priority":6 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1},'9': {"parent": None, "priority":9 ,"isMatched": False, "isPositive":False, "isReachable": False,"root":None,"isBolssom":False, "isExternal":True,"blossomsID":-1}}
    >>> edges_attrs ={('1', '2'): {"isMatched": False},('2', '3'): {"isMatched": True},('3', '4'): {"isMatched": False},('4', '5'): {"isMatched": True}, ('5', '6'): {"isMatched": False},('6', '7'): {"isMatched": True},('7', '3'): {"isMatched": False},('7', '8'): {"isMatched": False},('7', '9'): {"isMatched": False}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> prepare_for_algo(G , 1)
    ([], [])

    # more tests for this function display in "find_augmenting_paths"

    """
    nodes_priorities = nx.get_node_attributes(G, "priority")
    nodes_matching = nx.get_node_attributes(G, "isMatched")
    roots = []
    eligible_edges = []
    for node in G.nodes:
        # check if the node in the current priority class and if it doesn't 'touch' the matching yet
        if nodes_priorities[node] == Priority and nodes_matching[node] is False:
            roots.append(node)
            nx.set_node_attributes(
                G,
                {
                    node: {
                        "root": node,
                        "isPositive": True,
                        "isReachable": True,
                        "parent": None,
                        "isExternal": True,
                        "blossomsID": -1,
                    }
                },
            )
        # if not we iniliaze all the relevant attributes
        else:
            nx.set_node_attributes(
                G,
                {
                    node: {
                        "root": None,
                        "isPositive": None,
                        "isReachable": False,
                        "parent": None,
                        "isExternal": True,
                        "blossomsID": -1,
                    }
                },
            )

    # get all incident edges to the root into the eligible_edges list
    for root in roots:
        for neighbor in G.neighbors(root):
            edge = (root, neighbor)
            eligible_edges.append(edge)

    return (eligible_edges, roots)


def find_path(G: nx.Graph, blossoms, u, v, flag):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our find_path is a private function. The function gets graph , blossoms list, u , v and flag and returns the augmenting path in the graph.
    The function differentiates between the second and third conditions in the algorithm

    :param G: nx.Graph , List: blossoms , u: node , v: node , flag : Boolean
    :return: List

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'2': {"parent": '1', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'3': {"parent": '2', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": False, "blossomsID": 'B0'},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": False, "blossomsID": 'B0'},'5': {"parent": '4', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": False, "blossomsID": 'B0'},'6': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": False, "blossomsID": 'B0'},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": False, "blossomsID": 'B0'},'8': {"parent": None, "priority": 1, "isMatched": False, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'9': {"parent": None, "priority": 2, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'10': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'11': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'12': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False}, ('2', '3'): {"isMatched": True}, ('3', '4'): {"isMatched": False},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": True}, ('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False}, ('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> find_path(G,{'B0':{'nodes': ['5','4','3','6','7'], 'root': '1' , 'isPositive': True, 'Base': '3' }},'7','11', True)
    ['1', '2', '3', '6', '7', '11']

    """

    # second condition
    if flag is True:
        path = find_path_to_root(G, blossoms, u, v)
        path.append(v)
        return path
    # flag is False -> third condition
    else:
        first_path = find_path_to_root(G, blossoms, u, v)
        second_path = find_path_to_root(G, blossoms, v, u)
        path = merge_paths(first_path, second_path, u, v)
        return path


def merge_paths(lst1: list, lst2: list, u, v):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our merge_paths is a private function. The function gets two lists and returns a merge list

    :param lst1:List , lst2: List
    :return: List

    Tests:
    >>> lst1 = ['1','2','3','6','7']
    >>> lst2 = ['11','12','10','9','8']
    >>> merge_paths(lst1,lst2, '1','11')
    ['7', '6', '3', '2', '1', '11', '12', '10', '9', '8']
    >>> lst1 = ['a', 'b', 'c']
    >>> lst2 = ['d', 'e', 'f']
    >>> merge_paths(lst1,lst2, 'a', 'd')
    ['c', 'b', 'a', 'd', 'e', 'f']
    >>> lst1 = ['z']
    >>> lst2 = ['y', 'x']
    >>> merge_paths(lst1,lst2, 'z', 'y')
    ['z', 'y', 'x']
    >>> lst1 = ['a', 'b', 'c']
    >>> lst2 = ['a', 'b', 'c']
    >>> merge_paths(lst1,lst2, 'c', 'a')
    ['a', 'b', 'c', 'a', 'b', 'c']
    >>> lst1 = ['1', '3', '5', '7', '9']
    >>> lst2 = ['2', '4', '6', '8', '10']
    >>> merge_paths(lst1,lst2, '1', '2')
    ['9', '7', '5', '3', '1', '2', '4', '6', '8', '10']
    >>> lst1 = ['a', 'b', 'c']
    >>> lst2 = ['d']
    >>> merge_paths(lst1,lst2, 'a' ,'d')
    ['c', 'b', 'a', 'd']
    >>> lst1 = ['a']
    >>> lst2 = ['b']
    >>> merge_paths(lst1, lst2, 'a', 'b')
    ['a', 'b']
    >>> lst1 = ['a', 'b', 'c']
    >>> lst2 = ['a', 'b', 'c']
    >>> merge_paths(lst1,lst2, 'a', 'a')
    ['c', 'b', 'a', 'a', 'b', 'c']
    >>> lst1 = ['a', 'c', 'e', 'g']
    >>> lst2 = ['a', 'c', 'e', 'g']
    >>> merge_paths(lst1,lst2, 'a', 'a')
    ['g', 'e', 'c', 'a', 'a', 'c', 'e', 'g']

    """

    if u == None or v == None or u not in lst1 or v not in lst2:
        raise Exception ("somthing wrong in the arguments")

    list = []
    pos_u = lst1.index(u)
    pos_v = lst2.index(v)
    if pos_u == 0 and pos_v == 0:  
        for i in reversed(lst1):
            list.append(i)
        for j in lst2:
            list.append(j)
    
    elif pos_u == len(lst1) - 1 and pos_v == len(lst2) - 1:
        for i in lst1:
            list.append(i)
        for j in reversed(lst2):
            list.append(j)
    
    
    else:
        if pos_u == 0:
            for j in lst2:
                list.append(j)
            for i in lst1:
                list.append(i)
        else:
            for i in lst1:
                list.append(i)
            for j in lst2:
                list.append(j)
    return list


def find_blossom(G: nx.Graph, blossoms, u, v):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our find_blossom is a private function. The function gets Graph , blossoms list and two nodes and
    returns a new blossom and his key in blossoms list

    :param G:nx.Graph , blossoms: List , u: node , v: node
    :return: Tuple of blossom and String

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'2': {"parent": '1', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'3': {"parent": '2', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1',"isExternal": True, "blossomsID": -1},'5': {"parent": '4', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'6': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isBolssom": False, "isExternal": True, "blossomsID": -1},'8': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'9': {"parent": '8', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'10': {"parent": '9', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'11': {"parent": '10', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'12': {"parent": '11', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8',"isExternal": True, "blossomsID": -1}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False}, ('2', '3'): {"isMatched": True}, ('3', '4'): {"isMatched": False},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": True}, ('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False}, ('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> blossoms = {}
    >>> find_blossom(G,blossoms,'5','7')
    ({'nodes': ['5', '4', '3', '6', '7'], 'root': '1', 'isPositive': True, 'Base': '3'}, 'B0')
    >>> print(len(blossoms))
    1
    >>> external_info = nx.get_node_attributes(G,'isExternal')
    >>> blossoms_id = nx.get_node_attributes(G,'blossomsID')
    >>> print(external_info['5'])
    True
    >>> print(external_info['4'])
    True
    >>> print(external_info['3'])
    True
    >>> print(external_info['6'])
    True
    >>> print(external_info['7'])
    True
    >>> print(blossoms_id['4'])
    -1
    >>> print(blossoms_id['5'])
    -1
    >>> print(blossoms_id['3'])
    -1
    >>> print(blossoms_id['6'])
    -1
    >>> print(blossoms_id['7'])
    -1

    >>> print(external_info['10'])
    True
    >>> print(external_info['11'])
    True
    >>> print(external_info['12'])
    True
    >>> print(blossoms_id['10'])
    -1
    >>> print(blossoms_id['11'])
    -1
    >>> print(blossoms_id['12'])
    -1

    >>> shrink_graph(G,blossoms['B0'],'B0')
    [(False, 'B0'), (False, 'B0'), (False, 'B0'), (False, 'B0'), (False, 'B0')]
    >>> external_info = nx.get_node_attributes(G,'isExternal')
    >>> blossoms_id = nx.get_node_attributes(G,'blossomsID')
    >>> print(external_info['5'])
    False
    >>> print(external_info['4'])
    False
    >>> print(external_info['3'])
    False
    >>> print(external_info['6'])
    False
    >>> print(external_info['7'])
    False
    >>> print(blossoms_id['4'])
    B0
    >>> print(blossoms_id['5'])
    B0
    >>> print(blossoms_id['3'])
    B0
    >>> print(blossoms_id['6'])
    B0
    >>> print(blossoms_id['7'])
    B0

    >>> find_blossom(G,blossoms,'10','12')
    ({'nodes': ['10', '11', '12'], 'root': '8', 'isPositive': True, 'Base': '10'}, 'B1')
    >>> print(len(blossoms))
    2
    >>> shrink_graph(G,blossoms['B1'],'B1')
    [(False, 'B1'), (False, 'B1'), (False, 'B1')]
    >>> external_info = nx.get_node_attributes(G,'isExternal')
    >>> blossoms_id = nx.get_node_attributes(G,'blossomsID')
    >>> print(external_info['10'])
    False
    >>> print(external_info['11'])
    False
    >>> print(external_info['12'])
    False
    >>> print(blossoms_id['10'])
    B1
    >>> print(blossoms_id['11'])
    B1
    >>> print(blossoms_id['12'])
    B1

    """
    isExternal = nx.get_node_attributes(G, "isExternal")
    positive_list = nx.get_node_attributes(G, "isPositive")

    if isExternal[u] == False or isExternal[v] == False:
        return None

    path_to_root_from_u = find_path_to_root(G, blossoms, u, v)
    path_to_root_from_v = find_path_to_root(G, blossoms, v, u)

    common = []
    blossom_list = []
    for item in path_to_root_from_v:
        if item in path_to_root_from_u:
            common.append(item)
        else:
            blossom_list.append(item)

    ancestor = common[-1]
    blossom_list.insert(0, ancestor)
    for item in path_to_root_from_u:
        if item not in path_to_root_from_v:
            blossom_list.insert(0, item)

    blossom_index = len(blossoms)
    key = "B" + str(blossom_index)
    blossoms[key] = {
        "nodes": blossom_list,
        "root": common[0],
        "isPositive": positive_list[ancestor],
        "Base": ancestor,
    }
    return (blossoms[key], key)


def find_path_in_blossom(G: nx.Graph, blossom, flag, u):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our find_path_in_blossom is a private function. The function gets Graph , blossom ,flag (if (u,v) is a matching edge or not, when v
    is the incident node to u and is external to the blossom) and node and returns the path from u to the base and the parent of base


    :param G:nx.Graph blossom: Dictionary , flag: Boolean , u: node
    :return: Tuple of List and String

    Tests:
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": False, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'2': {"parent": None, "priority": 2, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'3': {"parent": '2', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'4': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'5': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'6': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'7': {"parent": None, "priority": 1, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'8': {"parent": None, "priority": 1, "isMatched": False, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'9': {"parent": None, "priority": 2, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isBolssom": False, "isExternal": True, "blossomsID": -1},'10': {"parent": '9', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'11': {"parent": '10', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'12': {"parent": '11', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False}, ('2', '3'): {"isMatched": True}, ('3', '4'): {"isMatched": False},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": True}, ('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False}, ('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> blossom = {'nodes':['5','4','3','6','7'] ,'Base': '3'}
    >>> find_path_in_blossom(G,blossom,False,'7')
    (['7', '6', '3'], '2')

    >>> blossom = {'nodes':['11', '10', '12'] , 'Base': '10'}
    >>> find_path_in_blossom(G,blossom,False,'11')
    (['11', '12', '10'], '9')


    >>> G1 = nx.Graph()
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'2': {"parent": None, "priority": 2, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'3': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '6',"isExternal": False, "blossomsID": 'B0'},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'5': {"parent": '7', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '6',"isExternal": True, "blossomsID": 'B0'},'6': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '6',"isExternal": False, "blossomsID": 'B0'},'8': {"parent": None, "priority": 1, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'9': {"parent": None, "priority": 2, "isMatched": True, "isPositive": False, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'10': {"parent": '12', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '12', "isExternal": False, "blossomsID": 'B1'},'11': {"parent": '10', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '12', "isExternal": False, "blossomsID": 'B1'},'12': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '12', "isExternal": False, "blossomsID": 'B1'}}
    >>> edges_attrs = {('1', '2'): {"isMatched": True}, ('2', '3'): {"isMatched": False}, ('3', '4'): {"isMatched": True},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": False}, ('5', '7'): {"isMatched": True},('6', '7'): {"isMatched": False}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": True}, ('9', '10'): {"isMatched": False},('10', '11'): {"isMatched": True}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": False}}
    >>> G1.add_nodes_from(nodes)
    >>> G1.add_edges_from(edges)
    >>> nx.set_node_attributes(G1, nodes_attrs)
    >>> nx.set_edge_attributes(G1, edges_attrs)
    >>> blossom = {'nodes':['5','4','3','6','7'] ,'Base': '6'}
    >>> find_path_in_blossom(G1,blossom,False,'7')
    (['7', '5', '4', '3', '6'], None)

    >>> blossom = {'nodes':['11','10','12'] ,'Base': '12'}
    >>> find_path_in_blossom(G1,blossom,False,'11')
    (['11', '10', '12'], None)

    """
    matching_info = nx.get_edge_attributes(G, "isMatched")
    parents_info = nx.get_node_attributes(G, "parent")

    paths = paths_to_base(blossom["nodes"], u, blossom["Base"])
    path1 = paths[0]
    path2 = paths[1]
    parent = parents_info[blossom["Base"]]
    # (u,v) is a matching edge
    if flag is True:
        w = path1[1]
        if (u, w) in matching_info:
            if matching_info[(u, w)] is False:
                return (path1, parent)
            else:
                return (path2, parent)

        else:
            if matching_info[(w, u)] is False:
                return (path1, parent)
            else:
                return (path2, parent)

    #  (u,v) is not a matching edge
    else:
        w = path1[1]
        if (u, w) in matching_info:
            if matching_info[(u, w)] is True:
                return (path1, parent)
            else:
                return (path2, parent)

        else:
            if matching_info[(w, u)] is True:
                return (path1, parent)
            else:
                return (path2, parent)


def paths_to_base(list, u, base):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our paths_to_base is a private function. The function gets List , node and base of a bolssom and returns the two possible
    paths from u to the base of the blossom.

    :param list:List , u: node , base: node
    :return: void

    Tests:

    >>> list = ['5','4','3','6','7']
    >>> u = '7'
    >>> base = '3'
    >>> paths_to_base(list,u,base)
    (['7', '5', '4', '3'], ['7', '6', '3'])
    >>> paths_to_base(['5', '4', '3', '6', '7'], '7', '3')
    (['7', '5', '4', '3'], ['7', '6', '3'])
    >>> paths_to_base(['5', '4', '3', '6', '7'], '5', '3')
    (['5', '4', '3'], ['5', '7', '6', '3'])
    >>> paths_to_base(['5', '4', '3', '6', '7'], '4', '3')
    (['4', '3'], ['4', '5', '7', '6', '3'])
    >>> paths_to_base(['1', '2', '3'], '2', '1')
    (['2', '3', '1'], ['2', '1'])
    >>> paths_to_base(['1', '2', '3'], '1', '1')
    (['1'], ['1'])
    >>> paths_to_base(['1', '2', '3'], '3', '1')
    (['3', '1'], ['3', '2', '1'])
    >>> paths_to_base(['1', '2', '3', '4'], '1', '1')
    (['1'], ['1'])
    >>> paths_to_base(['1', '2', '3', '4'], '2', '1')
    (['2', '3', '4', '1'], ['2', '1'])
    >>> paths_to_base(['1', '2', '3', '4'], '3', '1')
    (['3', '4', '1'], ['3', '2', '1'])
    >>> paths_to_base(['1', '2', '3', '4'], '4', '1')
    (['4', '1'], ['4', '3', '2', '1'])
    >>> paths_to_base(['1', '2', '3', '4', '5'], '5', '3')
    (['5', '1', '2', '3'], ['5', '4', '3'])
    """
    path1 = []
    path2 = []
    pos = list.index(u)
    temp = u

    while temp != base:
        path1.append(temp)
        if pos == (len(list) - 1):
            pos = 0
        else:
            pos = pos + 1
        temp = list[pos]
    path1.append(base)
    temp = u
    pos = list.index(u)
    while temp != base:

        path2.append(temp)
        if pos == 0:
            pos = len(list) - 1
        else:
            pos = pos - 1
        temp = list[pos]

    path2.append(base)
    return (path1, path2)


def find_path_to_root(G: nx.Graph, blossoms_list, u, v):
    """
    Programmers: Roi Meshulam and Liroy Melamed

    Our find_path_to_root is a private function. The function gets graph,u,v and the blossoms list and returns the path from u to his tree's root
    while taking into account if (u,v) is a matching edge or not.

    :param G: nx.Graph , List: blossoms , u: node , v: node
    :return: void

    Tests:

    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'2': {"parent": '1', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isExternal": True, "blossomsID": -1},'3': {"parent": '2', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isExternal": False, "blossomsID": 'B0'},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isExternal": False, "blossomsID": 'B0'},'5': {"parent": '4', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isExternal": False, "blossomsID": 'B0'},'6': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '1', "isExternal": False, "blossomsID": 'B0'},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '1', "isExternal": False, "blossomsID": 'B0'},'8': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'9': {"parent": '8', "priority": 2, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8', "isExternal": True, "blossomsID": -1},'10': {"parent": '9', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '8', "isExternal": False, "blossomsID": 'B1'},'11': {"parent": '10', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '8', "isExternal": False, "blossomsID": 'B1'},'12': {"parent": '11', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '8',"isExternal": False, "blossomsID": 'B1'}}
    >>> edges_attrs = {('1', '2'): {"isMatched": False}, ('2', '3'): {"isMatched": True}, ('3', '4'): {"isMatched": False},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": True}, ('5', '7'): {"isMatched": False},('6', '7'): {"isMatched": True}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": False}, ('9', '10'): {"isMatched": True},('10', '11'): {"isMatched": False}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": True}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> find_path_to_root(G,{'B0':{'nodes': ['5','4','3','6','7'], 'root': '1' , 'isPositive': True, 'Base': '3' }},'7','11')
    ['1', '2', '3', '6', '7']

    >>> find_path_to_root(G,{'B1':{'nodes': ['12','11','10'], 'root': '8' , 'isPositive': True, 'Base': '10' }},'11','7')
    ['8', '9', '10', '12', '11']

    # cases when the base's blossom does not have parent and the base is the root in some tree
    >>> G = nx.Graph()
    >>> nodes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    >>> edges = [('1', '2'), ('2', '3'), ('3', '4'),('3','6'), ('4', '5'), ('5', '7'), ('6', '7'), ('7', '11'), ('8', '9'), ('9', '10'),('10','11'),('10','12'),('11','12')]
    >>> nodes_attrs = {'1': {"parent": None, "priority": 1, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'2': {"parent": '1', "priority": 2, "isMatched": False, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'3': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'4': {"parent": '3', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'5': {"parent": '4', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'6': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'7': {"parent": '6', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '6', "isExternal": False, "blossomsID": 'B0'},'8': {"parent": None, "priority": 1, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'9': {"parent": None, "priority": 2, "isMatched": True, "isPositive": None, "isReachable": False,"root": None, "isExternal": True, "blossomsID": -1},'10': {"parent": '12', "priority": 1, "isMatched": True, "isPositive": False, "isReachable": True,"root": '12', "isExternal": False, "blossomsID": 'B1'},'11': {"parent": '10', "priority": 1, "isMatched": True, "isPositive": True, "isReachable": True,"root": '12', "isExternal": False, "blossomsID": 'B1'},'12': {"parent": None, "priority": 1, "isMatched": False, "isPositive": True, "isReachable": True,"root": '12',"isExternal": False, "blossomsID": 'B1'}}
    >>> edges_attrs = {('1', '2'): {"isMatched": True}, ('2', '3'): {"isMatched": False}, ('3', '4'): {"isMatched": True},('3','6'):{"isMatched":False},('4', '5'): {"isMatched": False}, ('5', '7'): {"isMatched": True},('6', '7'): {"isMatched": False}, ('7', '11'): {"isMatched": False},('8', '9'): {"isMatched": True}, ('9', '10'): {"isMatched": False},('10', '11'): {"isMatched": True}, ('10', '12'): {"isMatched": False}, ('11', '12'): {"isMatched": False}}
    >>> G.add_nodes_from(nodes)
    >>> G.add_edges_from(edges)
    >>> nx.set_node_attributes(G, nodes_attrs)
    >>> nx.set_edge_attributes(G, edges_attrs)
    >>> find_path_to_root(G,{'B0':{'nodes': ['5','4','3','6','7'], 'root': '1' , 'isPositive': True, 'Base': '6' }},'7','11')
    ['6', '3', '4', '5', '7']

    >>> find_path_to_root(G,{'B1':{'nodes': ['12','11','10'], 'root': '8' , 'isPositive': True, 'Base': '12' }},'11','7')
    ['12', '10', '11']

    """
    # info
    parents_list = nx.get_node_attributes(G, "parent")
    root_list = nx.get_node_attributes(G, "root")
    external_info = nx.get_node_attributes(G, "isExternal")
    blossoms_info = nx.get_node_attributes(G, "blossomsID")
    matching_info = nx.get_edge_attributes(G, "isMatched")
    # vars
    path: List = []
    temp = u
    prev = v
    # while temp is not the root of the tree
    while root_list[temp] != temp:
        if external_info[temp] is True:
            path.insert(0, temp)
            prev = temp
            temp = parents_list[temp]
        else:
            blossom_id = blossoms_info[temp]
            blossom = blossoms_list[blossom_id]
            if (prev,temp) in matching_info:
                if matching_info[(prev, temp)] is True:
                    blossom_path = find_path_in_blossom(G, blossom, True, temp)
                else:
                    blossom_path = find_path_in_blossom(G, blossom, False, temp)
            else:
                if matching_info[(temp, prev)] is True:
                    blossom_path = find_path_in_blossom(G, blossom, True, temp)
                else:
                    blossom_path = find_path_in_blossom(G, blossom, False, temp)
            for vertex in blossom_path[0]:
                path.insert(0, vertex)
                temp = vertex
            if root_list[temp] == temp:
                return path
            if blossom_path[1] is not None:
                prev = temp
                temp = blossom_path[1]
            



    path.insert(0, root_list[temp])

    return path


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
   

    
