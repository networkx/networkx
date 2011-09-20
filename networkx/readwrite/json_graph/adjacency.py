#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from copy import deepcopy
from itertools import count,repeat
import json
import networkx as nx
__author__ = """Aric Hagberg (hagberg@lanl.gov))"""
__all__ = ['adjacency_data', 'adjacency_graph']

def adjacency_data(G):
    """Return data in adjacency format that is suitable for JSON serialization
    and use in Javascript documents.

    Parameters
    ----------
    G : NetworkX graph
    
    Returns
    -------
    data : dict
       A dictionary with node-link formatted data.

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.Graph([(1,2)])
    >>> data = json_graph.adjacency_data(G)

    To serialize with json

    >>> import json
    >>> s = json.dumps(data)
    
    Notes
    -----
    Graph, node, and link attributes are stored in this format but keys 
    for attributes must be strings if you want to serialize with JSON.

    See Also
    --------
    adjacency_graph, node_link_data, tree_data
    """
    data = {}
    data['directed'] = G.is_directed()
    data['multigraph'] = G.is_multigraph()
    data['graph'] = list(G.graph.items())
    data['nodes'] = []
    data['adjacency'] = []
    for n,nbrdict in G.adjacency_iter():
        data['nodes'].append(dict(id=n, **G.node[n]))
        adj = []
        for nbr,d in nbrdict.items():
            adj.append(dict(id=nbr, **d))
        data['adjacency'].append(adj)
    return data

def adjacency_graph(data, directed=False, multigraph=True):
    """Return graph from adjacency data format. 

    Parameters
    ----------
    data : dict
        Adjacency list formatted graph data
    
    Returns
    -------
    G : NetworkX graph
       A NetworkX graph object

    directed : bool        
        If True, and direction not specified in data, return a directed graph.

    multigraph : bool        
        If True, and multigraph not specified in data, return a multigraph.

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.Graph([(1,2)])
    >>> data = json_graph.adjacency_data(G)
    >>> H = json_graph.adjacency_graph(data)

    See Also
    --------
    adjacency_graph, node_link_data, tree_data
    """
    multigraph = data.get('multigraph',multigraph)
    directed = data.get('directed',directed)
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()
    graph.graph = dict(data.get('graph',[]))
    mapping=[]
    for d in data['nodes']:
        node = d.pop('id')
        mapping.append(node)
        graph.add_node(node, attr_dict=d)
    for i,d in enumerate(data['adjacency']):
        source = mapping[i]
        for tdata in d:
            target=tdata.pop('id')
            graph.add_edge(source,target,attr_dict=tdata)
    return graph

