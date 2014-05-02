# -*- coding: utf-8 -*-
"""
Greedy graph coloring using various strategies.
"""
#    Copyright (C) 2014 by
#    Christian Olsson <chro@itu.dk>
#    Jan Aagaard Meier <jmei@itu.dk>
#    Henrik Haugbølle <hhau@itu.dk>
#    All rights reserved.
#    BSD license.
import networkx as nx
import random
import itertools
from . import coloring_with_interchange

__author__ = "\n".join(["Christian Olsson <chro@itu.dk>",
                        "Jan Aagaard Meier <jmei@itu.dk>",
                        "Henrik Haugbølle <hhau@itu.dk>"])
__all__ = ['coloring']

def min_degree_node(G):
    return min(G, key=G.degree)

def max_degree_node(G):
    return max(G, key=G.degree)

def dict_to_sets(colors, k):
    sets = [set() for _ in range(k)]

    for (node, color) in colors.items():
        sets[color].add(node)

    return sets

"""
Largest first (lf) ordering. Ordering the nodes by largest degree first.
"""

def strategy_largest_first(G):
    nodes = G.nodes()
    nodes.sort(key=lambda node: -G.degree(node))

    return nodes

"""
Random sequential (RS) ordering. Scrambles nodes into random ordering.
"""
def strategy_random_sequential(G):
    nodes = G.nodes()
    random.shuffle(nodes)

    return nodes

"""
Smallest last (sl). Picking the node with smallest degree first, 
subtracting it from the graph, and starting over with the new smallest degree node. 
When the graph is empty, the reverse ordering of the one built is returned.
"""
def strategy_smallest_last(G):
    len_g = len(G)
    available_g = G.copy()
    nodes = [None]*len_g

    for i in range(len_g):
        node = min_degree_node(available_g)

        available_g.remove_node(node)
        nodes[len_g - i - 1] = node

    return nodes

"""
Greedy independent set ordering (GIS). Generates a maximal independent set of nodes, 
and assigns color C to all nodes in this set. This set of nodes is now
removed from the graph, and the algorithm runs 
"""
def strategy_independent_set(G, colors):
    len_g = len(G)
    no_colored = 0
    k = 0

    uncolored_g = G.copy()
    while no_colored < len_g: # While there are uncolored nodes
        available_g = uncolored_g.copy()

        while len(available_g): # While there are still nodes available
            node = min_degree_node(available_g)
            colors[node] = k # assign color to values

            no_colored += 1
            uncolored_g.remove_node(node)
             # Remove node and its neighbors from available
            available_g.remove_nodes_from(available_g.neighbors(node) + [node])
        k += 1
    return k

"""
Connected sequential ordering (CS). Yield nodes in such an order, that each node, 
except the first one, has at least one neighbour in the preceeding sequence.
The sequence can be generated using both BFS and DFS search
"""
def strategy_connected_sequential(G, traversal='bfs'):
    source = G.nodes()[0]

    yield source # Pick the first node as source

    if traversal == 'bfs':
        tree = nx.bfs_edges(G, source)
    else:
        tree = nx.dfs_edges(G, source)

    for (_, end) in tree:
        yield end # Then yield nodes in the order traversed by either BFS or DFS

"""
Saturation largest first (SLF) or DSATUR.
"""
def strategy_saturation_largest_first(G, colors):
    len_g = len(G)
    no_colored = 0
    distinct_colors = {}

    for node in G.nodes_iter():
        distinct_colors[node] = set()

    while no_colored != len_g:
        if no_colored == 0:
             # When sat. for all nodes is 0, yield the node with highest degree
            no_colored += 1
            node = max_degree_node(G)
            yield node
            for neighbour in G.neighbors_iter(node):
                distinct_colors[neighbour].add(0)
        else:
            highest_saturation = -1
            highest_saturation_nodes = []

            for node, distinct in distinct_colors.items():
                if node not in colors: # If the node is not already colored
                    saturation = len(distinct)
                    if saturation > highest_saturation:
                        highest_saturation = saturation
                        highest_saturation_nodes = [node]
                    elif saturation == highest_saturation:
                        highest_saturation_nodes.append(node)

            if len(highest_saturation_nodes) == 1:
                node = highest_saturation_nodes[0]
            else:
                # Return the node with highest degree
                max_degree = -1
                max_node = None

                for node in highest_saturation_nodes:
                    degree = G.degree(node)
                    if degree > max_degree:
                        max_node = node
                        max_degree = degree

                node = max_node

            no_colored += 1
            yield node
            color = colors[node]
            for neighbour in G.neighbors_iter(node):
                distinct_colors[neighbour].add(color)

"""Color a graph using various strategies of greedy graph coloring.
The strategies are described in [1].

Attempts to color a graph using as few colors as possible, where no 
neighbours of a node can have same color as the node itself.

Parameters
----------
G : NetworkX graph

strategy : string
   Greedy coloring strategy. It is possible to choose from these strategies:
   
   lf: Largest first ordering
   rs: Random sequential ordering
   sl: Smallest last ordering
   gis: Greedy independent set ordering
   cs: Connected sequential ordering (using depth first search)
   cs-dfs: (same as cs)
   cs-bfs: Connected sequential ordering (using breath first search)
   slf: Saturation largest first (also known as DSATUR)
   
interchange: boolean
   If strategy allows it, will use the color interchange algorithm described by [2] if set to true.
   
returntype: string
   Whether to return a dictionary or a list of sets representing colors and nodes.
   Default is dictionary. (See 'Returns' for more information).
   
Returns
-------
If returntype is set to 'dict', a dictionary is returned with keys representing 
nodes and values representing corresponding coloring.

If returntype isset to 'sets', a list of sets is returned. Each set in the 
list represents a color and contains the nodes that is colored with this.

Examples
--------
>>> G = nx.random_regular_graph(2, 4)
>>> d = nx.coloring(G, strategy='lf')
>>> d
{0: 0, 1: 1, 2: 0, 3: 1}
>>> s = nx.coloring(G, strategy='lf', returntype='sets')
>>> s
[set([0, 2]), set([1, 3])]
>>> len(s)
2

References
----------
.. [1] Adrian Kosowski, and Krzysztof Manuszewski,
   Classical Coloring of Graphs, Graph Colorings, 2-19, 2004,
   ISBN 0-8218-3458-4.
   [2] Maciej M. Syslo, Marsingh Deo, Janusz S. Kowalik,
   Discrete Optimization Algorithms with Pascal Programs, 415-424, 1983
   ISBN 0-486-45353-7
"""
def coloring(G, strategy='lf', interchange=False, returntype='dict'):
    colors = dict() # dictionary to keep track of the colors of the nodes
    sets = [] # list of sets

    if len(G):
        # the type returned from strategies should probably be python generators
        if strategy == 'lf':
            nodes = strategy_largest_first(G)
        elif strategy == 'rs':
            nodes = strategy_random_sequential(G)
        elif strategy == 'sl':
            nodes = strategy_smallest_last(G)
        elif strategy == 'gis':
            if interchange:
                raise nx.NetworkXPointlessConcept(
                    'Interchange is not applicable for GIS')
            k = strategy_independent_set(G, colors)
            if returntype == 'sets':
                return dict_to_sets(colors, k)
            return colors
        elif strategy == 'cs' or strategy == 'cs-bfs':
            nodes = strategy_connected_sequential(G)
        elif strategy == 'cs-dfs':
            nodes = strategy_connected_sequential(G, traversal='dfs')
        elif strategy == 'slf':
            if interchange:
                raise nx.NetworkXPointlessConcept(
                    'Interchange is not applicable for SLF')
            nodes = strategy_saturation_largest_first(G, colors)
        else:
            raise nx.NetworkXPointlessConcept(
                'Strategy ' + strategy + ' does not exist.')

        if interchange:
            return coloring_with_interchange.coloring_with_interchange(G, nodes, returntype)
        else:
            for node in nodes:
                neighbour_colors = set() # set to keep track of colors of neighbours

                for neighbour in G.neighbors_iter(node): # iterate through the neighbours of the node
                    if neighbour in colors: # if the neighbour has been assigned a color ...
                        neighbour_colors.add(colors[neighbour]) # ... put it into the neighbour color set

                for color in itertools.count():
                    if color not in neighbour_colors:
                        break

                colors[node] = color # assign the node the newly found color

                if returntype == 'sets': # only maintain the list of sets, if the desired return type is 'set'
                    if len(sets) <= color: # ensure that a set has been initialize at the 'color'/index of the list
                        sets.append(set()) # ... if not, do it
                    
                    sets[color].add(node) # add the node to the respective set

    if returntype == 'sets': # determine desired return type
        return sets
    else:
        return colors
