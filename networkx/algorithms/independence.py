import networkx as nx
from networkx.algorithms import *

from networkx.utils import not_implemented_for
__author__ = """Naresh Peshwe (nareshpeshwe12078@gmail.com)"""
__all__ = ['enumerate_all_independentSets', 'independence_number']


@not_implemented_for('directed')
def enumerate_all_independentSets(G):
    """Returns all independent sets in an undirected graph.

    This function returns an iterator over independent sets, each of which is a
    list of nodes. The iteration is ordered by cardinality of the
    independent sets: first all independent sets of size one, then all independent sets of size
    two, etc.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.
    Returns
    -------
    iterator
        An iterator over independent sets, each of which is a list of nodes in
        `G`. The independent sets are ordered according to size.
    Notes
    -----
    To obtain a list of all independent sets, use the fact that the cliques corresponding
    to the complement graph of G is the independent sets of G.
    
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
	if independentsets = None:
		independentsets = enumerate_all_independentSets(G)
	
	return max( [len(i) for i in independentsets])

