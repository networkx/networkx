#    Copyright (C) 2011-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

"""
Read and write NetworkX graphs as JavaScript InfoVis Toolkit (JIT) format JSON.

See the `JIT documentation`_ for more examples.

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
.. _JIT documentation: http://thejit.org
"""

import json
import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ['jit_graph', 'jit_data']

def jit_graph(data):
    """Read a graph from JIT JSON.

    Parameters
    ----------
    data : JSON Graph Object

    Returns
    -------
    G : NetworkX Graph
    """
    G = nx.Graph()
    for node in data:
        G.add_node(node['id'], **node['data'])
        if node.get('adjacencies') is not None:
            for adj in node['adjacencies']:
                G.add_edge(node['id'], adj['nodeTo'], **adj['data'])
    return G


@not_implemented_for('multigraph')
def jit_data(G, indent=None):
    """Return data in JIT JSON format.

    Parameters
    ----------
    G : NetworkX Graph

    indent: optional, default=None
        If indent is a non-negative integer, then JSON array elements and object
        members will be pretty-printed with that indent level. An indent level
        of 0, or negative, will only insert newlines. None (the default) selects
        the most compact representation.

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
        json_node["data"] = G.node[node]
        # adjacencies
        if G[node]:
            json_node["adjacencies"] = []
            for neighbour in G[node]:
                adjacency = {
                    "nodeTo": neighbour,
                }
                # adjacency data
                adjacency["data"] = G.edge[node][neighbour]
                json_node["adjacencies"].append(adjacency)
        json_graph.append(json_node)
    return json.dumps(json_graph, indent=indent)
