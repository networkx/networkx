import doctest
import networkx as nx
import hypernetx as hnx
import matplotlib.pyplot as plt
from networkx import maximal_independent_set

from dwave_networkx import maximum_weighted_independent_set, get_default_sampler, maximum_weighted_independent_set_qubo
from dwave_networkx.examples.max_independent_set import sampler

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


def find_cycles(graph, k):
    temp_cycles = nx.recursive_simple_cycles(graph)
    cycles = []
    for cycle in temp_cycles:
        if len(cycle) == k and k == 2:
            cycles.append(cycle)
        if (len(cycle) == k or len(cycle) == k - 1) and k == 3:
            cycles.append(cycle)
    print("Cycles are: ", cycles)
    return cycles


def build_hypergraph_format(cycles):
    i = 0
    buildHype = {}
    for cycle in cycles:
        buildHype[i] = tuple(str(item) for item in cycle)
        i = i + 1
    print("build hype's format is: ", buildHype)
    return buildHype


def get_weights_of_cycles(graph, cycles):
    weight_of_cycles = {}
    for cycle in cycles:
        if len(cycle) < 3:
            list_of_strings = [str(graph.get_edge_data(cycle[0], cycle[1])),
                               str(graph.get_edge_data(cycle[1], cycle[0]))]
            weight_of_cycles[tuple(cycle)] = ''.join(list_of_strings)
        else:
            list_of_strings = [str(graph.get_edge_data(cycle[0], cycle[1])),
                               str(graph.get_edge_data(cycle[1], cycle[2])),
                               str(graph.get_edge_data(cycle[2], cycle[0]))]
            weight_of_cycles[tuple(cycle)] = ''.join(list_of_strings)

    print("weight_of_cycle are: ", weight_of_cycles)
    return weight_of_cycles


def weights_of_each_cycle(weight_of_cycles):
    weight_cycles = []
    temp = "0"
    for weight_of_cycle in weight_of_cycles.values():
        sum_weights = 0
        for ch in weight_of_cycle:
            if ch.isdigit():
                temp += ch
            else:
                sum_weights += int(temp)
                temp = "0"
        weight_cycles.append(sum_weights + int(temp))

    print("weight_cycles are: ", weight_cycles)
    return weight_cycles


def set_weights_to_hypergarphs_edges(h, weight_cycles):
    i = 0
    edge_labels = {}
    for e in h.edges:
        try:
            h.edges[e].weight = weight_cycles[i]
            edge_labels[e] = weight_cycles[i]
            i = i + 1
        except:
            w = 2
            # add unit weight if none to simplify other functions
            h.edges[e].weight = weight_cycles[i]
            edge_labels[e] = weight_cycles[i]
            i = i + 1

    print("edge_labels are: ", edge_labels)
    return edge_labels


def get_undirected_graph_for_independent_weight_set_algo(h, weight_of_cycles, neighbours, graphL, buildHype,
                                                         edge_labels):
    num_of_edges = h.number_of_edges()
    for val in weight_of_cycles.keys():
        neighbours.append(val)
    print(neighbours)
    count = 0
    for e in h.edges:
        if count < num_of_edges:
            if len(h.edge_neighbors(e)) == 0:
                graphL.add_node(buildHype[e], weight=edge_labels[e])
            for i in h.edge_neighbors(e):
                graphL.add_edge(buildHype[e], buildHype[i])
    print("GraphL nodes: ", graphL.nodes)
    print("GraphL edges: ", graphL.edges)
    return graphL


def transform_h_to_g(buildHype, weight_cycles):
    i = 0
    transformHtoG = {}
    for v in buildHype.values():
        transformHtoG[v] = weight_cycles[i]
        i = i + 1
    print("transformHtoG: ", transformHtoG)
    return transformHtoG


def APXalgorithm(graph: nx.DiGraph, epsilon, k: int) -> dict:
    """
    "
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
    >>> print(APXalgorithm(Digraph,3))
    [[5,6,7],[1,8,2]]||[[5,6,7],[1,3,8]]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(APXalgorithm(Digraph))
    [3,4]
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> print(APXalgorithm(Digraph,2))
    []
    Notes
    -----------
    Algorithm - the algorithm finds maximum weight k-way exchanges using reduction from graph to hyper-graph by
    the algorithm in the published article APX-complete algorithm for kidney exchange programs"

    Refrences
    ----------
    Algorithm 1 - 'MAXIMUM WEIGHT CYCLE PACKING IN DIRECTED GRAPHS, WITH APPLICATION TO KIDNEY EXCHANGE PROGRAMS' by Biro, P. and Manlove, D.F. and Rizzi, R. http://eprints.gla.ac.uk/25732/
    :param k:  num of circles size
    :param epsilon: Level of accuracy
    :param graph: graph that simulates donors-Patients for kidney exchange programs.

    """
    accu_level = k - 1 + epsilon
    print("accu level is: ", accu_level)
    # find cycles in graph
    cycles = find_cycles(graph, k)

    # create hypergraph according to hypergraph's format
    buildHype = build_hypergraph_format(cycles)
    h = hnx.Hypergraph(buildHype)

    # add weights of cycles to implement on hypergrap's edges weights:
    weight_of_cycles = get_weights_of_cycles(graph, cycles)

    # find weights of each cycle in the graph! :*****
    weight_cycles = weights_of_each_cycle(weight_of_cycles)

    # set weights to each hypergraph's edge
    edge_labels = set_weights_to_hypergarphs_edges(h, weight_cycles)

    # draw hypergraph h
    hnx.draw(h, edge_labels=edge_labels)
    print(h)
    plt.title('HyperGraph')
    plt.show()

    # create a new graph for maximum weight independent set algorithm
    neighbours = []
    graphL = nx.Graph()
    graphL = get_undirected_graph_for_independent_weight_set_algo(h, weight_of_cycles, neighbours, graphL, buildHype,
                                                                  edge_labels)

    # draw undirected graphL
    nx.draw(graphL, pos=nx.spring_layout(graphL), font_size=12, with_labels=True)
    plt.title('graphL')
    plt.show()

    # Get all edges of H and weights
    transformHtoG = transform_h_to_g(buildHype, weight_cycles)

    print("neighbours are: ", neighbours)

    # find maximum weight independent set
    maximal_set = {}
    print("maximal_independent_set of nodes: ", maximal_independent_set(graphL))
    for n in maximal_independent_set(graphL):
        maximal_set[n] = transformHtoG[n]

    return maximal_set


if __name__ == '__main__':
    graph1 = nx.DiGraph()
    graph1.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    graph1.add_weighted_edges_from(
        [(1, 8, 2), (8, 1, 4), (2, 1, 5), (1, 3, 4), (3, 8, 2), (8, 2, 3), (8, 5, 4), (5, 7, 3), (7, 6, 2), (6, 5, 4)])
    print(APXalgorithm(graph1, 0.1, 3))
