"""
*******
DIMACS
*******
Read and write graphs in DIMACS Format

Format
------
The DIMACS graph format is a human readable text format.  See
http://archive.dimacs.rutgers.edu/pub/challenge/graph/doc/ccformat.dvi
"""

import networkx as nx
from networkx.utils import open_file

__all__ = ["parse_dimacs", "read_dimacs", "generate_dimacs", "write_dimacs"]


class DimacsValidationError(Exception):
    pass


def parse_dimacs(lines, create_using=None):
    """Parse lines of a DIMACS representation of a graph.

    Parameters
    ----------
    lines : list or iterator of strings
        Input data in edgelist format

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using

    See Also
    --------
    read_dimacs
    """
    g = nx.empty_graph(0, create_using=create_using)

    expected_num_nodes = None
    expected_num_edges = None

    for line in lines:
        if len(line) > 1:
            if line.startswith("c"):
                pass
            elif line.startswith("p"):
                # The p line contains meta information about the graph
                _, file_type, num_nodes, num_edges = line.strip().split(" ")
                expected_num_nodes = int(num_nodes)
                expected_num_edges = int(num_edges)
            elif line.startswith("n"):
                line_split = line.strip().split(" ")
                if len(line_split) == 3:
                    _, id_u, value_u = line_split
                    g.add_node(int(id_u), value=value_u)
                elif len(line_split) == 2:
                    _, id_u = line_split
                    # Add node with default value of 1
                    g.add_node(int(id_u), value=1)
                else:
                    raise ValueError(f"Found node line of illegal format: {line}")
            elif line.startswith("e"):
                _, id_u, id_v = line.strip().split(" ")
                g.add_edge(int(id_u), int(id_v))
            else:
                raise ValueError(f"Unknown line start: {line[0]}")

    if not expected_num_nodes == g.number_of_nodes():
        raise DimacsValidationError(
            f"Expected to read {expected_num_nodes} nodes but found {g.number_of_nodes()}"
        )
    if not expected_num_edges == g.number_of_edges():
        raise DimacsValidationError(
            f"Expected to read {expected_num_edges} edges but found {g.number_of_edges()}"
        )

    return g


@open_file(0, mode="rb")
def read_dimacs(
    path,
    create_using=None,
    encoding="utf-8",
):
    """Read a graph from a file in DIMACS format.

    Parameters
    ----------
    path : string or file
       Filename or file handle to read.
       Filenames ending in .gz or .bz2 will be uncompressed.

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using


    See Also
    --------
    parse_dimacs
    write_dimacs
    """
    lines = (line if isinstance(line, str) else line.decode(encoding) for line in path)
    return parse_dimacs(
        lines,
        create_using=create_using,
    )


def generate_dimacs(G):
    """Generate a single line of the graph G in DIMACS format.

    Parameters
    ----------
    G : graph
        A networkx graph.

    Returns
    -------
    lines : string
        Lines of data in DIMACS format.

    See Also
    --------
    write_dimacs
    """
    yield f"p edge {G.number_of_nodes()} {G.number_of_edges()}"
    for node, data in G.nodes(data=True):
        if data and data["value"]:
            yield f"n {node} {data['value']}"
    for u, v in G.edges:
        yield f"e {u} {v}"


@open_file(1, mode="wb")
def write_dimacs(G, path, encoding="utf-8"):
    """Write a graph as a file in DIMACS format.

    Parameters
    ----------
    G : graph
        A networkx graph.
    path : file or string
       File or filename to read. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    encoding: string, optional
       Specify which encoding to use when writing file.


    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using

    See Also
    --------
    generate_dimacs
    read_dimacs
    """
    for line in generate_dimacs(G):
        line += "\n"
        path.write(line.encode(encoding))
