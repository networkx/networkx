import doctest

import networkx as nx
import numpy as np
from networkx.algorithms import cycles

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


def maximum_weight_cycle_packing(graph: nx.DiGraph, k: int) -> list:
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
    >>> print(len(maximum_weight_cycle_packing(Digraph,3))) #[1,8,2] [6,5,7] [1,3,8] , can be only 2 but in any order
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

    Notes
    -----------
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from directed graph to not directed graph by
    the algorithm in the published article Exact-complete algorithm for kidney exchange programs"
    Refrences
    ----------
    Algorithm 1 - 'MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS, WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS' by Biro, P. and Manlove, D.F. and Rizzi, R. http://eprints.gla.ac.uk/25732/
    """

    Ys,cycles = create_Ys(graph,k)

    X = []
    max_cycles=[]
    max_weight=0
    for Y in Ys:
        ans_graph = nx.Graph()
        #   creating the nodes in the graph graph
        for edge in graph.edges:
            if edge in Y:
                ans_graph.add_node(f"Y{edge[0]},{edge[1]}")
            else:
                if edge[0] not in X:
                    X.append(edge[0])
                ans_graph.add_node(f"X{edge[0]}")

        for i in range(len(X)):  # creating the edges in the graph by going through the 2-circles
            for j in range(i + 1, len(X)):
                if (X[i], X[j]) in graph.edges and (X[j], X[i]) in graph.edges:
                    weight = graph.get_edge_data(X[i], X[j])["weight"] + graph.get_edge_data(X[j], X[i])["weight"]
                    ans_graph.add_edge(f"X{X[i]}", f"X{X[j]}", weight=weight, cycle=[X[i], X[j]])

        #   creating the edges in the graph by going through the 3-circles
        for k in range(len(X)):
            for j, l in Y:  # This deals with the normal case of Yi,j Xk
                if [j, l, X[k]] in cycles:
                    weight = graph.get_edge_data(j, l)["weight"] + graph.get_edge_data(l, X[k])["weight"] + \
                             graph.get_edge_data(X[k], j)["weight"]
                    ans_graph.add_edge(f"X{X[k]}", f"Y{j},{l}", weight=weight, cycle=[j, l, X[k]])
        exchanges = list(nx.max_weight_matching(ans_graph))
        to_remove = set()
        # now in this use-case we iterate over all the matching which we got back
        # and we want to remove the ones with the same node , like (X8,Y1,3),(Y1,8,X2)
        # by also preserving the highest weighted cycle
        for i in range(len(exchanges)):
            nodes_1 = [exchanges[i][0][1:], exchanges[i][1][1:]]
            for j in range(i + 1, len(exchanges)):
                nodes_2 = [exchanges[j][0][1:], exchanges[j][1][1:]]
                for node in nodes_2:
                    if node in nodes_1[0] or node in nodes_1[1] or nodes_1[0] in node or nodes_1[1] in node:
                        ed1 = ans_graph.get_edge_data(*exchanges[i])
                        ed2 = ans_graph.get_edge_data(*exchanges[j])
                        if ed1["weight"] > ed2["weight"]:
                            to_remove.add(exchanges[j])
                        else:
                            to_remove.add(exchanges[i])
        if len(to_remove) > 0:
            exchanges.remove(*to_remove)
        #   This next part is used to get the max exchange.
        temp_max=0
        for cyc in exchanges:
            #ed=ans_graph.get_edge_data(cyc[0],cyc[1])["weight"]
            temp_max=temp_max+ans_graph.get_edge_data(cyc[0],cyc[1])["weight"]
        if temp_max>max_weight:
            max_weight=temp_max
            max_cycles=exchanges
    # This last part is only for pretty printing and showing , instead of [('X8','Y1,2')] becomes [1,2,8]

    result = []
    for cyc in max_cycles:
        temp = []
        for node in cyc:
            if node[0] == 'Y':
                node1, node2 = node[1:].split(',')
                temp.append(int(node1))
                temp.append(int(node2))
            else:
                temp.append(int(node[1:]))
        result.append(temp)

    return result  # exchanges


def create_Ys(graph,k):
    """This function is used to create the cartesian product of the 3-cycles
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> Ys,_=create_Ys(Digraph,3)
    >>> print(len(Ys)) #- the known product is supposed to be composed of 27 permutation
    27
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(len(create_Ys(Digraph,3))) #- the known product is supposed to be composed of 1 permutation
    2
    """
    temp_cycles = nx.recursive_simple_cycles(graph)
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
    mesh=[]
    if len(perm_arr)>0:
        mesh = np.array(np.meshgrid(*perm_arr))
        mesh = mesh.T.reshape(-1, len(mesh))

    return mesh,cycles


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # itertools.ne
    doctest.testmod()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
