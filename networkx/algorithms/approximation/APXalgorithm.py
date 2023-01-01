import doctest
import logging

import networkx as nx
import hypernetx as hnx
import matplotlib.pyplot as plt

logging.basicConfig(filemode="Logs.log", level=logging.INFO)
log = logging.getLogger()

EPS = 1e-6

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
    # print("Cycles are: ", cycles)
    return cycles


def build_hypergraph_format(cycles):
    i = 0
    buildHype = {}
    for cycle in cycles:
        buildHype[i] = tuple(str(item) for item in cycle)
        i = i + 1
    # print("build hype's format is: ", buildHype)
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

    # print("weight_of_cycle are: ", weight_of_cycles)
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

    # print("weight_cycles are: ", weight_cycles)
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

    # print("edge_labels are: ", edge_labels)
    return edge_labels


def get_undirected_graph_for_independent_weight_set_algo(h, graphL, buildHype, edge_labels):
    num_of_edges = h.number_of_edges()
    count = 0
    for e in h.edges:
        if len(h.edge_neighbors(e)) == 0:
            graphL.add_node(buildHype[e], weight=edge_labels[e])
        for i in h.edge_neighbors(e):
            graphL.add_edge(buildHype[e], buildHype[i])
    # print("GraphL nodes: ", graphL.nodes)
    # print("GraphL edges: ", graphL.edges)
    return graphL


def transform_h_to_g(buildHype, weight_cycles):
    i = 0
    transformHtoG = {}
    for v in buildHype.values():
        transformHtoG[v] = weight_cycles[i]
        i = i + 1
    # print("transformHtoG: ", transformHtoG)
    return transformHtoG


"""recursive heuristic for maximum weighted independent sets
https://github.com/pchervi/Graph-Coloring/blob/295f7bce72885eab05ff50adea746585a2914727/Coloring_MWIS_heuristics.py#L159
@author: Philippe Chervi"""


def exact_MWIS(graph, pi, b_score=0):
    ''' compute mawimum weighted independent set (recursively) using python
    networkx package. Input items are:
    - graph, a networkx graph
    - pi, a dictionary of dual values attached to node (primal constraints)
    - b_score, a bestscore (if non 0, it pruned some final branches)
    It returns:
    - mwis_set, a MWIS as a sorted tuple of nodes
    - mwis_weight, the sum over n in mwis_set of pi[n]'''
    global best_score
    graph_copy = graph.copy()
    # mwis weight is stored as a 'score' graph attribute
    graph_copy.graph['score'] = 0
    best_score = b_score

    def get_mwis(G):
        '''compute mawimum weighted independent set (recursively) for non
        yet computed sets. Input is a networkx graph, output is the
        exact MWIS set of nodes and its weight.
        Based on "A column generation approach for graph coloring" from
        Mehrotra and Trick, 1995, using recursion formula:
        MWIS(G union {i}) = max(MWIS(G), MWIS({i} union AN(i)) where
        AN(i) is the anti-neighbor set of node i'''
        global best_score
        # score stores the best score along the path explored so far
        key = tuple(sorted(G.nodes()))
        ub = sum(pi[n] for n in G.nodes())
        score = G.graph['score']
        # if graph is composed of singletons, leave now
        if G.number_of_edges == 0:
            if score + ub > best_score + EPS:
                best_score = score + ub
            return key, ub
        # compute highest priority node (used in recursion to choose {i})
        node_iter = ((n, deg * pi[n]) for (n, deg) in G.degree())
        node_chosen, _ = max(node_iter, key=lambda x: x[1])
        pi_chosen = pi[node_chosen]
        node_chosen_neighbors = list(G[node_chosen])
        pi_neighbors = sum(pi[n] for n in node_chosen_neighbors)
        G.remove_node(node_chosen)
        # Gh = G - {node_chosen} union {anti-neighbors{node-chosen}}
        # For Gh, ub decreases by value of pi over neighbors of {node_chosen}
        # and value of pi over {node_chosen} as node_chosen is disconnected
        # For Gh, score increases by value of pi over {node_chosen}
        Gh = G.copy()
        Gh.remove_nodes_from(node_chosen_neighbors)
        mwis_set_h, mwis_weight_h = tuple(), 0
        if Gh:
            ubh = ub - pi_neighbors - pi_chosen
            if score + pi_chosen + ubh > best_score + EPS:
                Gh.graph['score'] += pi_chosen
                mwis_set_h, mwis_weight_h = get_mwis(Gh)
            del Gh
        mwis_set_h += (node_chosen,)
        mwis_weight_h += pi_chosen
        # Gp = G - {node_chosen}
        # For Gp, ub decreases by value of pi over {node_chosen}
        # For Gh, score does not increase
        mwis_set_p, mwis_weight_p = tuple(), 0
        if G:
            ubp = ub - pi_chosen
            if score + ubp > best_score + EPS:
                mwis_set_p, mwis_weight_p = get_mwis(G)
            del G
        # select case with maximum score
        if mwis_set_p and mwis_weight_p > mwis_weight_h + EPS:
            mwis_set, mwis_weight = mwis_set_p, mwis_weight_p
        else:
            mwis_set, mwis_weight = mwis_set_h, mwis_weight_h
        # increase score
        score += mwis_weight
        if score > best_score + EPS:
            best_score = score
        # return set and weight
        key = sorted(mwis_set)
        return key, mwis_weight

    return get_mwis(graph_copy)


def Maximum_weight_cycle_packing_approximation_algorithm(graph: nx.DiGraph, k: int):
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
    >>> print(Maximum_weight_cycle_packing_approximation_algorithm(Digraph, 3))
    [('1', '8', '2'), ('5', '7', '6')]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> print(Maximum_weight_cycle_packing_approximation_algorithm(Digraph, 2))
    [('3', '4')]
    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> print(Maximum_weight_cycle_packing_approximation_algorithm(Digraph, 2))
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
    # find cycles in graph
    cycles = find_cycles(graph, k)

    # create hypergraph according to hypergraph's format
    buildHype = build_hypergraph_format(cycles)
    h = hnx.Hypergraph(buildHype)
    # print(h)

    # get weights of cycles to implement on hypergrap's edges weights:
    weight_of_cycles = get_weights_of_cycles(graph, cycles)
    # print("weight_of_cycles: ", weight_of_cycles)

    # find weights of each cycle in the graph! :*****
    weight_cycles = weights_of_each_cycle(weight_of_cycles)
    # print("weight_cycles: ", weight_cycles)

    # set weights to each hypergraph's edge
    edge_labels = set_weights_to_hypergarphs_edges(h, weight_cycles)
    # print("edge_labels: ", edge_labels)

    # draw hypergraph h
    hnx.draw(h, edge_labels=edge_labels)
    plt.title('HyperGraph')
    plt.show()

    # create a new graph for maximum weight independent set algorithm
    graphL = nx.Graph()
    graphL = get_undirected_graph_for_independent_weight_set_algo(h, graphL, buildHype,
                                                                  edge_labels)
    # print("GraphL nodes: ", graphL.nodes)
    # print("GraphL edges: ", graphL.edges)

    # draw undirected graphL
    nx.draw(graphL, pos=nx.spring_layout(graphL), font_size=12, with_labels=True)
    plt.title('graphL')
    plt.show()

    # Get all edges of H and weights
    transformHtoG = transform_h_to_g(buildHype, weight_cycles)
    # print("transformHtoG: ", transformHtoG)

    if len(transformHtoG) == 0:
        return []

    # find maximum weight independent set
    pi = dict(zip(graphL.nodes(), (transformHtoG[i] for i in transformHtoG.keys())))
    mwis_set, mwis_weight = set(), 0
    mwis_set, mwis_weight = exact_MWIS(graphL, pi, 0)
    return mwis_set


if __name__ == '__main__':
    print(doctest.testmod())
    # graph1 = nx.DiGraph()
    # graph1.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    # graph1.add_weighted_edges_from(
    #     [(1, 8, 2), (8, 1, 4), (2, 1, 5), (1, 3, 4), (3, 8, 2), (8, 2, 3), (8, 5, 4), (5, 7, 3), (7, 6, 2), (6, 5, 4)])
    # print(Maximum_weight_cycle_packing_approximation_algorithm(graph1, 3))
