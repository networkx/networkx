#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from itertools import count,repeat
import json
import networkx as nx
__author__ = """Aric Hagberg (hagberg@lanl.gov))"""
__all__ = ['tree_data',
           'tree_graph']

def tree_data(G, root):
    """Return data in tree format that is suitable for JSON serialization
    and use in Javascript documents.

    Parameters
    ----------
    G : NetworkX graph
       G must be an oriented tree

    root : node
       The root of the tree

    Returns
    -------
    data : dict
       A dictionary with node-link formatted data.

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.DiGraph([(1,2)])
    >>> data = json_graph.tree_data(G,root=1)

    To serialize with json

    >>> import json
    >>> s = json.dumps(data)
    
    Notes
    -----
    Node attributes are stored in this format but keys 
    for attributes must be strings if you want to serialize with JSON.
    
    Graph and edge attributes are not stored.

    See Also
    --------
    tree_graph, node_link_data, node_link_data
    """
    if not G.number_of_nodes()==G.number_of_edges()+1:
        raise TypeError("G is not a tree.")
    if not G.is_directed():
        raise TypeError("G is not directed")
    def add_children(n, G):
        nbrs = G[n]
        if len(nbrs) == 0:
            return []
        children = []
        for child in nbrs:
            d = dict(id=child, **G.node[child])
            c = add_children(child,G)
            if c:
                d['children'] = c
            children.append(d)
        return children
    data = dict(id=root, **G.node[root])
    data['children'] = add_children(root,G)
    return data

def tree_graph(data):
    """Return graph from tree data format. 

    Parameters
    ----------
    data : dict
        Tree formatted graph data
    
    Returns
    -------
    G : NetworkX DiGraph

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.DiGraph([(1,2)])
    >>> data = json_graph.tree_data(G,root=1)
    >>> H = json_graph.tree_graph(data)

    See Also
    --------
    tree_graph, node_link_data, adjacency_data
    """
    graph = nx.DiGraph()
    def add_children(parent, children):
        for data in children:
            child = data['id']
            graph.add_edge(parent, child)
            grandchildren = data.get('children',[])
            if grandchildren:
                add_children(child,grandchildren)
            nodedata = dict((str(k),v) for k,v in data.items() 
                            if k!='id' and k!='children')
            graph.add_node(child,attr_dict=nodedata)
    root = data['id']
    children = data.get('children',[])
    nodedata = dict((k,v) for k,v in data.items() 
                    if k!='id' and k!='children')
    graph.add_node(root, attr_dict=nodedata)
    add_children(root, children)
    return graph
