import doctest
import logging

import re
import networkx as nx
import hypernetx as hnx
import matplotlib.pyplot as plt

# logging.basicConfig(filemode="Logs.log", level=logging.INFO)
# log = logging.getLogger()
from hypernetx import Entity

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
    ['[5, 7, 6]', '[8, 2, 1]']
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    >>> Digraph.add_weighted_edges_from([(1, 6, 11), (6, 1, 10), (1, 5, 3), (5, 1, 2), (8, 9, 11), (9, 8, 20), (3, 2, 6), (2, 6, 5), (6, 3, 8),(5, 7, 6), (7, 4, 11), (4, 5, 5), (10, 16, 1), (16, 11, 10), (11, 15, 3), (15, 11, 2), (18, 19, 11),(19, 18, 20), (13, 12, 6), (12, 16, 5), (16, 13, 8)])
    >>> print(Maximum_weight_cycle_packing_approximation_algorithm(Digraph, 2))
    ['[1, 6]', '[11, 15]', '[18, 19]', '[8, 9]']
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
    :param graph: graph that simulates donors-Patients for kidney exchange programs.

    """
    logging.info("Finds cycles of size k in graph")
    cycles = find_cycles_of_size_k(graph, k)

    if len(cycles) == 0:
        return []

    logging.info("create hypergraph according to hypergraph's format of hypernetx library - "
                 "https://pnnl.github.io/HyperNetX/build/classes/classes.html")
    buildHype = {}
    weights = {}
    i = 0
    for cycle in cycles:
        if len(cycle) < 3:
            weight = graph.get_edge_data(cycle[0], cycle[1])["weight"] + graph.get_edge_data(cycle[1], cycle[0])[
                "weight"]
        else:
            weight = graph.get_edge_data(cycle[0], cycle[1])["weight"] + graph.get_edge_data(cycle[1], cycle[2])[
                "weight"] + graph.get_edge_data(cycle[2], cycle[0])["weight"]
        buildHype[i] = Entity(i, tuple(str(item) for item in cycle), weight=weight)
        weights[i] = weight
        i = i + 1
    h = hnx.Hypergraph(buildHype)

    # logging.info("draw hypergraph h")
    # hnx.draw(h, edge_labels=weights)
    # plt.title('HyperGraph')
    # plt.show()

    logging.info("create a new graph for maximum weight independent set algorithm")
    graphL = nx.Graph()
    for e in h.edges:
        if len(h.edge_neighbors(e)) == 0:
            graphL.add_node(str(cycles[e]), weight=weights[e])
        for i in h.edge_neighbors(e):
            graphL.add_edge(str(cycles[e]), str(cycles[i]))

    # logging.info("draw undirected graphL")
    # nx.draw(graphL, pos=nx.spring_layout(graphL), font_size=12, with_labels=True)
    # plt.title('graphL')
    # plt.show()

    logging.info("nodes and weights")
    pi = dict(zip(graphL.nodes(), (weights[i] for i in weights)))

    logging.info("find maximum weight independent set")
    mwis_set, mwis_weight = MWIS(graphL, pi, 0)
    return mwis_set


def simple_cycles(graph, k):
    subG = type(graph)(graph.edges())
    ccs = list(nx.strongly_connected_components(subG))
    while ccs:
        scc = ccs.pop()
        startnode = scc.pop()
        path = [startnode]
        blocked = set()
        blocked.add(startnode)
        stack = [(startnode, list(subG[startnode]))]

        while stack:
            thisnode, nbrs = stack[-1]

            if nbrs and len(path) <= k:
                nextnode = nbrs.pop()
                if nextnode == startnode:
                    yield path[:]
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append((nextnode, list(subG[nextnode])))
                    blocked.add(nextnode)
                    continue
            if not nbrs or len(path) >= k:
                blocked.remove(thisnode)
                stack.pop()
                path.pop()
        subG.remove_node(startnode)
        H = subG.subgraph(scc)
        ccs.extend(nx.strongly_connected_components(H))


def find_cycles_of_size_k(graph, k):
    """finds relevent cycles according to chosen K
       Parameters
       -----------
       :param graph : NetworkX DiGraph
           Directed graph with weights
       :param k : size of cycles (according to article - max size is 3 and min size is 2)
       Returns
       -----------
       cycles: cycles on graph according to chosen K
       Examples
       -----------
       >>> Digraph=nx.DiGraph()
       >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
       >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
       >>> print(find_cycles_of_size_k(Digraph, 3))
       [[8, 2, 1], [8, 1, 3], [8, 1], [5, 7, 6]]
       >>> Digraph =nx.DiGraph()
       >>> Digraph.add_nodes_from([1,2,3,4])
       >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
       >>> print(find_cycles_of_size_k(Digraph, 2))
       [[3, 4]]
       >>> Digraph=nx.DiGraph()
       >>> Digraph.add_nodes_from([1,2,3,4,5,6,7,8])
       >>> Digraph.add_weighted_edges_from([(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
       >>> print(find_cycles_of_size_k(Digraph, 2))
       []
       """
    sc = simple_cycles(graph, k)
    cycles = []
    for cycle in sc:
        if len(cycle) == k and k == 2:
            cycles.append(cycle)
        if (len(cycle) == k or len(cycle) == k - 1) and k == 3:
            cycles.append(cycle)
    return cycles


"""recursive heuristic for maximum weighted independent sets
https://github.com/pchervi/Graph-Coloring/blob/295f7bce72885eab05ff50adea746585a2914727/Coloring_MWIS_heuristics.py#L159
@author: Philippe Chervi"""


def MWIS(graph, pi, b_score=0):
    """ compute mawimum weighted independent set (recursively) using python
    networkx package. Input items are:
    :param graph, a networkx graph
    :param pi, a dictionary of dual values attached to node (primal constraints)
    :param b_score, a bestscore (if non 0, it pruned some final branches)
    It returns:
    :return mwis_set, a MWIS as a sorted tuple of nodes
    :return mwis_weight, the sum over n in mwis_set of pi[n]
    Examples
    -----------
    >>> Graph = nx.Graph()
    >>> Graph.add_node(1,weight=1)
    >>> Graph.add_node(2,weight=2)
    >>> Graph.add_node(3,weight=3)
    >>> Graph.add_node(4,weight=4)
    >>> Graph.add_node(5,weight=5)
    >>> Graph.add_node(6,weight=6)
    >>> Graph.add_node(7,weight=7)
    >>> Graph.add_node(8,weight=8)
    >>> Graph.add_weighted_edges_from([(1, 8, 2), (8, 1, 4), (2, 1, 5), (1, 3, 4), (3, 8, 2), (8, 2, 3), (8, 5, 4), (5, 7, 3), (7, 6, 2), (6, 5, 4)])
    >>> pi = dict(zip(Graph.nodes(), (Graph.nodes[i]['weight'] for i in Graph.nodes)))
    >>> print(MWIS(Graph, pi,0))
    ([4, 7, 8], 19)
    >>> Graph = nx.Graph()
    >>> Graph.add_node(1,weight=1)
    >>> Graph.add_node(2,weight=2)
    >>> Graph.add_node(3,weight=3)
    >>> Graph.add_node(4,weight=4)
    >>> Graph.add_weighted_edges_from([(2, 1, 3), (1, 3, 1), (3, 2, 2), (3, 4, 5), (4, 3, 9)])
    >>> pi = dict(zip(Graph.nodes(), (Graph.nodes[i]['weight'] for i in Graph.nodes)))
    >>> print(MWIS(Graph, pi,0))
    ([2, 4], 6)
    >>> Graph = nx.Graph()
    >>> Graph.add_node(1,weight=1)
    >>> Graph.add_node(2,weight=2)
    >>> Graph.add_node(3,weight=3)
    >>> Graph.add_node(4,weight=4)
    >>> Graph.add_node(5,weight=5)
    >>> Graph.add_node(6,weight=6)
    >>> Graph.add_node(7,weight=7)
    >>> Graph.add_node(8,weight=8)
    >>> pi = dict(zip(Graph.nodes(), (Graph.nodes[i]['weight'] for i in Graph.nodes)))
    >>> print(MWIS(Graph, pi,0))
    ([1, 2, 3, 4, 5, 6, 7, 8], 36)
    """

    global best_score
    graph_copy = graph.copy()
    # mwis weight is stored as a 'score' graph attribute
    graph_copy.graph['score'] = 0
    best_score = b_score

    def get_mwis(G):
        """compute mawimum weighted independent set (recursively) for non
        yet computed sets. Input is a networkx graph, output is the
        exact MWIS set of nodes and its weight.
        Based on "A column generation approach for graph coloring" from
        Mehrotra and Trick, 1995, using recursion formula:
        MWIS(G union {i}) = max(MWIS(G), MWIS({i} union AN(i)) where
        AN(i) is the anti-neighbor set of node i"""
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


if __name__ == '__main__':
    print(doctest.testmod())
    # graphEX3 = nx.DiGraph()
    # graphEX3.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    # graphEX3.add_weighted_edges_from(
    #     [(1, 6, 11), (6, 1, 10), (1, 5, 3), (5, 1, 2), (8, 9, 11), (9, 8, 20), (3, 2, 6), (2, 6, 5), (6, 3, 8),
    #      (5, 7, 6), (7, 4, 11), (4, 5, 5), (10, 16, 1), (16, 11, 10), (11, 15, 3), (15, 11, 2), (18, 19, 11),
    #      (19, 18, 20), (13, 12, 6), (12, 16, 5), (16, 13, 8)])
    # print(Maximum_weight_cycle_packing_approximation_algorithm(graphEX3, 2))
