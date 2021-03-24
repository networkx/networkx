"""
****
ETE
****
Read and write NetworkX graphs in ETE standard tree representation format.

"ETE (Environment for Tree Exploration) is a Python programming toolkit
that assists in the automated manipulation,
analysis and visualization of phylogenetic trees.
It uses the Newick format as one of the most widely used
standard representation of trees in bioinformatics."
See http://etetoolkit.org/ for documentation.

Format
------
http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees

"""

__all__ = ["read_ete", "write_ete"]

from networkx.utils import open_file
import networkx as nx


@open_file(1, mode="w")
def write_ete(G_to_be_ete, path_for_ete_output, root_node=None):
    """Write graph G in Newick format to path.

    The Newick format is one of the most widely used
    standard representation of trees in bioinformatics [1]_.


    Parameters
    ----------
    G_to_be_ete : graph
       A NetworkX graph
    path_for_ete_output : file or string
       File or filename to write.

    Examples
    --------
    >>> G = nx.path_graph(42)
    >>> nx.write_ete(G, "test_ete.txt")

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    """
    assert nx.is_tree(
        G_to_be_ete
    ), "write_ete() requires `G_to_be_ete` be a tree: %s" % (
        "https://networkx.org/documentation/stable/reference/algorithms/tree.html"
    )

    try:
        import ete3
    except ImportError as e:
        raise ImportError("to_ete() requires ete3: http://etetoolkit.org/") from e

    if root_node is None:
        root_node = list(G_to_be_ete.nodes)[0]

    G_tree = nx.dfs_tree(G_to_be_ete, source=root_node)

    node2tree = dict()

    for node_name, node_features in G_tree.nodes(data=True):
        node2tree[node_name] = ete3.Tree(name=str(node_name))
        node2tree[node_name].add_features(**node_features)

    for parent, child in G_tree.edges:
        node2tree[parent].add_child(child=node2tree[child])

    tree = node2tree[root_node]

    path_for_ete_output.write(
        tree.write(
            features=list(tree.features - {"dist", "support"}), format_root_node=True
        )
    )


@open_file(0, mode="r")
def read_ete(path):
    """Read graph in Newick format from path.

    The Newick format is one of the most widely used
    standard representation of trees in bioinformatics [1]_.

    Parameters
    ----------
    path : file or string
       File or filename to read.

    Returns
    -------
    G : NetworkX graph

    Examples
    --------
    >>> G = nx.path_graph(42)
    >>> nx.write_ete(G, "test_ete.txt")
    >>> G = nx.read_yaml("test_ete.txt")

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    """

    try:
        import ete3
    except ImportError as e:
        raise ImportError("to_ete() requires ete3: http://etetoolkit.org/") from e

    file = [line for line in path]

    tree = ete3.Tree(file[0])

    G = nx.Graph()

    for tree_node in tree.iter_search_nodes():
        node_name = tree_node.name
        node_features = {
            k: getattr(tree_node, k) for k in tree_node.features - {"dist", "support"}
        }

        G.add_node(node_name, **node_features)

    queue = [tree]

    while queue:
        parent = queue.pop(0)

        for child in parent.children:
            queue.append(child)
            G.add_edge(parent.name, child.name)

    return G
