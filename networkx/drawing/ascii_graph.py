"""
******
ascii graph
******

Function to display Digraph in ascii format
(In CLI or other text based kernels)

Warning: Displays only Digraphs:
└── A
    ├── B
    │   └── D
    └── C
        ├── E
        ├── F
        └── G

For Cyclic graph, will show the cycle
Cycle 1: A -> C -> G
Cycle 2: B -> G
...

"""
import networkx as nx

__all__ = ["digraph_ascii"]


def digraph_ascii(graph):
    """Display a directed graph in ASCII/Textual format

    Parameters
    ----------
    graph : NetworkX DiGraph or list of nodes

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edges_from([('A','B'),('A','C'),('B','D'),])
    >>> digraph_ascii(G)

    Notes
    -----
    - This function can handle both acyclic and cyclic Digraphs.
    - For cyclic Digraphs, it will display the cycles separately.

    """

    def print_digraph_ascii(person, prefix="", last_child=False):
        print(prefix + ("└── " if last_child else "├── ") + str(person))
        if person in graph:
            children = list(graph[person])
            for i, child in enumerate(children):
                print_digraph_ascii(
                    child,
                    prefix + ("    " if last_child else "│   "),
                    i == len(children) - 1,
                )

    if not isinstance(graph, nx.DiGraph):
        return

    cycles = list(nx.simple_cycles(graph))
    if cycles:
        print("Cycles in the graph:")
        for i, cycle in enumerate(cycles, start=1):
            cycle_str = " -> ".join(map(str, cycle))
            print(f"Cycle {i}: {cycle_str}")
    else:
        root_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
        for i, root in enumerate(root_nodes):
            print_digraph_ascii(root, last_child=i == len(root_nodes) - 1)
