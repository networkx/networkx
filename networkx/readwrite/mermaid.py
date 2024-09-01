"""
****************
Mermaid diagrams
****************
Read and write NetworkX graphs in Mermaid format.

Mermaid is a collection of text-based diagrams that are well suited
to be integrated with markdown and get visually rendered by JavaScript.

While Mermaid has plenty of diagram formats [1], here in NetworkX
we only support flowcharts [2]

[1] https://mermaid.js.org/intro/#diagram-types

[2] https://mermaid.js.org/syntax/flowchart.html

You can read or write Mermaid flowcharts.

For example, a directed graph might be formatted::

    flowchart LR
        A --> B
        A --> C
        B --> D
        C --> D
"""

__all__ = [
    "generate_mermaid",
    "write_mermaid",
    "parse_mermaid",
    "read_mermaid",
]

import networkx as nx
from networkx.utils import open_file


def generate_mermaid(G):
    """Generate a single line of the graph G in mermaid flowchart format.

    Parameters
    ----------
    G : NetworkX graph

    Yields
    ------
    lines : string
        Lines of data in mermaid flowchart format.

    Examples
    --------
    >>> G = nx.lollipop_graph(4, 3)
    >>> for line in nx.generate_mermaid(G):
    ...     print(line)
    0 --> 1
    0 --> 2
    0 --> 3
    1 --> 2
    1 --> 3
    2 --> 3
    3 --> 4
    4 --> 5
    5 --> 6

    See Also
    --------
    write_mermaid, read_mermaid
    """
    for u, v in G.edges(data=False):
        yield f"{u} --> {v}"


@open_file(1, mode="wb")
def write_mermaid(G, path, encoding="utf-8"):
    """Write graph as a mermaid flowchart.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode. Filenames ending in .gz or .bz2 will be compressed.
    encoding: string, optional
       Specify which encoding to use when writing file.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_mermaid(G, "test.mermaid")
    >>> G = nx.path_graph(4)
    >>> fh = open("test.mermaid", "wb")
    >>> nx.write_mermaid(G, fh)
    >>> nx.write_mermaid(G, "test.mermaid.gz")

    See Also
    --------
    read_mermaid
    """
    path.write("flowchart\n".encode(encoding))
    for line in generate_mermaid(G):
        line = f"    {line}\n"
        path.write(line.encode(encoding))


@nx._dispatchable(graphs=None, returns_graph=True)
def parse_mermaid(lines):
    """Parse lines of a mermaid flowchart representation of a graph.

    Parameters
    ----------
    lines : list or iterator of strings
        Input data in mermaid flowchart format

    Returns
    -------
    G: NetworkX Graph
        The graph corresponding to lines

    Examples
    --------
    Mermaid flowchart:

    >>> lines = ["flowchart", "A --> B", "A --> C", "B --> C"]
    >>> G = nx.parse_mermaid(lines)
    >>> list(G)
    ['A', 'B', 'C']
    >>> list(G.edges())
    [('A', 'B'), ('A', 'C'), ('B', 'C')]
    """
    G = nx.empty_graph(0)
    skip_lines = True
    for line in lines:
        if "flowchart" in line:
            skip_lines = False
            continue
        if skip_lines:
            continue
        if "-->" in line:
            parts = line.strip().split(" ")
            u = parts[0]
            v = parts[-1]
            G.add_edge(u, v)
    return G


@open_file(0, mode="rb")
@nx._dispatchable(graphs=None, returns_graph=True)
def read_mermaid(path, encoding="utf-8"):
    """Read a graph from a list of edges.

    Parameters
    ----------
    path : file or string
       File or filename to read. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A networkx Graph

    Examples
    --------
    >>> nx.write_mermaid(nx.path_graph(4), "test.mermaid")
    >>> G = nx.read_mermaid("test.mermaid")

    >>> fh = open("test.mermaid", "rb")
    >>> G = nx.read_mermaid(fh)
    >>> fh.close()

    See Also
    --------
    write_mermaid
    """
    lines = (line if isinstance(line, str) else line.decode(encoding) for line in path)
    return parse_mermaid(lines)
