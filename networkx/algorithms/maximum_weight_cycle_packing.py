import doctest

import networkx as nx
from networkx.algorithms.simple_cycles_le_k import simple_cycles_le_k

"""REUT HADAD & TAL SOMECH
This is an implementation for two different algorithms described on "MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,
WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS" article.
The article points on two algorithms that solves kidney exchange problems, which can be modelled as cycle packing
problems in a directed graph, involving cycles of length 2, 3, or even longer.
In the article we focus on the maximal exchange of cycles of size 2 and 3 vertices, we demonstrate an approximation
algorithm and an exact algorithm for this problem.
"""
"""article title: MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS
authors:Biro, P. and Manlove, D.F. and Rizzi, R.
year:(2009)
link:http://eprints.gla.ac.uk/25732/
"""


def maximum_weight_cycle_packing(graph: nx.DiGraph, k: int) -> list:
    """Algorithm - the algorithm finds the exact maximum weight k-way exchanges using reduction from directed graph to
    non-directed graph "Algorithm 2 - Exact algorithm for kidney exchange programs" by Biro, P. and Manlove,
    D.F. and Rizzi, R. Returns the list of max weighted exchanges of directed weighted graph 'G' A directed weighted
    graph is a graph in which every edge is one-sided and weighted for example an edge from node 1->2 with a weight
    of 5,a k-way exchange is a cycle within a graph containing at most k nodes. max weighted exchange is a cycle
    with the most weighted edges from every node in the cycle
    Parameters
      G : NetworkX DiGraph Directed graph with weights
     Returns
     Lst: list of lists Each list in lst contaning the nodes which make up the
    cycle with the highest weights sum

        Notes
    -----------
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from directed graph to not directed graph by
    the algorithm in the published article Exact-complete algorithm for kidney exchange programs"
    Refrences
    ----------
    Algorithm 1 - 'MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS, WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS' by Biro, P. and Manlove, D.F. and Rizzi, R. http://eprints.gla.ac.uk/25732/


     Examples -----------
     >>> Digraph=nx.DiGraph()
     >>> Digraph.add_nodes_from([1,2,3,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> print(len(maximum_weight_cycle_packing(Digraph,3))) #[1,8,2] [6,5,7] [1,3,8] ,
    2
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(len(maximum_weight_cycle_packing(Digraph,2)))#[3,4] or [4,3]
    1
    >>> graphEX3 = nx.DiGraph()
    >>> graphEX3.add_nodes_from([10,11,12,13,14,15,16])
    >>> Digraph.add_weighted_edges_from([(10,11,10),(11,12,5),(12,13,6),(13,10,4),(11,14,2),(14,16,3),(16,15,8),(15,14,6)])
    >>> print(maximum_weight_cycle_packing(graphEX3, 3))
    []
    """

    Ys = create_Ys(graph, k)

    max_cycles = []
    max_weight = 0
    max_graph = nx.Graph()
    for Y in Ys:
        X = []
        seen_Y = set()
        ans_graph = nx.Graph()
        #   creating the nodes in the graph
        #   adding the nodes in the graph
        for edge in Y:
            ans_graph.add_node((edge[0], edge[1]))
            seen_Y.add(edge[0])
            seen_Y.add(edge[1])
        for edge in graph.edges:
            if edge[0] not in seen_Y and edge[0] not in X:
                X.append(edge[0])
                ans_graph.add_node(edge[0])
        connect_2cycles(X, graph, ans_graph)
        if k > 2:
            connect_3cycles(X, Y, graph, ans_graph)
        exchanges = list(nx.max_weight_matching(ans_graph))
        if (
            len(exchanges) == 0 and ans_graph.number_of_edges() == 1
        ):  # for the use-case of only self connected edge
            exchanges = [list(ans_graph.edges)[0]]
        temp_max = 0
        for cyc in exchanges:
            temp_max = temp_max + ans_graph.get_edge_data(cyc[0], cyc[1])["weight"]
        if temp_max > max_weight:
            max_weight = temp_max
            max_cycles = exchanges
            max_graph = ans_graph.copy()

    result = []  # exctract only the cycles
    for cyc in max_cycles:
        cycle = max_graph.get_edge_data(cyc[0], cyc[1])["cycle"]
        result.append(cycle)

    return result  # exchanges


def connect_2cycles(X, graph, ans_graph):
    for i in range(
        len(X)
    ):  # creating the edges in the graph by going through the 2-cycles
        for j in range(i + 1, len(X)):
            if (X[i], X[j]) in graph.edges and (X[j], X[i]) in graph.edges:
                weight = (
                    graph.get_edge_data(X[i], X[j])["weight"]
                    + graph.get_edge_data(X[j], X[i])["weight"]
                )
                ans_graph.add_edge((X[i]), (X[j]), weight=weight, cycle=[X[i], X[j]])


def connect_3cycles(X, Y, graph, ans_graph):
    #   creating the edges in the graph by going through the 3-cycles
    for k in range(len(X)):
        for j, l in Y:  # This deals with the normal case of Yi,j Xk
            if (l, X[k]) in graph.edges and (X[k], j) in graph.edges:
                weight = (
                    graph.get_edge_data(j, l)["weight"]
                    + graph.get_edge_data(l, X[k])["weight"]
                    + graph.get_edge_data(X[k], j)["weight"]
                )
                ans_graph.add_edge((X[k]), (j, l), weight=weight, cycle=[j, l, X[k]])


def check_independent(temp):
    """This function is used to check if a list of edges are independent set
    >>> check_independent([(2,3),(1,4),(5,7)])
    True
    >>> check_independent([(2,3),(1,4),(5,1)])
    False
    """
    nodes_seen = []
    for cyc in temp:
        for node in cyc:
            if node in nodes_seen:
                return False
            nodes_seen.append(node)
    return True


def create_Ys(graph, k):
    """This function is used to create the cartesian product of the 3-cycles
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> Ys=create_Ys(Digraph,3)
    >>> print(((len(Ys)==6 ) or (len(Ys) == 8))) #- the known product is supposed to be composed of 27 permutation
    True
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(len(create_Ys(Digraph,3))) #- the known product is supposed to be composed of 1 permutation
    2
    """

    import itertools
    import random

    import numpy as np

    temp_cycles = simple_cycles_le_k(graph, k)
    cycles = []
    for cycle in temp_cycles:
        if len(cycle) == k:
            cycles.append(cycle)

    perm_arr = np.ndarray(shape=(len(cycles), k), dtype=list)
    for cyc_idx in range(len(cycles)):
        cyc = cycles[cyc_idx]
        for ed_idx in range(len(cyc)):
            mid = (cyc[ed_idx], cyc[(ed_idx + 1) % len(cyc)])
            perm_arr[cyc_idx][ed_idx] = mid
    S = set()
    for cyc in perm_arr:
        S.add(cyc[0])
    Ys = []
    for i in range(len(S) + 1):

        for temp in itertools.combinations(S, i):
            temp = list(temp)
            if check_independent(temp):
                Ys.append(temp)

    return Ys


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print(doctest.testmod())
