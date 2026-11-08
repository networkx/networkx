import json

import networkx as nx
from networkx.utils import open_file

__all__ = ["write_cytoscape", "read_cytoscape"]


@open_file(1, mode="wb")
def write_cytoscape(G, path, name="name", id="id", **kwargs):
    """Write G in Cytoscape JSON format to path.

    This function uses Python's json module.

    Parameters
    ----------
    G : graph
       A networkx graph
    path : file or string
       File or filename to write.
       Filenames ending in .gz or .bz2 will be compressed.
    name : string
        A string which is mapped to the 'name' node element in cyjs format.
        Must not have the same value as `ident`.
    ident : string
        A string which is mapped to the 'id' node element in cyjs format.
        Must not have the same value as `name`.

    Raises
    ------
    NetworkXError
        If the values for `name` and `ident` are identical.

    See Also
    --------
    read_cytoscape: read a graph from a Cytoscape JSON file (cyjs)
    cytoscape_data: convert a NetworkX graph to a Python dictionary following Cytcoscape data structure.

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_cytoscape(G, "fourpath.cyjs")
    """
    import json

    data = nx.json_graph.cytoscape_data(G, name=name, ident=id)
    path.write(json.dumps(data, **kwargs).encode("ascii"))


@open_file(0, mode="rb")
@nx._dispatchable(graphs=None, returns_graph=True)
def read_cytoscape(path, name="name", ident="ident", **kwargs):
    """Read graph in GML format from `path`.

    Parameters
    ----------
    path : file or string
        Filename or file handle to read.
        Filenames ending in .gz or .bz2 will be decompressed.
    name : string
        A string which is mapped to the 'name' node element in cyjs format.
        Must not have the same value as `ident`.
    ident : string
        A string which is mapped to the 'id' node element in cyjs format.
        Must not have the same value as `name`.

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
    write_cytoscape: write a graph to a Cytoscape JSON file (cyjs).
    cytoscape_graph: convert a dictionary following Cytoscape data structure to a graph.

    References
    ----------
    .. [1] Cytoscape user's manual:
       http://manual.cytoscape.org/en/stable/index.html

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_cytoscape(G, "test.cyjs")
    >>> H = nx.read_cytoscape("test.cyjs")
    >>> H.nodes
    NodeView((0, 1, 2, 3))
    """

    data = json.load(path, **kwargs)
    return nx.json_graph.cytoscape_graph(data, name=name, ident=ident)
