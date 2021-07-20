"""Read and write graphs in GDF format.

GDF (GUESS Data Format) is a simple file format for network files. It is
supported by Gephi and GUESS, among others, and due to its simplicity it
is used as a graph export format by research software like DMI-TCAT and
4CAT.

Format
------
GDF is a plain-text format similar to CSV.  See
https://gephi.org/users/supported-graph-formats/gdf-format/ for the
specification and examples.
"""
import networkx as nx
from networkx.utils import open_file
import re


def gdf_escape(value):
    """Escape a value for inclusion in a GDF file

    Parameters
    ----------
    value
      A value to escape for inclusion in a GDF file

    Returns
    -------
      The value, as an empty string if empty; as TRUE or FALSE (as strings) if
      a boolean; as a string representation if an integer; or as a string
      wrapped in single quotes with any single quotes inside the string slash-
      escaped in other cases.

    """
    if value == "" or value is None:
        return ""

    if type(value) is bool:
        return str(value).upper()

    if type(value) is int:
        return str(value)

    return "'" + str(value).replace("'", "\\'").replace("\n", "\\n") + "'"


def gdf_split(line, types=None):
    """Parse a node or edge definition from a GDF file

    Parses a line of values. Since values may be wrapped in single quotes, we
    cannot simply split by commas. Instead, this implements a simple parser
    that ignores single quotes unless escaped, and only splits on commas if
    they are outside single quotes.

    Parameters
    ----------
    line : str
      Line of node or edge data to parse
    types : list
      A list of Gephi types in the same order as the values to be parsed, which
      will be used to convert the values to the required type if possible. If
      omitted, all values will be returned as strings. Values that cannot be
      converted to the given type will be replaced with `None`.

    Returns
    -------
    values : list
      A list of parsed values, as strings.

    """
    buffer = ""
    values = []
    escape_open = False

    while line:
        character = line[0]
        line = line[1:]

        if character == "'":
            if buffer and buffer[-1] == "\\":
                buffer = buffer[:-1]
            else:
                escape_open = not escape_open
                continue

        if character == "," and not escape_open:
            values.append(buffer)
            buffer = ""
            continue

        buffer += character

    if buffer:
        values.append(buffer)

    values = [value.strip() for value in values]

    # convert to the required type
    # this is sort of done on a best-effort bases - if the conversion fails,
    # `None` is used instead. Unknown types are left as strings.
    if types and len(types) == len(values):
        for i, gdftype in enumerate(types):
            if gdftype == "BOOLEAN":
                values[i] = values[i].lower() == "true"
            elif gdftype == "INTEGER" or gdftype.endswith("INT"):
                try:
                    values[i] = int(values[i])
                except ValueError:
                    values[i] = None
            elif gdftype in ("FLOAT", "DOUBLE"):
                try:
                    values[i] = float(values[i])
                except ValueError:
                    values[i] = None

    return values


@open_file(1, mode="wb")
def write_gdf(G, path, encoding="utf-8"):
    """Write a NetworkX network as a GDF file to a given file path

    Parameters
    ----------
    G : graph
      A NetworkX graph
    path : file or string
       File or filename to write.
    encoding : string (optional)
       Encoding for text data.

    Notes
    ----------
    If the provided graph is a DiGraph or MultiDiGraph, the attribute
    `directed` is set to `TRUE` for all edges. Otherwise, it is absent unless
    it is specified explicitly in the edge's data.

    If nodes have a `name` attribute in their data, the value of that attribute
    is used as the node name in the GDF file. Otherwise, all nodes are given a
    unique integer as their name.
    """

    def write_schema(component, path, columns):
        schema = ",".join(columns)
        path.write(("%sdef>%s\n" % (component, schema)).encode(encoding))

    # determine node attributes to include
    node_attributes = set()
    name_map = {}
    directed = type(G) in (nx.DiGraph, nx.MultiDiGraph)

    for index, item_data in G.nodes(data=True):
        node_attributes |= set(item_data.keys())
        name_map[index] = item_data.get("name", index)

    node_attributes.discard("name")
    node_attributes = ["name", *sorted(node_attributes)]
    write_schema("node", path, node_attributes)

    # write nodes
    for index, item_data in G.nodes(data=True):
        if "name" in item_data:
            del item_data["name"]

        node_values = [gdf_escape(item_data.get(key)) for key in sorted(node_attributes) if key != "name"]
        node_values.insert(0, gdf_escape(name_map[index]))
        path.write((",".join(node_values) + "\n").encode(encoding))

    # determine edge attributes to include
    edge_attributes = set()
    for from_index, to_index, edge_data in G.edges(data=True):
        edge_attributes |= set(edge_data.keys())

    edge_attributes.discard("node1")
    edge_attributes.discard("node2")
    if directed:
        edge_attributes.add("directed")

    edge_attributes = ["node1", "node2", *sorted(edge_attributes)]
    write_schema("edge", path, edge_attributes)

    # write edges
    for from_index, to_index, edge_data in G.edges(data=True):
        if directed:
            edge_data["directed"] = True

        edge_values = [gdf_escape(edge_data.get(key)) for key in sorted(edge_attributes) if key not in ("node1", "node2")]
        edge_values.insert(0, gdf_escape(name_map[to_index]))
        edge_values.insert(0, gdf_escape(name_map[from_index]))
        path.write((",".join(edge_values) + "\n").encode(encoding))

    # done!


@open_file(0, mode="r")
def read_gdf(path, encoding="utf-8"):
    """Read graph in GraphML format from a reader object

    Notes
    ----------
    The returned graph can be a Graph or a DiGraph. For it to be a DiGraph, all
    edges must have a `directed` attribute, and the attribute must be set to
    `True` for all of the edges.

    Parameters
    ----------
    path : generator
      A generator that yields a GDF network line by line, e.g. an open file
      handler.

    Returns
    -------
    graph : NetworkX graph
      The reconstructed graph. Any node and edge attributes, including
      'name' for nodes and 'node1' and 'node2' for edges, are included as node
      and edge data. Node IDs are not inferred from the GDF file, but will be
      internally consistent (i.e. the edges will use the IDs for the
      corresponding nodes, and so on).

    """
    reading_mode = None
    node_attributes = []
    node_types = []
    edge_attributes = []
    edge_types = []

    G = nx.Graph()
    line_num = 0
    name_map = {}
    node_index = 1

    for line in path:
        line_num += 1

        if line.startswith("nodedef>"):
            # read node schema
            # *if* nodes are defined as having a type, store these as well so
            # they can be used for parsing the values later
            reading_mode = "node"
            nodedef = re.sub(r"^nodedef>", "", line).strip()
            for attribute in nodedef.split(","):
                attribute = attribute.split(" ")
                node_attributes.append(attribute[0])

                if len(attribute) > 1:
                    node_types.append(attribute[1])

        elif line.startswith("edgedef>"):
            # read edge schema
            # identical to the node schema
            reading_mode = "edge"
            edgedef = re.sub(r"^edgedef>", "", line).strip()

            for attribute in edgedef.split(","):
                attribute = attribute.split(" ")
                edge_attributes.append(attribute[0])

                if len(attribute) > 1:
                    edge_types.append(attribute[1])

        elif reading_mode == "node":
            # read node definitions
            values = gdf_split(line, node_types)

            if len(values) != len(node_attributes):
                raise ImportError("Cannot parse GDF file: not all attributes specified for node on line %i" % line_num)

            name = values[0]
            name_map[name] = node_index

            attributes = {node_attributes[i]: value for i, value in enumerate(values)}
            G.add_nodes_from([(node_index, attributes)])
            node_index += 1

        elif reading_mode == "edge":
            # read edge definitions
            values = gdf_split(line, edge_types)

            if len(values) != len(edge_attributes):
                raise ImportError("Cannot parse GDF file: not all attributes specified for edge on line %i" % line_num)

            node1 = values[0]
            node2 = values[1]

            if node1 not in name_map or node2 not in name_map:
                raise ImportError("Cannot parse GDF file: edge references undefined node on line %i" % line_num)

            attributes = {edge_attributes[i]: value for i, value in enumerate(values)}
            G.add_edges_from([(name_map[node1], name_map[node2], attributes)])

    # we can only know if the graph is directed *after* parsing the whole file
    # since before that we don't know if all edges have their 'directed'
    # attribute set to 'true', if they have one - so if that is the case, we
    # re-create the graph here as a DiGraph
    is_directed = False
    if "directed" in edge_attributes:
        for node1, node2, edge in G.edges(data=True):
            is_directed = str(edge["directed"]).lower() == "true"

    if is_directed:
        DiG = nx.DiGraph()
        DiG.add_nodes_from(G.nodes(data=True))
        DiG.add_edges_from(G.edges(data=True))
        return DiG
    else:
        return G
