"""SimRank matrix of graphs
"""

# Copyright (C) 2015 by
# Janu Verma <j.verma5@gmail.com>
# All rights reserved.
# BSD License. 


import networkx as nx
import numpy as np 
import itertools


__author__ = "\n".join(['Janu Verma (j.verma5@gmail.com)'])

__all__ = ['simrank_matrix']

def simrank_matrix(G, relative_importance_factor=0.9, max_iter=100, tol=1e-4):
	"""Return the SimRank matrix of G.

	SimRank is a vertex similarity measure. It computes the 
	similarity between two nodes on a graph based on the topology, 
	i.e., the nodes and the links of the graph.

	Parameters
	----------
	G : graph
		A networkx graph

	relativeImportanceFactor : float, optional (default = 0.9)
		It represents the relative importance between 
		in-direct neighbors and direct neighbors.

	max_iter : integer, optional (default=100)
		Maximum number of iterations. 

	tol : float, optional
		Error tolerance used to check convergence 

	Returns
	-------
	simrank : Numpy matrix
		Matrix containing SimRank scores of the nodes.

	Examples
	--------
	>>> G = nx.DiGraph(nx.path_graph(4))
	>>> sr = nx.simrank_matrix(G)

	Notes
	-----

	See Also
	--------
	modularity_matrix
	pagerank
	laplacian_matrix

	References
	----------
	.. [1] G. Jeh and J. Widom. "SimRank: a measure of structural-context similarity",
	 	In KDD'02: Proceedings of the eighth ACM SIGKDD international conference on Knowledge discovery and data mining,
	 	pages 538-543. ACM Press, 2002
	"""
	nodes = G.nodes()
	n = len(nodes)
	nodes_dict = {node:i for (i,node) in enumerate(nodes)}

	prev_sim = np.zeros(n)
	new_sim = np.identity(n)

	for i in range(max_iter):
		if (np.allclose(new_sim, prev_sim, atol=tol)):
			break
		prev_sim = np.copy(new_sim)

		for n1 in nodes:
			for n2 in nodes:
				if (n1 == n2):
					continue

				simrank12 = 0.0	
				neighbors1 = G.neighbors(n1)
				neighbors2 = G.neighbors(n2)

				for u in neighbors1:
					for v in neighbors2:
						simrank12 += prev_sim[nodes_dict[u]][nodes_dict[v]]
					new_sim[nodes_dict[n1]][nodes_dict[n2]] = (relative_importance_factor \
						* simrank12)/(len(neighbors1)  * len(neighbors2))

	return new_sim
