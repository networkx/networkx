import doctest
import itertools

import networkx as nx
from itertools import permutations, product
import numpy as np
from more_itertools import distinct_permutations as idp
import matplotlib.pyplot as plt
"""REUT HADAD & TAL SOMECH"""

"""
This is an implementation for two different algorithms described on "MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,
WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS" article.
The article points on two algorithms that solves kidney exchange problems, which can be modelled as cycle packing
problems in a directed graph, involving cycles of length 2, 3, or even longer.
In the article we focus on the maximal exchange of circles of size 2 and 3 vertices, we demonstrate an approximation
algorithm and an exact algorithm for this problem.
"""
"""article title: MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS,WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS
authors:Biro, P. and Manlove, D.F. and Rizzi, R.
year:(2009)
link:http://eprints.gla.ac.uk/25732/
"""


def ExactAlgorithm(graph: nx.DiGraph, k: int) -> list:
    """
    Algorithm - the algorithm finds the exact maximum weight k-way exchanges using reduction from directed graph to non directed
    graph
    "Algorithm 2 - Exact algorithm for kidney exchange programs" by Biro, P. and Manlove, D.F. and Rizzi, R.
    Returns the list of max weighted exchanges of directed weighted graph 'G'

    A directed weighted graph is a graph in which every edge is one sided and weighted
    for example an edge from node 1->2 with a weight of 5,an k-way exchange
    is a circle within a graph containing at most k nodes.
    max weighted exchange is a circle with the most weighted edges from every node in the circle

    Parameters
    -----------
    G : NetworkX DiGraph
        Directed graph with weights

    Returns
    -----------
    Lst: list of lists
        Each list in lst contaning the nodes which make up the circle with the highest weights sum
    Examples
    -----------


    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> print(ExactAlgorithm(Digraph,3))
    [[5,6,7],[1,8,2]]||[[5,6,7],[1,3,8]]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(ExactAlgorithm(Digraph,3))
    [3,4]
    >>> graphEX3 = nx.DiGraph()
    >>> graphEX3.add_nodes_from([10,11,12,13,14,15,16])
    >>> Digraph.add_weighted_edges_from([(10,11,10),(11,12,5),(12,13,6),(13,10,4),(11,14,2),(14,16,3),(16,15,8),(15,14,6)])
    >>> print(ExactAlgorithm(graphEX3, 2))
    []
    Notes
    -----------
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from directed graph to not directed graph by
    the algorithm in the published article Exact-complete algorithm for kidney exchange programs"
    Refrences
    ----------
    Algorithm 1 - 'MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS, WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS' by Biro, P. and Manlove, D.F. and Rizzi, R. http://eprints.gla.ac.uk/25732/
    """
    temp_cycles = nx.recursive_simple_cycles(graph)
    cycles = []
    for cycle in temp_cycles:
        if len(cycle) == k:
            cycles.append(cycle)
    Ys = create_Ys(cycles, k)

    X = []
    for Y in Ys:
        ans_graph = nx.Graph()

        for edge in graph.edges:
            if edge in Y:
                ans_graph.add_node(f"Y{edge[0]},{edge[1]}")
            else:
                if edge[0] not in X:
                    X.append(edge[0])
                ans_graph.add_node(f"X{edge[0]}")

        for i in range(len(X)):
            for edge in Y:
                if X[i] in edge:
                    ans_graph.add_edge(f"X{X[i]}",f"Y{edge[0]},{edge[1]}")
            for j in range(i + 1, len(X)):
                if (X[i], X[j]) in graph.edges and (X[j], X[i]) in graph.edges:
                    t = 5
                    weight = graph.get_edge_data(X[i], X[j])["weight"] + graph.get_edge_data(X[j], X[i])["weight"]
                    ans_graph.add_edge(f"X{X[i]}", f"X{X[j]}", weight=weight)

        for k in range(len(X)):
            for j,l in Y:
                if [j, l, X[k]] in cycles:  # j == X[i] and (l, X[k]) in graph.edges and (X[k], X[i]) in graph.edges:
                    weight = graph.get_edge_data(j, l)["weight"] + graph.get_edge_data(l, X[k])["weight"] + \
                             graph.get_edge_data(X[k], j)["weight"]
                    ans_graph.add_edge(f"X{X[k]}", f"Y{j},{l}", weight=weight)
        components = [ans_graph.subgraph(c).copy() for c in nx.connected_components(ans_graph)]
        exchanges=[]
        for comp in components:
            exchanges.append(sorted(comp.edges(data=True), key=lambda t: t[2].get('weight', 1),reverse=True)[0])
        return exchanges


def create_Ys(cycles, k):
    arr2 = np.ndarray(shape=(len(cycles),k), dtype=list)
    for cyc_idx in range(len(cycles)):
        cyc = cycles[cyc_idx]
        for ed_idx in range(len(cyc)):
            mid = (cyc[ed_idx], cyc[(ed_idx + 1) % len(cyc)])
            arr2[cyc_idx][ed_idx] = mid
    temp=arr2[0]
    for i in range(1,len(arr2)):
        k=np.ndarray(list(temp))
        temp=itertools.product(temp,arr2[i])
    return list(temp) #[[i, j, k] for i in arr2[0] for j in arr2[1] for k in arr2[2]]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # itertools.ne
    Digraph = nx.DiGraph()
    Digraph.add_nodes_from([1, 2, 3, 5, 6, 7, 8])
    Digraph.add_weighted_edges_from(
        [(1, 8, 2), (8, 1, 4), (2, 1, 5), (1, 3, 4), (3, 8, 2), (8, 2, 3), (8, 5, 4), (5, 7, 3), (7, 6, 2), (6, 5, 4)])
    # t = Digraph.edges
    # Digraph =nx.DiGraph()
    # Digraph.add_nodes_from([1,2,3,4])
    # Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    # nx.draw_shell(ExactAlgorithm(Digraph, 3))
    # plt.show()
    print(ExactAlgorithm(Digraph, 3))
    # # for b in permutations([Dx[0:3],Dx[3:6],Dx[6:9]]):
    #     print(b)
    # print_hi('PyCharm')
    # print(permutations([1, 2, 3],2))
    # for i in idp([1, 2, 3], 2):
    #     print(i)
    # get_pem()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
