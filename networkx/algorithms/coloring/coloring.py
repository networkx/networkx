# -*- coding: utf-8 -*-
"""Greedy graph coloring using the First Fit algorithm and maximum degree ordering.
"""

"""
Greedy-Color
Color-with-Interchange
RS-Color
LF-Color
SL-Color
RSI-Color
LFI-Color
SLI-Color
CS-Color
SLF-Color
GIS-Color
"""

from heapq import heappush, heappop
import networkx as nx

__author__ = "\n".join(["Christian Olsson <chro@itu.dk>",
						"Jan Aagaard Meier <jmei@itu.dk>",
						"Henrik Haugbølle <hhau@itu.dk>"])
__all__ = ['coloring']

def interchange(G):
	""" Not implemented """

def strategy_maxdegree(G):
	queue = []
	result = []
	for n in G.nodes(): # take each node of the graph ...
		heappush(queue, (len(G.neighbors(n)) * -1, n)) # ... and push it onto the priority queue using its reneighbour degree as priority (max as high priorty)
	
	while len(queue): # iterate the priority queue until empty
		(priority, node) = heappop(queue)
		result.append(node)
		
	return result
	
def strategy_mindegree(G):
		queue = []
		result = []
		for n in G.nodes(): # take each node of the graph ...
			heappush(queue, (len(G.neighbors(n)), n)) # ... and push it onto the priority queue using its neighbour degree as priority (min as high priority)
		
		while len(queue): # iterate the priority queue until empty
			(priority, node) = heappop(queue)
			result.append(node)
			
		return result
		
def coloring(G, strategy='maxdegree', interchange=False, returntype='dict'):
	queue = [] # our priority queue
	colors = dict() # dictionary to keep track of the colors of the nodes
	sets = [] # list of sets

	# the type returned from strategies should probably be python generators
	if strategy == 'maxdegree':
		nodes = strategy_maxdegree(G)
	elif strategy == 'mindegree':
		nodes = strategy_mindegree(G)
	else:
		print 'Strategy ' + strategy + ' does not exist.'
	
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
# 	queue = [] # our priority queue
# 	colors = dict() # dictionary to keep track of the colors of the nodes
# 	sets = [] # list of sets
# 
# 	for n in G.nodes(): # take each node of the graph ...
# 		heappush(queue, (len(G.neighbors(n)) * -1, n)) # ... and push it onto the priority queue using its neighbour degree as priority
# 
# 	while len(queue): # iterate the priority queue until empty
# 		(priority, node) = heappop(queue) # choose the element from the priority queue with highest degree
# 
# 		neighbourColors = set() # set to keep track of colors of neighbours
# 
# 		for neighbour in G.neighbors(node): # iterate through the neighbours of the node
# 			if neighbour in colors: # if the neighbour has been assigned a color ...
# 				neighbourColors.add(colors[neighbour]) # ... put it into the neighbour color set
# 
# 		i = 0 # initialize first potentially available color
# 		color = -1 # initialize non-existant color (-1)
# 		while color == -1: # loop over all possible colors, until a vacant has been found
# 			if i in neighbourColors: # check if the color is already occupied by a neighbour
# 				i = i + 1 # ... if that's the case, move to next color and reiterate
# 			else:
# 				color = i # ... if the color is vacant, choose it as the node's color
# 
# 		colors[node] = color # assign the node the newly found color
# 
# 		if rtype == 'sets': # only maintain the list of sets, if the desired return type is 'set'
# 			if len(sets) <= i: # ensure that a set has been initialize at the 'color'/index of the list
# 				sets.append(set()) # ... if not, do it
# 			
# 			sets[i].add(node) # add the node to the respective set
# 
# 	if rtype == 'sets': # determine desired return type
# 		return sets
# 	else:
# 		return colors
# 
# def max_degree_sets(G):
# 	"""Performs a greedy coloring of the graph using the First Fit algorithm
# 	and maximum degree ordering.
# 
# 	The result returned is a list of sets, containing nodes. Each set 
# 	corresponds to a color of the contained nodes. In other words,
# 	all nodes contained in a given set, is of same color.
# 
# 	Parameters
# 	----------
# 	G : NetworkX graph
# 
# 	Examples
# 	--------
# 	>>> G=nx.graph()
# 	>>> G.add_edges_from([(1,2),(1,3)])
# 	>>> print(nx.max_degree_sets(G))
# 	[set([1]), set([2,3])]
# 
# 	>>> G=nx.graph()
# 	>>> G.add_edges_from([(1,2),(1,3),(2,3)])
# 	>>> print(nx.max_degree_sets(G))
# 	[set([1]), set([2]), set([3])]
# 
# 	See Also
# 	--------
# 	(the 4 other algorithms, that we have not implemented yet)
# 
# 	"""
# 	return max_degree(G, rtype='sets')
# 
# def max_degree_dict(G):
# 	"""Performs a greedy coloring of the graph using the First Fit algorithm
# 	and maximum degree ordering.
# 
# 	The returned result is a dictionary, where keys corresponds to nodes, and
# 	values corresponds to colors. A color is represented by an integer from 0
# 	to the number of unique colors used.
# 
# 	Parameters
# 	----------
# 	G : NetworkX graph
# 
# 	Examples
# 	--------
# 	>>> G=nx.graph()
# 	>>> G.add_edges_from([(1,2),(1,3)])
# 	>>> print(nx.max_degree_dict(G))
# 	{1: 0, 2: 1, 3: 1}
# 
# 	>>> G=nx.graph()
# 	>>> G.add_edges_from([(1,2),(1,3),(2,3)])
# 	>>> print(nx.max_degree_dict(G))
# 	{1: 0, 2: 1, 3: 2}
# 
# 	See Also
# 	--------
# 	(the 4 other algorithms, that we have not implemented yet)
# 
# 	"""
# 	return max_degree(G, rtype='dict')