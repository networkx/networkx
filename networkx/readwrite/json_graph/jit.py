"""
Read and write NetworkX graphs as JavaScript InfoVis Toolkit (JIT) format JSON.

See the JIT documentation and examples at http://thejit.org

Format
------
var json = [
  {
    "id": "aUniqueIdentifier",
    "name": "usually a nodes name",
    "data": {
      "some key": "some value",
      "some other key": "some other value"
     },
    "adjacencies": [
    {
      nodeTo:"aNodeId",
      data: {} //put whatever you want here
    },
    'other adjacencies go here...'
  },

  'other nodes go here...'
];
"""

#    Copyright (C) 2011-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['jit_graph', 'jit_data']

import networkx as nx
import json


def jit_graph(data):
    """Read a graph from JIT JSON.

    Parameters
    ----------
    data : JIT JSON string

    Returns
    -------
    G : NetworkX Graph
    """
    G = nx.Graph()
    for node in data:
        for adj in node['adjacencies']:
            G.add_edge(node['id'], adj['nodeTo'], **adj['data'])
            G.add_node(node['id'], **node['data'])
    return G


def jit_data(G, indent=None):
    """Return data in JIT JSON format.

    Parameters
    ----------
    G : NetworkX Graph

    Returns
    -------
    data: JIT JSON string
    """
    json_graph = []
    for node in G.nodes():
        json_node = {
            "id": node,
            "name": node
        }
        # node data
        if G.node[node]:
            json_node["data"] = G.node[node]
        else:
            json_node["data"] = {}
        # adjacencies
        if G[node]:
            json_node["adjacencies"] = []
            for neighbour in G[node]:
                adjacency = {
                    "nodeTo": neighbour,
                }
                # adjacency data
                if G.edge[node][neighbour]:
                    adjacency["data"] = G.edge[node][neighbour]
                else:
                    adjacency["data"] = {}
                json_node["adjacencies"].append(adjacency)
        json_graph.append(json_node)
    return json.dumps(json_graph, indent=indent)
