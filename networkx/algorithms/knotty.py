# -*- coding: utf-8 -*-
import networkx as nx
import numpy as np
__author__ = """\n""".join(['Murray Shanahan',
							'Mark Wildie',
                            'Erik Ziegler <erik.ziegler@ulg.ac.be>'])

__all__ = ['knotty_centrality']

def knotty_centrality(G, compact=True):
    """Return the sub-graph with the highest value of knotty centrality

	Attempts to find the sub-graph of G with the highest value for
	knotty-centrality. Carries out a series of exhaustive searches on
	subsets of the nodes ranked by "indirect" betweenness centrality, then
	carries out a phase of hill-climbing to see whether the sub-graph can
	be improved by adding further nodes.
	
	Written by Erik Ziegler, adapted from original MATLAB code 
	by Murray Shanahan and Mark Wildie

    Parameters
    ----------
    G : NetworkX graph 
    compact : bool (optional)
       Calculates the compact knotty centrality (default=True)

    Returns
    -------       
    g : NetworkX graph
       The sub-graph with the highest knotty centrality
       (also stored in each node as 'value')
    nodes: list
		nodes in the sub-graph with the highest knotty centrality
    kc : float
		the highest value of knotty centrality
		
    Examples
    --------
    >>> G = nx.Graph([(0,1),(0,2),(1,2),(1,3),(1,4),(4,5)])
    >>> g, nodes, kc = nx.knotty_centrality(G,compact=False)

    Notes
    ------
    The knotty centrality definition and algorithm are found in [1]_. 

    References
    ----------
    .. [1] Shanahan M, Wildie M (2012) Knotty-Centrality: 
    Finding the Connective Core of a Complex Network. 
    PLoS ONE 7(5): e36579. doi:10.1371/journal.pone.0036579 

    """
    if G.is_multigraph() or G.is_directed():
        raise Exception('knotty centrality is not implemented for ',
                        'directed or multiedge graphs.')
                        
    nodes, kc = _find_knotty_centre(G, compact)
    g = G.subgraph(nodes)

    return g, nodes, kc

def filter_list(full_list, excludes):
	# borrowed from StackOverflow's Daniel Pryden
	# http://stackoverflow.com/questions/4211209/remove-all-the-elements-that-occur-in-1-list-from-another
    s = set(excludes)
    return (x for x in full_list if x not in s)

def _find_knotty_centre(G, compact):
	# nodes = the sub-graph found
	# kc = its knotty-centredness

	N = G.number_of_nodes()

	# binarise matrix - all non-zero weights become 1s
	edge_matrix = np.array(nx.to_numpy_matrix(G))
	CIJ = edge_matrix!=0
	CIJ = CIJ.astype(int)


	# Exhastive search phase
	Exh = 10 # number of nodes for exhaustive search (2^Exh combinations)
	Exh = min([Exh,N])
	
	BC_dict = nx.betweenness_centrality(G)
	BC_list = list(BC_dict.values())
	
	BC = np.array(BC_list)/sum(BC_list) # normalise wrt total betweenness centrality

	# Calculate indirect betweenness centrality
	BC2 = np.zeros((N))
	for i in range(0,N):
		BC2[i] = BC[i]+(sum(CIJ[i,:]*BC[i]))+(sum(CIJ[:,i].T*BC[i]))
	
	# Ranking the nodes in descending order
	array_asc = (BC2.ravel().argsort())
	list_asc = array_asc.tolist()
	list_asc.reverse() #list_asc is not descending
	IxBC = list_asc
	
	nodes = []
	improving = 1
	
	while improving:
		L = len(nodes)
		nodes_left = IxBC
		nodes_left = list(filter_list(nodes_left, nodes))	
		choices = [nodes_left[i] for i in range(0, min([Exh,len(nodes_left)]))]
		nodes, kc = _best_perm(nodes, choices, G, CIJ, compact,BC)
		improving = len(nodes) > L

	# Hill climbing phase
	nodes_left = range(0,N)
	nodes_left = list(filter_list(nodes_left, nodes))	
	improving = 1
	
	while improving and nodes_left:
		best_kc = 0
		for node in nodes_left:
			nodes2 = np.hstack((nodes, node))
			kc2 = _compute_knotty_centrality(G, CIJ, nodes2, compact, BC)
			if kc2 > best_kc:
				best_kc = kc2
				best_node = node
				
		if best_kc > kc:
			kc = best_kc
			nodes = np.hstack((nodes, best_node))
			nodes_left.remove(best_node)
		else:
			improving = 0
	return nodes, kc

def _best_perm(given, choices, G, CIJ, compact, BC):
	# Carries out exhaustive search to find a permutation of nodes in
	# "choices" that when added to the nodes in "given" yields the highest
	# value of knotty-centrality

	if choices:
		choices2 = [choices[i] for i in range(0, len(choices))]
		new = choices[0]
		nodes1, kc1 = _best_perm(np.hstack((given, new)), choices2, G, CIJ, compact, BC)
		nodes2, kc2 = _best_perm(given, choices2, G, CIJ, compact, BC)
		if kc1 > kc2:
			nodes = nodes1
			kc = kc1
		else:
			nodes = nodes2
			kc = kc2
	else:
		nodes = given
		kc = _compute_knotty_centrality(G, CIJ, nodes, compact, BC)
	return nodes, kc

def _compute_knotty_centrality(G, CIJ, nodes, compact, BC):
	# Returns knotty-centrality of the subgraph of CIJ comprising only
	# "nodes" and the associated connections
	
	if len(nodes) < 3:
		kc = 0
	else:
		CIJ = CIJ!=0 # binarise matrix
		CIJ = CIJ.astype(int) #set to 1/0 instead of True/False
		N = len(CIJ) # nodes in overall graph
		M = len(nodes) # nodes in subgraph

		BC_list = [BC[i] for i in nodes]
		BCtot = sum(BC_list)			
		
		p = ((float(N)-M)/N) # proportion of nodes not in subgraph

		g = G.subgraph(nodes.tolist())
		RC = nx.density(g)

		if compact:
			kc = p*BCtot*RC; # compact knotty-centrality
		else:
			kc = BCtot*RC; # knotty-centrality
	return kc
