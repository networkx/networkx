import networkx as nx

__all__ = ["cytoscape_data", "cytoscape_graph"]

_attrs = dict(name="name", ident="id")


def cytoscape_data(G, attrs=None):
    """Returns data in Cytoscape JSON format (cyjs).

    Parameters
    ----------
    G : NetworkX Graph
        The graph to convert to cytoscape format
    attrs : dict or None (default=None)
        A dictionary containing the keys 'name' and 'ident' which are mapped to
        the 'name' and 'id' node elements in cyjs format. All other keys are
        ignored. Default is `None` which results in the default mapping
        ``dict(name="name", ident="id")``.

    Returns
    -------
    data: dict
        A dictionary with cyjs formatted data.

    Raises
    ------
    NetworkXError
        If values in `attrs` are not unique.

    See Also
    --------
    cytoscape_graph - convert a dictionary in cyjs format to a graph

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> G = nx.path_graph(2)
    >>> nx.cytoscape_data(G)  # doctest: +SKIP
    {'data': [],
     'directed': False,
     'multigraph': False,
     'elements': {'nodes': [{'data': {'id': '0', 'value': 0, 'name': '0'}},
       {'data': {'id': '1', 'value': 1, 'name': '1'}}],
      'edges': [{'data': {'source': 0, 'target': 1}}]}}
    """
    if not attrs:
        attrs = _attrs
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})

    name = attrs["name"]
    ident = attrs["ident"]

    if len({name, ident}) < 2:
        raise nx.NetworkXError("Attribute names are not unique.")

    jsondata = {"data": list(G.graph.items())}
    jsondata["directed"] = G.is_directed()
    jsondata["multigraph"] = G.is_multigraph()
    jsondata["elements"] = {"nodes": [], "edges": []}
    nodes = jsondata["elements"]["nodes"]
    edges = jsondata["elements"]["edges"]

    for i, j in G.nodes.items():
        n = {"data": j.copy()}
        n["data"]["id"] = j.get(ident) or str(i)
        n["data"]["value"] = i
        n["data"]["name"] = j.get(name) or str(i)
        nodes.append(n)

    if G.is_multigraph():
        for e in G.edges(keys=True):
            n = {"data": G.adj[e[0]][e[1]][e[2]].copy()}
            n["data"]["source"] = e[0]
            n["data"]["target"] = e[1]
            n["data"]["key"] = e[2]
            edges.append(n)
    else:
        for e in G.edges():
            n = {"data": G.adj[e[0]][e[1]].copy()}
            n["data"]["source"] = e[0]
            n["data"]["target"] = e[1]
            edges.append(n)
    return jsondata


def cytoscape_graph(data, attrs=None):
    """
    Create a NetworkX graph from a dictionary in cytoscape JSON format.

    Parameters
    ----------
    data : dict
        A dictionary of data conforming to cytoscape JSON format.
    attrs : dict or None (default=None)
        A dictionary containing the keys 'name' and 'ident' which are mapped to
        the 'name' and 'id' node elements in cyjs format. All other keys are
        ignored. Default is `None` which results in the default mapping
        ``dict(name="name", ident="id")``.

    Returns
    -------
    graph : a NetworkX graph instance
        The `graph` can be an instance of `Graph`, `DiGraph`, `MultiGraph`, or
        `MultiDiGraph` depending on the input data.

    Raises
    ------
    NetworkXError
        If values in `attrs` are not unique.

    See Also
    --------
    cytoscape_data - convert a NetworkX graph to a dict in cyjs format

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> data_dict = {
    ...     'data': [],
    ...     'directed': False,
    ...     'multigraph': False,
    ...     'elements': {'nodes': [{'data': {'id': '0', 'value': 0, 'name': '0'}},
    ...       {'data': {'id': '1', 'value': 1, 'name': '1'}}],
    ...      'edges': [{'data': {'source': 0, 'target': 1}}]}
    ... }
    >>> G = nx.cytoscape_graph(data_dict)
    >>> G.name
    ''
    >>> G.nodes()
    NodeView((0, 1))
    >>> G.nodes(data=True)[0]
    {'id': '0', 'value': 0, 'name': '0'}
    >>> G.edges(data=True)
    EdgeDataView([(0, 1, {'source': 0, 'target': 1})])
    """
    if not attrs:
        attrs = _attrs
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})

    name = attrs["name"]
    ident = attrs["ident"]

    if len({ident, name}) < 2:
        raise nx.NetworkXError("Attribute names are not unique.")

    multigraph = data.get("multigraph")
    directed = data.get("directed")
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()
    graph.graph = dict(data.get("data"))
    for d in data["elements"]["nodes"]:
        node_data = d["data"].copy()
        node = d["data"]["value"]

        if d["data"].get(name):
            node_data[name] = d["data"].get(name)
        if d["data"].get(ident):
            node_data[ident] = d["data"].get(ident)

        graph.add_node(node)
        graph.nodes[node].update(node_data)

    for d in data["elements"]["edges"]:
        edge_data = d["data"].copy()
        sour = d["data"]["source"]
        targ = d["data"]["target"]
        if multigraph:
            key = d["data"].get("key", 0)
            graph.add_edge(sour, targ, key=key)
            graph.edges[sour, targ, key].update(edge_data)
        else:
            graph.add_edge(sour, targ)
            graph.edges[sour, targ].update(edge_data)
    return graph
