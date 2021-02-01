"""
*******
DIMACS
*******
Read and write graphs in DIMACS Format

Format
------
The DIMACS graph format is a human readable text fromat.  See
http://archive.dimacs.rutgers.edu/pub/challenge/graph/doc/ccformat.dvi
"""

import networkx as nx
from networkx.utils import open_file

__all__ = [
    "parse_dimacs",
    "read_dimacs",
    "write_dimacs"
]


def parse_dimacs(lines, create_using=None):
    g = create_using if create_using else nx.Graph()

    expected_num_nodes = None
    expected_num_edges = None

    for line in lines:
        if len(line) > 1:
            if line.startswith('c'):
                pass
            elif line.startswith("p"):
                _, file_type, num_nodes, num_edges = line.strip().split(" ")
                expected_num_nodes = int(num_nodes)
                expected_num_edges = int(num_edges)
            elif line.startswith("n"):
                _, id_u, value_u = line.strip().split(" ")
                g.add_node(int(id_u), value=value_u)
            elif line.startswith("e"):
                _, id_u, id_v = line.strip().split(" ")
                g.add_edge(int(id_u), int(id_v))
            else:
                raise ValueError(f"Unknown line start: {line[0]}")

    assert expected_num_nodes == g.number_of_nodes(), f"{expected_num_nodes} {g.number_of_nodes()}"
    assert expected_num_edges == g.number_of_edges(), f"{expected_num_edges} {g.number_of_edges()}"
    return g


@open_file(0, mode="rb")
def read_dimacs(
        path,
        create_using=None,
        encoding="utf-8",
):
    """Read a graph from a list of edges.

    Parameters
    ----------
    path : file or string
       File or filename to read. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.

    Returns
    -------
    G : graph
       A networkx Graph or other type specified with create_using


    See Also
    --------
    parse_dimacs
    write_dimacs

    Notes
    -----
    """
    lines = (line if isinstance(line, str) else line.decode(encoding) for line in path)
    return parse_dimacs(
        lines,
        create_using=create_using,
    )


@open_file(1, mode="wb")
def write_dimacs(G, path):
    raise NotImplementedError("Writing of DIMACS not implemented yet.")
