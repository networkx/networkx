import networkx as nx
from networkx.readwrite.json_graph.node_link import _to_tuple

__all__ = ["cytoscape_data", "cytoscape_graph"]


def cytoscape_data(G, name="name", ident="id"):
    """Returns data in Cytoscape JSON format (cyjs).

    Parameters
    ----------
    G : NetworkX Graph
        The graph to convert to cytoscape format
    name : string
        A string which is mapped to the 'name' node element in cyjs format.
        Must not have the same value as `ident`.
    ident : string
        A string which is mapped to the 'id' node element in cyjs format.
        Must not have the same value as `name`.

    Returns
    -------
    data: dict
        A dictionary with cyjs formatted data.

    Raises
    ------
    NetworkXError
        If the values for `name` and `ident` are identical, or if node IDs
        are not unique after conversion to strings.

    See Also
    --------
    cytoscape_graph: convert a dictionary in cyjs format to a graph

    Notes
    -----
    Node IDs are strings, and edge sources and targets refer to these IDs.
    The original NetworkX node labels are stored in each node's ``value``.
    If distinct labels have the same string representation, assign unique
    node attributes using `ident`.

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> from pprint import pprint
    >>> G = nx.path_graph(2)
    >>> cyto_data = nx.cytoscape_data(G)
    >>> pprint(cyto_data, sort_dicts=False)
    {'data': [],
     'directed': False,
     'multigraph': False,
     'elements': {'nodes': [{'data': {'id': '0', 'value': 0, 'name': '0'}},
                            {'data': {'id': '1', 'value': 1, 'name': '1'}}],
                  'edges': [{'data': {'source': '0', 'target': '1'}}]}}

    The :mod:`json` package can be used to serialize the resulting data

    >>> import io, json
    >>> with io.StringIO() as fh:  # replace io with `open(...)` to write to disk
    ...     json.dump(cyto_data, fh)
    ...     fh.seek(0)  # doctest: +SKIP
    ...     print(fh.getvalue()[:64])  # View the first 64 characters
    {"data": [], "directed": false, "multigraph": false, "elements":

    """
    if name == ident:
        raise nx.NetworkXError("name and ident must be different.")

    jsondata = {"data": list(G.graph.items())}
    jsondata["directed"] = G.is_directed()
    jsondata["multigraph"] = G.is_multigraph()
    jsondata["elements"] = {"nodes": [], "edges": []}
    nodes = jsondata["elements"]["nodes"]
    edges = jsondata["elements"]["edges"]
    node_ids = {}
    seen_ids = set()

    for i, j in G.nodes.items():
        n = {"data": j.copy()}
        node_id = str(j.get(ident) or i)
        if node_id in seen_ids:
            raise nx.NetworkXError("Cytoscape node IDs must be unique.")
        seen_ids.add(node_id)
        node_ids[i] = node_id
        n["data"]["id"] = node_id
        n["data"]["value"] = i
        n["data"]["name"] = j.get(name) or str(i)
        nodes.append(n)

    if G.is_multigraph():
        for e in G.edges(keys=True):
            n = {"data": G.adj[e[0]][e[1]][e[2]].copy()}
            n["data"]["source"] = node_ids[e[0]]
            n["data"]["target"] = node_ids[e[1]]
            n["data"]["key"] = e[2]
            edges.append(n)
    else:
        for e in G.edges():
            n = {"data": G.adj[e[0]][e[1]].copy()}
            n["data"]["source"] = node_ids[e[0]]
            n["data"]["target"] = node_ids[e[1]]
            edges.append(n)
    return jsondata


@nx._dispatchable(graphs=None, returns_graph=True)
def cytoscape_graph(data, name="name", ident="id", *, legacy=False):
    """
    Create a NetworkX graph from a dictionary in cytoscape JSON format.

    Parameters
    ----------
    data : dict
        A dictionary of data conforming to cytoscape JSON format.
    name : string
        A string which is mapped to the 'name' node element in cyjs format.
        Must not have the same value as `ident`.
    ident : string
        A string which is mapped to the 'id' node element in cyjs format.
        Must not have the same value as `name`.
    legacy : bool, optional
        If True, interpret edge sources and targets as node labels rather
        than node IDs. Use this for older NetworkX exports when node labels
        and IDs overlap. The default is False. See Notes for automatic
        detection of older exports.

    Returns
    -------
    graph : a NetworkX graph instance
        The `graph` can be an instance of `Graph`, `DiGraph`, `MultiGraph`, or
        `MultiDiGraph` depending on the input data.

    Raises
    ------
    NetworkXError
        If the `name` and `ident` attributes are identical.

    See Also
    --------
    cytoscape_data: convert a NetworkX graph to a dict in cyjs format

    Notes
    -----
    Edge sources and targets are resolved through the node IDs to the
    original node labels stored in ``value``. If an endpoint matches a node
    label but no node ID, all endpoints are interpreted as node labels,
    as in older NetworkX exports. Otherwise, endpoints that do not match
    a node ID are used directly. Node entries without an ID are supported.

    When every endpoint matches a node ID, older exports cannot always be
    distinguished from current exports. Pass ``legacy=True`` to read such
    older exports using node labels, even when they match another node's ID.
    Lists in node labels are converted to tuples, including nested lists.

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> data_dict = {
    ...     "data": [],
    ...     "directed": False,
    ...     "multigraph": False,
    ...     "elements": {
    ...         "nodes": [
    ...             {"data": {"id": "0", "value": 0, "name": "0"}},
    ...             {"data": {"id": "1", "value": 1, "name": "1"}},
    ...         ],
    ...         "edges": [{"data": {"source": "0", "target": "1"}}],
    ...     },
    ... }
    >>> G = nx.cytoscape_graph(data_dict)
    >>> G.name
    ''
    >>> G.nodes()
    NodeView((0, 1))
    >>> G.nodes(data=True)[0]
    {'id': '0', 'value': 0, 'name': '0'}
    >>> G.edges(data=True)
    EdgeDataView([(0, 1, {'source': '0', 'target': '1'})])
    """
    if name == ident:
        raise nx.NetworkXError("name and ident must be different.")

    multigraph = data.get("multigraph")
    directed = data.get("directed")
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()
    graph.graph = dict(data.get("data"))
    node_ids = {}
    for d in data["elements"]["nodes"]:
        node_data = d["data"].copy()
        node = _to_tuple(d["data"]["value"])
        if "id" in d["data"]:
            node_ids[str(d["data"]["id"])] = node

        if d["data"].get(name):
            node_data[name] = d["data"].get(name)
        if d["data"].get(ident):
            node_data[ident] = d["data"].get(ident)

        graph.add_node(node)
        graph.nodes[node].update(node_data)

    # Resolve all endpoints consistently when reading older NetworkX exports.
    if not legacy:
        legacy = any(
            endpoint in graph and endpoint not in node_ids
            for d in data["elements"]["edges"]
            for endpoint in (
                _to_tuple(d["data"]["source"]),
                _to_tuple(d["data"]["target"]),
            )
        )

    for d in data["elements"]["edges"]:
        edge_data = d["data"].copy()
        sour = _to_tuple(d["data"]["source"])
        targ = _to_tuple(d["data"]["target"])
        if not legacy:
            sour = node_ids.get(sour, sour)
            targ = node_ids.get(targ, targ)
        if multigraph:
            key = d["data"].get("key", 0)
            graph.add_edge(sour, targ, key=key)
            graph.edges[sour, targ, key].update(edge_data)
        else:
            graph.add_edge(sour, targ)
            graph.edges[sour, targ].update(edge_data)
    return graph
