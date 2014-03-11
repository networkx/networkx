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
SLF-Color
GIS-Color                   x        x     x
RSI-Color
LFI-Color
SLI-Color
"""

from heapq import heappush, heappop
import networkx as nx
import sys

__author__ = "\n".join(["Christian Olsson <chro@itu.dk>",
                        "Jan Aagaard Meier <jmei@itu.dk>",
                        "Henrik Haugbølle <hhau@itu.dk>"])
__all__ = ['coloring']
    
    
def min_degree_node(G):
    degree = G.degree()
    v = list(degree.values())
    k = list(degree.keys())
    return k[v.index(min(v))]

def interchange(G):
    """ Not implemented """

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
            v = list(degree.values())
            k = list(degree.keys())
            node = k[v.index(min(v))]
            yield node # assign color to v

            no_colored += 1
            available_g.remove_nodes_from(available_g.neighbors(node) + [node]) # Remove v and its neighbors from available

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
    
        
def coloring(G, strategy='maxdegree', interchange=False, returntype='dict'):
    colors = dict() # dictionary to keep track of the colors of the nodes
    sets = [] # list of sets

    # the type returned from strategies should probably be python generators
    if strategy == 'lf':
        nodes = strategy_lf(G)
    elif strategy == 'sf':
        nodes = strategy_sf(G)
    elif strategy == 'sl':
        nodes = strategy_sl(G)
    elif strategy == 'gis':
        nodes = strategy_gis(G, colors)
    elif strategy == 'cs' or strategy == 'cs-bfs':
        nodes = strategy_cs(G)
    elif strategy == 'cs-dfs':
        nodes = strategy_cs(G, traversal='dfs')
    else:
        print 'Strategy ' + strategy + ' does not exist.'
        return colors

    for node in nodes:
        neighbourColors = set() # set to keep track of colors of neighbours

        for neighbour in G.neighbors(node): # iterate through the neighbours of the node
            if neighbour in colors: # if the neighbour has been assigned a color ...
                neighbourColors.add(colors[neighbour]) # ... put it into the neighbour color set

        i = 0 # initialize first potentially available color
        color = -1 # initialize non-existant color (-1)
        while color == -1: # loop over all possible colors, until a vacant has been found
            if i in neighbourColors: # check if the color is already occupied by a neighbour
                if interchange == True:
                    print "Interchange is not implemented"
                    
                i = i + 1 # ... if that's the case, move to next color and reiterate
                
            else:
                color = i # ... if the color is vacant, choose it as the node's color

        colors[node] = color # assign the node the newly found color

        if returntype == 'sets': # only maintain the list of sets, if the desired return type is 'set'
            if len(sets) <= i: # ensure that a set has been initialize at the 'color'/index of the list
                sets.append(set()) # ... if not, do it
            
            sets[i].add(node) # add the node to the respective set

    if returntype == 'sets': # determine desired return type
        return sets
    else:
        return colors



# 
# def max_degree(G, rtype='dict'):
#   queue = [] # our priority queue
#   colors = dict() # dictionary to keep track of the colors of the nodes
#   sets = [] # list of sets
# 
#   for n in G.nodes(): # take each node of the graph ...
#       heappush(queue, (len(G.neighbors(n)) * -1, n)) # ... and push it onto the priority queue using its neighbour degree as priority
# 
#   while len(queue): # iterate the priority queue until empty
#       (priority, node) = heappop(queue) # choose the element from the priority queue with highest degree
# 
#       neighbourColors = set() # set to keep track of colors of neighbours
# 
#       for neighbour in G.neighbors(node): # iterate through the neighbours of the node
#           if neighbour in colors: # if the neighbour has been assigned a color ...
#               neighbourColors.add(colors[neighbour]) # ... put it into the neighbour color set
# 
#       i = 0 # initialize first potentially available color
#       color = -1 # initialize non-existant color (-1)
#       while color == -1: # loop over all possible colors, until a vacant has been found
#           if i in neighbourColors: # check if the color is already occupied by a neighbour
#               i = i + 1 # ... if that's the case, move to next color and reiterate
#           else:
#               color = i # ... if the color is vacant, choose it as the node's color
# 
#       colors[node] = color # assign the node the newly found color
# 
#       if rtype == 'sets': # only maintain the list of sets, if the desired return type is 'set'
#           if len(sets) <= i: # ensure that a set has been initialize at the 'color'/index of the list
#               sets.append(set()) # ... if not, do it
#           
#           sets[i].add(node) # add the node to the respective set
# 
#   if rtype == 'sets': # determine desired return type
#       return sets
#   else:
#       return colors
# 
# def max_degree_sets(G):
#   """Performs a greedy coloring of the graph using the First Fit algorithm
#   and maximum degree ordering.
# 
#   The result returned is a list of sets, containing nodes. Each set 
#   corresponds to a color of the contained nodes. In other words,
#   all nodes contained in a given set, is of same color.
# 
#   Parameters
#   ----------
#   G : NetworkX graph
# 
#   Examples
#   --------
#   >>> G=nx.graph()
#   >>> G.add_edges_from([(1,2),(1,3)])
#   >>> print(nx.max_degree_sets(G))
#   [set([1]), set([2,3])]
# 
#   >>> G=nx.graph()
#   >>> G.add_edges_from([(1,2),(1,3),(2,3)])
#   >>> print(nx.max_degree_sets(G))
#   [set([1]), set([2]), set([3])]
# 
#   See Also
#   --------
#   (the 4 other algorithms, that we have not implemented yet)
# 
#   """
#   return max_degree(G, rtype='sets')
# 
# def max_degree_dict(G):
#   """Performs a greedy coloring of the graph using the First Fit algorithm
#   and maximum degree ordering.
# 
#   The returned result is a dictionary, where keys corresponds to nodes, and
#   values corresponds to colors. A color is represented by an integer from 0
#   to the number of unique colors used.
# 
#   Parameters
#   ----------
#   G : NetworkX graph
# 
#   Examples
#   --------
#   >>> G=nx.graph()
#   >>> G.add_edges_from([(1,2),(1,3)])
#   >>> print(nx.max_degree_dict(G))
#   {1: 0, 2: 1, 3: 1}
# 
#   >>> G=nx.graph()
#   >>> G.add_edges_from([(1,2),(1,3),(2,3)])
#   >>> print(nx.max_degree_dict(G))
#   {1: 0, 2: 1, 3: 2}
# 
#   See Also
#   --------
#   (the 4 other algorithms, that we have not implemented yet)
# 
#   """
#   return max_degree(G, rtype='dict')