"""
****
ETE
****
Read and write NetworkX graphs in the New Hampshire Newick format.

"ETE (Environment for Tree Exploration) is a Python programming toolkit
that assists in the automated manipulation,
analysis and visualization of phylogenetic trees.

It uses the New Hampshire Newick format as one of the most widely used
standard representation of trees in bioinformatics."

See http://etetoolkit.org/ for documentation.

Format
------
http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees

"""

__all__ = ["to_ete", "from_ete", "write_ete", "read_ete"]

import networkx as nx
from networkx.utils import open_file, deque


def to_ete(G):
    """Returns a ETE Tree from NetworkX arborescence [3]_ G.

    ETE (Environment for Tree Exploration) is a Python programming toolkit
    that assists in the automated manipulation,
    analysis and visualization of phylogenetic trees [2]_.

    It uses the New Hampshire Newick format as one of the most widely used
    standard representation of trees in bioinformatics [1]_.


    Parameters
    ----------
    G : NetworkX arborescence

    Returns
    -------
    T : ETE Tree

    Examples
    --------
    >>> G = nx.path_graph(42)
    >>> T = nx.to_ete(G)

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    .. [3] https://networkx.org/documentation/stable//reference/algorithms/tree.html#tree
    """
    if not nx.is_arborescence(G):
        raise ValueError(f"Input graph {G} must be an arborescence.")

    try:
        import ete3
    except ImportError as e:
        raise ImportError("to_ete() requires ete3: http://etetoolkit.org/") from e

    node2tree = dict()

    for node_name, node_features in G.nodes(data=True):
        node2tree[node_name] = ete3.Tree(name=node_name)
        node2tree[node_name].add_features(**node_features)

    root_node = [n for n, d in G.in_degree() if d == 0][0]

    queue = deque([root_node])

    while queue:
        parent = queue.popleft()

        for child in G[parent]:
            queue.append(child)
            node2tree[parent].add_child(node2tree[child])

    return node2tree[root_node]


def from_ete(T):
    """Returns a NetworkX arborescence [3]_ from ETE Tree.

    ETE (Environment for Tree Exploration) is a Python programming toolkit
    that assists in the automated manipulation,
    analysis and visualization of phylogenetic trees [2]_.

    It uses the New Hampshire Newick format as one of the most widely used
    standard representation of trees in bioinformatics [1]_.

    Parameters
    ----------
    T : ETE Tree

    Returns
    -------
    G : NetworkX arborescence

    Examples
    --------
    >>> T = nx.to_ete(nx.path_graph(42))
    >>> G = nx.from_ete(T)

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    .. [3] https://networkx.org/documentation/stable//reference/algorithms/tree.html#tree
    """
    try:
        import ete3
    except ImportError as e:
        raise ImportError("to_ete() requires ete3: http://etetoolkit.org/") from e

    G = nx.DiGraph()

    for tree_node in T.iter_search_nodes():
        node_name = tree_node.name
        node_features = {
            k: getattr(tree_node, k) for k in tree_node.features - {"dist", "support"}
        }

        G.add_node(node_name, **node_features)

    queue = deque([T])

    while queue:
        parent = queue.popleft()

        for child in parent.children:
            queue.append(child)
            G.add_edge(parent.name, child.name)

    return G


@open_file(1, mode="w")
def write_ete(G, path_for_ete_output):
    """Write NetworkX arborescence [3]_ G in the New Hampshire Newick format.

    ETE (Environment for Tree Exploration) is a Python programming toolkit
    that assists in the automated manipulation,
    analysis and visualization of phylogenetic trees [2]_.

    It uses the New Hampshire Newick format as one of the most widely used
    standard representation of trees in bioinformatics [1]_.


    Parameters
    ----------
    G : NetworkX arborescence

    path_for_ete_output : file or string
       File or filename to write.

    Examples
    --------
    >>> G = nx.path_graph(42)
    >>> nx.write_ete(G, "test_ete.txt")

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    .. [3] https://networkx.org/documentation/stable//reference/algorithms/tree.html#tree
    """
    tree = to_ete(G)

    path_for_ete_output.write(
        tree.write(
            features=list(tree.features - {"dist", "support"}), format_root_node=True
        )
    )


@open_file(0, mode="r")
def read_ete(path):
    """Read a NetworkX arborescence [3]_ in the New Hampshire Newick format.

    ETE (Environment for Tree Exploration) is a Python programming toolkit
    that assists in the automated manipulation,
    analysis and visualization of phylogenetic trees [2]_.

    It uses the New Hampshire Newick format as one of the most widely used
    standard representation of trees in bioinformatics [1]_.

    Parameters
    ----------
    path : file or string
       File or filename to read.

    Returns
    -------
    G : NetworkX arborescence

    Examples
    --------
    >>> nx.write_ete(nx.path_graph(42), "test_ete.txt")
    >>> G = nx.read_ete("test_ete.txt")

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    .. [3] https://networkx.org/documentation/stable//reference/algorithms/tree.html#tree
    """
    try:
        import ete3
    except ImportError as e:
        raise ImportError("to_ete() requires ete3: http://etetoolkit.org/") from e

    file = [line for line in path]

    tree = ete3.Tree(file[0])

    return from_ete(tree)
