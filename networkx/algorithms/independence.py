import networkx as nx
from networkx.algorithms import *

from networkx.utils import not_implemented_for
__author__ = """Naresh Peshwe (nareshpeshwe12078@gmail.com)"""
__all__ = ['enumerate_all_independentSets', 'independence_number']


@not_implemented_for('directed')
def enumerate_all_independentSets(G):
	""" Returns an iterator object over the independent sets of nodes of the graph 'G'.

		Parameters
		----------
		G : Networkx graph
			An undirected graph.

		Returns
		-------
		Iterator

		Returns an iterator over the all the independent set of nodes in the given graph 'G'.

		Note : For finding the independent sets we use the fact that 
		independent sets of a graph G are the cliques corresponding 
		to its complement.

	"""
	return enumerate_all_cliques(complement(G))
	

def independence_number(G, independentsets=None):
	""" Returns the independence number of an undirected graph

	Parameters
	----------
	G : NetworkX graph
		An undirected graph.
	Returns
	-------
	int 

		The size of the largest independent set of nodes of 'G'.
		A maximum independent set is an independent set of largest possible size for a given graph G. 
		This size is called the independence number of G.


	"""
	if independentsets == None:
		independentsets = enumerate_all_independentSets(G)
	return max([len(i) for i in independentsets])

