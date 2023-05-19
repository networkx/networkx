import networkx as nx
import math

__all__ = ["num_independent_sets"]


def _get_tree_neighbors(G, nodes: set)->set:
    '''

    Parameters
    ----------
    nodes: list of nodes

    Returns
    ----------
    list of neighbors
    '''
    neighbors: set = set()
    for node in nodes:
        for k in G.neighbors(node):
            neighbors.add(k)
    return neighbors

def num_independent_sets(G):
    '''Returns the number independent set for a tree graph
    
    Parameters
    ----------
    nodes: list of nodes

    Raises
    ------
    NetworkXNotImplemented
        Independent sets are counted for trees only. If the graph 'G'
        is not a tree a NetworkXNotImplemented is raised.

    Returns
    ----------
    total number of independent sets.

    Notes
    -----
    In graph theory, an independent set, stable set, coclique or anticlique 
    is a set of vertices in a graph, no two of which are adjacent. 

    https://en.wikipedia.org/wiki/Independent_set_(graph_theory)
    
    This function takes a dynamic programming approach to counting the number
    of independent sets in tree graphs exclusively.
    '''
    if not nx.is_tree(G):
        raise nx.NetworkXNotImplemented("Graph must be a tree.")
    postorder_nodes = nx.dfs_postorder_nodes(G)
    num_ind_sets_at_node = dict()

    for node in postorder_nodes:
        # For undirected graphs, only get nodes that are already visited (children)
        children = set(node for node in _get_tree_neighbors(G, {node}) 
                        if node in num_ind_sets_at_node) # get children of the node
        grandchildren = set(node for node in _get_tree_neighbors(G, children) 
                            if node in num_ind_sets_at_node)  # get grandchildren of the node
        
        if len(children) == 0 and len(grandchildren) == 0:
            # a single node has 2 ind sets. {empty, self}
            num_ind_sets_at_node[node] = 2
        elif len(grandchildren) == 0:
            # if grandchildren are empty but children are not,
            # number of ind sets should be product of children + self.
            num_ind_sets_at_node[node] = math.prod([num_ind_sets_at_node[c] for c in children])+1
        else:
            # if both children and grandchildren are not empty,
            # number of ind sets is should be the products children(excluding the current node) and product of grandchildren
            num_ind_sets_at_node[node] =  math.prod([num_ind_sets_at_node[c] for c in children]) +\
                math.prod([num_ind_sets_at_node[gc] for gc in grandchildren])
    return num_ind_sets_at_node[node] #node will always be the root
