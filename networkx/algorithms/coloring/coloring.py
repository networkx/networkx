# -*- coding: utf-8 -*-
"""Greedy graph coloring using the First Fit algorithm and maximum degree ordering.
"""

"""
                            impl    shc    hc    strategy test
Greedy-Color                
Color-with-Interchange
RS-Color                    x        non   non
LF-Color                    x        x     x
SL-Color                    x        x     x
CS-Color                    x        x     
SLF-Color                   x        x     x
GIS-Color                   x        x     x
RSI-Color                   x        non   non   
LFI-Color                   x
SLI-Color                   x
CSI-Color                   x        ?     ?
SLFI-Color                  x        ?     ?
"""

from heapq import heappush, heappop
import itertools
import networkx as nx
import sys
import random

__author__ = "\n".join(["Christian Olsson <chro@itu.dk>",
                        "Jan Aagaard Meier <jmei@itu.dk>",
                        "Henrik Haugbølle <hhau@itu.dk>"])
__all__ = ['coloring']
    
    
def min_degree_node(G):
    degree = G.degree()
    v = list(degree.values())
    k = list(degree.keys())
    return k[v.index(min(v))]

def max_degree_node(G):
    degree = G.degree()
    v = list(degree.values())
    k = list(degree.keys())
    return k[v.index(max(v))]

def doInterchange(G, node, colors, returntype, sets):
    # Build a graph where queries on adjacency nodes for a given color combination is possible
    graph = {}
    for tmpNode in G.nodes():
        graph[tmpNode] = {}
    
    for tmpNode in G.nodes():
        for neighbour in G.neighbors(tmpNode):
            if (tmpNode in colors) and (neighbour in colors):
                color0 = colors[tmpNode]
                color1 = colors[neighbour]
                if color0 < color1:
                    combination = (color0, color1)
                else:
                    combination = (color1, color0)

                if not combination in graph[tmpNode]:
                    graph[tmpNode][combination] = []
                if not combination in graph[neighbour]:
                    graph[neighbour][combination] = []
                graph[tmpNode][combination].append(neighbour)
                graph[neighbour][combination].append(tmpNode)
    
    # Build a dictionary storing neighbouring nodes for each color
    neighboursWithColor = {}
    for neighbour in G.neighbors(node):
        if (neighbour in colors):
            color = colors[neighbour]
            if not color in neighboursWithColor:
                neighboursWithColor[color] = []
            neighboursWithColor[color].append(neighbour) 
    
    # Iterate through all color combination and see if there is a connection
    combinations = itertools.combinations(neighboursWithColor, 2) # Find all combination of neighbour colors
    for combination in combinations: # For all combinations
        color0 = combination[0] # The first color in the combination
        color1 = combination[1] # The second color in the combination
        neighboursColor0 = neighboursWithColor[color0] # A list storing all neighbours with color0
        neighboursColor1 = neighboursWithColor[color1] # A list storing all neighbours with color1
        
        # In the following section we find all nodes reachable from neighbours with color0
        # When traversing the graph using BFS we only add nodes of either color0 or color1 
        visited = set()
        queue = list(neighboursColor0)
        while queue:
            newNode = queue.pop()
            visited.add(newNode)
            if combination in graph[newNode]: 
                for neighbour in graph[newNode][combination]:
                    if not neighbour in visited:
                        queue.append(neighbour)
            
        # In this section we test if there was a connection from neighbours with color0 to neighbours with color1
        differentComponents = True
        for neighbourColor1 in neighboursColor1:
            if neighbourColor1 in visited:
                differentComponents = False

        # If there were no connection we swap the colors of one of the components
        if(differentComponents):
            for nodeToColor in visited: # For all nodes in the connected component
                if colors[nodeToColor] == color0: # If the node has color0
                    colors[nodeToColor] = color1 # ... we color it with color1
                    if returntype == 'sets': # If the return type is sets we need to maintain the data structure
                        sets[color0].remove(nodeToColor)
                        sets[color1].add(nodeToColor)
                elif colors[nodeToColor] == color1: # If the node has color1
                    colors[nodeToColor] = color0 # ... we color it with color0
                    if returntype == 'sets': # If the return type is sets we need to maintain the data structure
                        sets[color1].remove(nodeToColor)
                        sets[color0].add(nodeToColor)
            return color0 # Return the color that was is no longer adjacent to this node
    return -1 # The function did not successeed in finding two colors to swap

"""
Largest first (lf) ordering. Ordering the nodes by largest degree first.
"""

def strategy_lf(G):
    nodes = G.nodes()
    nodes.sort(key=lambda node: G.degree(node) * -1)
    
    return iter(nodes)
"""
Smallest first (sf) ordering. Ordering the nodes by smallest degree first.
"""

def strategy_sf(G):
    nodes = G.nodes()
    nodes.sort(key=lambda node: G.degree(node))
    
    return iter(nodes)
    
"""
Random sequential (RS) ordering. Scrambles nodes into random ordering.
"""
def strategy_rs(G):
    nodes = G.nodes()
    random.shuffle(nodes)
    
    return iter(nodes)
    
"""
Smallest last (sl). Picking the node with smallest degree first, subtracting it from the graph, and starting over with the new smallest degree node. When
the graph is empty, the reverse ordering of the one built is returned.
"""

def strategy_sl(G):
    available_g = G.copy()
    k = []
    
    while len(available_g):
        node = min_degree_node(available_g)
        
        available_g.remove_node(node)
        k.append(node)
    
    return reversed(k)
    
"""
Greedy independent set ordering (GIS). Generates a maximum independent set of nodes, and assigns color C to all nodes in this set. This set of nodes is now
removed from the graph, and the algorithm runs 
"""
def strategy_gis(G, colors):
    len_g = len(G)
    no_colored = 0
    k = 0

    while no_colored < len_g: # While there are uncolored nodes 
        available_g = G.copy()

        # Find all uncolored nodes
        for node in available_g.nodes():
            if node in colors:
                available_g.remove_node(node)

        while available_g.number_of_nodes() > 0: # While there are still vertices available
            degree = available_g.degree()
            
            # Pick the one with minimal degree in available
            # Finding the minimum degree, http://stackoverflow.com/a/12343826/800016
            values = list(degree.values())
            keys = list(degree.keys())
            node = keys[values.index(min(values))]
            colors[node] = k # assign color to values

            no_colored += 1
            available_g.remove_nodes_from(available_g.neighbors(node) + [node]) # Remove v and its neighbors from available
        k += 1
    return k

"""
Connected sequential ordering (CS). Yield nodes in such an order, that each node, except the first one, has at least one neighbour in the preceeding sequence.
The sequence can be generated using both BFS and DFS search
"""
def strategy_cs(G, traversal='bfs'):
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
def strategy_slf(G, colors):
    len_g = len(G)
    no_colored = 0
    saturation = {}
    for node in G.nodes():
        saturation[node] = 0

    while no_colored != len_g:
        if no_colored == 0: # When saturation for all nodes is 0, yield the node with highest degree
            no_colored += 1
            node = max_degree_node(G)
            yield node
            for neighbour in G.neighbors(node):
                saturation[node] += 1
        else:
            highest_saturation = -1
            highest_saturation_nodes = []

            for (node, satur) in saturation.items():
                if node not in colors: # If the node is not already colored
                    if satur > highest_saturation:
                        highest_saturation = satur
                        highest_saturation_nodes = [node]
                    elif satur == highest_saturation:
                        highest_saturation_nodes.append(node)

            if len(highest_saturation_nodes) == 1:
                node = highest_saturation_nodes[0]
            else:
                # Return the node with highest degree
                degree = dict()
                for node in highest_saturation_nodes:
                    degree[node] = G.degree(node)

                v = list(degree.values())
                k = list(degree.keys())

                node = k[v.index(max(v))]

            no_colored += 1
            yield node
            for neighbour in G.neighbors(node):
                saturation[node] += 1
    

def dict_to_sets(colors, k):
    sets = [set() for i in range(k)]

    for (node, color) in colors.items():
        sets[color].add(node)

    return sets



def coloring(G, strategy='lf', interchange=False, returntype='dict'):
    colors = dict() # dictionary to keep track of the colors of the nodes
    sets = [] # list of sets

    # the type returned from strategies should probably be python generators
    if strategy == 'lf':
        nodes = strategy_lf(G)
    elif strategy == 'rs':
        nodes = strategy_rs(G)
    elif strategy == 'sf':
        nodes = strategy_sf(G)
    elif strategy == 'sl':
        nodes = strategy_sl(G)
    elif strategy == 'gis':
        k = strategy_gis(G, colors)
        if returntype == 'sets':
            return dict_to_sets(colors, k)
        return colors
    elif strategy == 'cs' or strategy == 'cs-bfs':
        nodes = strategy_cs(G)
    elif strategy == 'cs-dfs':
        nodes = strategy_cs(G, traversal='dfs')
    elif strategy == 'slf':
        nodes = strategy_slf(G, colors)
    else:
        print 'Strategy ' + strategy + ' does not exist.'
        return colors

    if interchange:
        noColors = 1 # There is no reason for swapping less than to colors
        
    for node in nodes:
        neighbourColors = set() # set to keep track of colors of neighbours

        for neighbour in G.neighbors(node): # iterate through the neighbours of the node
            if neighbour in colors: # if the neighbour has been assigned a color ...
                neighbourColors.add(colors[neighbour]) # ... put it into the neighbour color set

        i = 0 # initialize first potentially available color
        color = -1 # initialize non-existant color (-1)
        
        while color == -1: # loop over all possible colors, until a vacant has been found
            if i in neighbourColors: # check if the color is already occupied by a neighbour
                if interchange and i == noColors:
                    result = doInterchange(G, node, colors, returntype, sets)
                    if result != -1:
                        color = result
                    else:
                        i += 1
                        color = i
                        noColors = i
                else:
                    i += 1 # ... if that's the case, move to next color and reiterate
            else:
                color = i # ... if the color is vacant, choose it as the node's color

        colors[node] = color # assign the node the newly found color
        
        if returntype == 'sets': # only maintain the list of sets, if the desired return type is 'set'
            if len(sets) <= color: # ensure that a set has been initialize at the 'color'/index of the list
                sets.append(set()) # ... if not, do it
            
            sets[color].add(node) # add the node to the respective set

    if returntype == 'sets': # determine desired return type
        return sets
    else:
        return colors