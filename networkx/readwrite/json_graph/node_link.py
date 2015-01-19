#    Copyright (C) 2011-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from itertools import chain, count
import json
import networkx as nx
from networkx.utils import make_str
__author__ = """Aric Hagberg <hagberg@lanl.gov>"""
__all__ = ['node_link_data', 'node_link_graph']


_attrs = dict(id='id', source='source', target='target', key='key')


def node_link_data(G, attrs=_attrs):
    """Return data in node-link format that is suitable for JSON serialization
    and use in Javascript documents.

    Parameters
    ----------
    G : NetworkX graph

    attrs : dict
        A dictionary that contains four keys 'id', 'source', 'target' and
        'key'. The corresponding values provide the attribute names for storing
        NetworkX-internal graph data. The values should be unique. Default
        value:
        :samp:`dict(id='id', source='source', target='target', key='key')`.

        If some user-defined graph data use these attribute names as data keys,
        they may be silently dropped.

    Returns
    -------
    data : dict
       A dictionary with node-link formatted data.

    Raises
    ------
    NetworkXError
        If values in attrs are not unique.

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.Graph([(1,2)])
    >>> data = json_graph.node_link_data(G)

    To serialize with json

    >>> import json
    >>> s = json.dumps(data)

    Notes
    -----
    Graph, node, and link attributes are stored in this format. Note that
    attribute keys will be converted to strings in order to comply with
    JSON.

    The default value of attrs will be changed in a future release of NetworkX.

    See Also
    --------
    node_link_graph, adjacency_data, tree_data
    """
    multigraph = G.is_multigraph()
    id_ = attrs['id']
    source = attrs['source']
    target = attrs['target']
    # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
    key = None if not multigraph else attrs['key']
    if len(set([source, target, key])) < 3:
        raise nx.NetworkXError('Attribute names are not unique.')
    mapping = dict(zip(G, count()))
    data = {}
    data['directed'] = G.is_directed()
    data['multigraph'] = multigraph
    data['graph'] = G.graph
    data['nodes'] = [dict(chain(G.node[n].items(), [(id_, n)])) for n in G]
    if multigraph:
        data['links'] = [
            dict(chain(d.items(),
                       [(source, mapping[u]), (target, mapping[v]), (key, k)]))
            for u, v, k, d in G.edges_iter(keys=True, data=True)]
    else:
        data['links'] = [
            dict(chain(d.items(),
                       [(source, mapping[u]), (target, mapping[v])]))
            for u, v, d in G.edges_iter(data=True)]

    return data


def node_link_graph(data, directed=False, multigraph=True, attrs=_attrs):
    """Return graph from node-link data format.

    Parameters
    ----------
    data : dict
        node-link formatted graph data

    directed : bool
        If True, and direction not specified in data, return a directed graph.

    multigraph : bool
        If True, and multigraph not specified in data, return a multigraph.

    attrs : dict
        A dictionary that contains four keys 'id', 'source', 'target' and
        'key'. The corresponding values provide the attribute names for storing
        NetworkX-internal graph data. Default value:
        :samp:`dict(id='id', source='source', target='target', key='key')`.

    Returns
    -------
    G : NetworkX graph
       A NetworkX graph object

    Examples
    --------
    >>> from networkx.readwrite import json_graph
    >>> G = nx.Graph([(1,2)])
    >>> data = json_graph.node_link_data(G)
    >>> H = json_graph.node_link_graph(data)

    Notes
    -----
    The default value of attrs will be changed in a future release of NetworkX.


    See Also
    --------
    node_link_data, adjacency_data, tree_data
    """
    multigraph = data.get('multigraph', multigraph)
    directed = data.get('directed', directed)
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()
    id_ = attrs['id']
    source = attrs['source']
    target = attrs['target']
    # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
    key = None if not multigraph else attrs['key']
    mapping = []
    graph.graph = data.get('graph', {})
    c = count()
    for d in data['nodes']:
        node = d.get(id_, next(c))
        mapping.append(node)
        nodedata = dict((make_str(k), v) for k, v in d.items() if k != id_)
        graph.add_node(node, **nodedata)
    for d in data['links']:
        src = d[source]
        tgt = d[target]
        if not multigraph:
            edgedata = dict((make_str(k), v) for k, v in d.items()
                            if k != source and k != target)
            graph.add_edge(mapping[src], mapping[tgt], **edgedata)
        else:
            ky = d.get(key, None)
            edgedata = dict((make_str(k), v) for k, v in d.items()
                            if k != source and k != target and k != key)
            graph.add_edge(mapping[src], mapping[tgt], ky, **edgedata)
    return graph
