#    Copyright (C) 2011-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from copy import deepcopy
from itertools import count,repeat
import json
import networkx as nx
__author__ = """Aric Hagberg <aric.hagberg@gmail.com>"""
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
    Graph, node, and link attributes will be written when using this format
    but attribute keys must be strings if you want to serialize the resulting
    data with JSON.

    See Also
    --------
    adjacency_graph, node_link_data, tree_data
    """
    multigraph = G.is_multigraph()
    data = {}
    data['directed'] = G.is_directed()
    data['multigraph'] = multigraph
    data['graph'] = list(G.graph.items())
    data['nodes'] = []
    data['adjacency'] = []
    for n,nbrdict in G.adjacency_iter():
        data['nodes'].append(dict(id=n, **G.node[n]))
        adj = []
        if multigraph:
            for nbr,key in nbrdict.items():
                for k,d in key.items():
                    adj.append(dict(id=nbr, key=k, **d))
        else:
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
        node_data = d.copy()
        node = node_data.pop('id')
        mapping.append(node)
        graph.add_node(node, attr_dict=node_data)
    for i,d in enumerate(data['adjacency']):
        source = mapping[i]
        for tdata in d:
            target_data = tdata.copy()
            target = target_data.pop('id')
            key = target_data.pop('key', None)
            if not multigraph or key is None:
                graph.add_edge(source,target,attr_dict=tdata)
            else:
                graph.add_edge(source,target,key=key, attr_dict=tdata)
    return graph
