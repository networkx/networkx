import networkx as nx


__author__ = "Rohail Syed <rohailsyed@gmail.com>"

__all__ = [
	'bridges_exist',
	'all_bridges',
	'all_local_bridges'
]



def bridges_exist(G):
	""" Checks if any bridges exist in this network. We will simply call the all_bridges()
	function with the first-match stop parameter. Since the search for bridges will terminate
	after finding one instance, this function is faster if we just want to know if at least one
	bridge exists in the network and what it is.
	
	Parameters
	----------
	G : Undirected Graph object
	
	Returns
	----------
	boolean
		True if we found at least one bridge.
		False otherwise.
	
	Notes
	----------
	This function can be useful to quickly determine whether or not bridges exist in a given network.
	"""
	
	results = all_bridges(G, first_match = True)
	if len(results)>0:
		return True
	else:
		return False

		
		




def all_local_bridges(G, first_match=False):
	""" Looks through the graph object G for all local bridges.
	We formally define a local bridge to be any edge AB such that the removal
	of the edge results in a distance strictly greater than 2 between nodes A and B.
	Note that all bridges are local bridges.
	
	Parameters
	----------
	G : Undirected Graph object
	first_match : boolean
		Tells us if we should only look for at least one instance of a local bridge (True) or look for
		all (False).
	
	Returns
	----------
	dict
		edges : List of edges that are local bridges
		spans : List of corresponding spans of the ith local bridge
	
	Notes
	----------
	This function can be useful to quickly determine what local bridges exist in a given network
	and what their spans are.
	"""
	
	# For each node A, remove the edge it has with each of its neighbors and determine
	# A's new shortest path to that node. If none exists, we have a bridge (span=-1 represents infinite)
	# Otherwise record the finite and strictly greater than 2 span of the local bridge.
	nodeset = G.nodes()
	allBridges = []
	allSpans = []
	usedNodes = []
	for startNode in nodeset:
		neighbors = G.neighbors(startNode)
		for endNode in neighbors:
			if endNode in usedNodes:
				# this edge has already been checked. move on
				continue
			if [startNode,endNode] in allBridges:
				# this edge is already known to be a local bridge
				continue
			G.remove_edge(startNode, endNode)
			try:
				pathLength = nx.shortest_path_length(G, startNode, endNode)
				G.add_edge(startNode, endNode)
				if pathLength>2:
					# found a local bridge
					allBridges.append([startNode, endNode])
					allSpans.append(pathLength)
					if first_match:
						return {"edges":allBridges, "spans":allSpans}
						
			except nx.NetworkXNoPath:
				# found a bridge
				allBridges.append([startNode, endNode])
				allSpans.append(-1)
				G.add_edge(startNode, endNode)
				if first_match:
					return {"edges":allBridges, "spans":allSpans}
		usedNodes.append(startNode)
		
	return {"edges":allBridges, "spans":allSpans}






def all_bridges(G, first_match=False):
	""" Looks through the graph object G for all bridges.
	We formally define a bridge to be any edge AB such that the removal
	of the edge results in a distance of infinite between nodes A and B. Specifically,
	this means that the total number of connected components should increase by one after
	the removal of the edge.
	
	Parameters
	----------
	G : Undirected Graph object
	first_match: boolean
		Tells us if we should only look for at least one instance of a bridge (True) or look for
		all (False).
	
	Returns
	----------
	list
		List of edges that are bridges
	
	Notes
	----------
	This function can be useful to quickly determine what bridges exist in a given network.
	"""
	
	# For each node A, remove the edge it has with each of its neighbors and determine
	# A's new shortest path to that node. If none exists, we have a bridge
	nodeset = G.nodes()
	allBridges = []
	usedNodes = []
	for startNode in nodeset:
		neighbors = G.neighbors(startNode)
		for endNode in neighbors:
			if endNode in usedNodes:
				# this edge has already been checked. move on
				continue
			if [startNode,endNode] in allBridges:
				# this edge is already known to be a bridge
				continue
			G.remove_edge(startNode, endNode)
			try:
				pathLength = nx.shortest_path_length(G, startNode, endNode)
				G.add_edge(startNode, endNode)
			except nx.NetworkXNoPath:
				# found a bridge
				allBridges.append([startNode, endNode])
				G.add_edge(startNode, endNode)
				if first_match:
					return allBridges
		usedNodes.append(startNode)
	return allBridges
