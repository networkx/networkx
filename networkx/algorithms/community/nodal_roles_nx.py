from networkx.algorithms.community import louvain
import networkx as nx

def convert_dictionary(dictionary):
	'''
	Converts dictionary with nodes as keys to modules as keys

	------
	Inputs
	------
	dictionary =  dictionary output from Louvain community detection

	------
	Output
	------
	Dictionary with modules as keys, nodes as values

	'''

	new_dict = {}
	for m,n in zip(dictionary.values(),dictionary.keys()):
	    try:
	        new_dict[m].append(n)
	    except KeyError:
	        new_dict[m] = [n]
	return new_dict

def get_within_module_edges(module, graph):
	module_edges = []
	for edge in graph.edges():
		if edge[0] in module and edge[1] in module:
			module_edges.append(edge)
	return module_edges


def within_module_degree(graph, partition, weighted = False):
    '''
    Computes the within-module degree for each node (Guimera et al. 2005)

    ------
    Inputs
    ------
    graph = Networkx Graph
   	partition = dictionary from modularity partition of graph using Louvain method
    where the keys are nodes and values are module numbers
    weighted: Boolean

    ------
    Output
    ------
    Dictionary of the within-module degree of each node.

    '''
    graph = graph.to_undirected()
    partition = convert_dictionary(partition)
    wmd_dict = {}
    for module in partition.keys():
        module = partition[module]
        module_wd_dict = {}
        module_edges = get_within_module_edges(module,graph)
        for source in module:
            edge_count = 0
            for target in module:
                if (source,target) in module_edges or (target,source) in module_edges:
                    if weighted:
                        edge_count += graph.get_edge_data(source,target)['weight']
                        edge_count += graph.get_edge_data(target,source)['weight']
                    else:
                        edge_count += 1
            module_wd_dict[source] = edge_count
        module_avg_wmd = float(sum(module_wd_dict.values()) / len(module_wd_dict))
        stds = []
        for value in module_wd_dict.values():
            std_v = (module_avg_wmd - value)**2
            stds.append(std_v)
        std = float(sum(stds) / len(stds))
        for source in module:
            wmd_dict[source] = (module_wd_dict[source] - module_avg_wmd) / std
    return wmd_dict


def participation_coefficient(graph, partition, weighted = False):
    '''
    Computes the participation coefficient for each node (Guimera et al. 2005).

    ------
    Inputs
    ------
    graph = Networkx Graph
    partition = dictionary from modularity partition of graph using Louvain method
    where the keys are nodes and values are module numbers
    weighted: Boolean

    ------
    Output
    ------
    Dictionary of the participation coefficient for each node.

    '''
    graph = graph.to_undirected()
    old_partition = partition
    partition = convert_dictionary(old_partition)
    pc_dict = {}
    all_nodes = set(graph.nodes())
    if weighted == False:
        for module in partition.keys():
            module_nodes = set(partition[module])
            outside_module_nodes = list(set.difference(all_nodes, module_nodes))
            for source in module_nodes:
                edge_count = 0
                for target in outside_module_nodes:
                    if (source,target) in graph.edges() or(source,target) in graph.edges():
                        if weighted:
	                        count += graph.get_edge_data(source,target)['weight']
	                        count += graph.get_edge_data(target,source)['weight']
                        else:
                        	edge_count += 1
                bm_degree = float(edge_count)
                if bm_degree == 0.0:
                    pc = 0.0
                else:
                    degree = float(nx.degree(G=graph, nbunch=source))
                    pc = 1 - ((float(bm_degree) / float(degree))**2)
                pc_dict[source] = pc
        return pc_dict




