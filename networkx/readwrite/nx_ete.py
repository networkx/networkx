"""
****
ETE
****
Read and write NetworkX :mod:`arborescence<tree>` in the New Hampshire Newick format.

ETE (Environment for Tree Exploration) is a Python programming toolkit
that assists in the automated manipulation,
analysis and visualization of phylogenetic trees.

It uses the New Hampshire Newick format as one of the most widely used
standard representation of trees in bioinformatics.

See http://etetoolkit.org/ for documentation.

Format
------
http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees

"""

__all__ = ["generate_ete", "parse_ete"]

from collections import deque

import networkx as nx


def generate_ete(G):
    """Returns a ETE Tree from NetworkX :mod:`arborescence<tree>` G.

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
    >>> G = nx.path_graph(42, create_using=nx.DiGraph)
    >>> T = nx.generate_ete(G)

    Notes
    -----
    - ETE Tree containing only node features.
      Thus, the data of the edges of the NetworkX :mod:`arborescence<tree>` will be lost.
    - In ETE Tree every node contains three basic attributes: name(``TreeNode.name``),
      branch length(``TreeNode.dist``) and branch support(``TreeNode.support``)
      which can have different meanings in the NetworkX :mod:`arborescence<tree>`.

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    """
    if not nx.is_arborescence(G):
        raise ValueError(f"Input graph G must be an arborescence.")

    try:
        import ete3
    except ImportError as e:
        raise ImportError("generate_ete() requires ete3: http://etetoolkit.org/") from e

    tree_nodes = dict()

    for node_name, node_features in G.nodes(data=True):
        tree_node = ete3.Tree(name=node_name)
        tree_node.add_features(**node_features)

        tree_nodes[node_name] = tree_node

    root_node = [n for n, d in G.in_degree() if d == 0][0]

    queue = deque([root_node])

    while queue:
        parent = queue.popleft()

        for child in G[parent]:
            queue.append(child)
            tree_nodes[parent].add_child(child=tree_nodes[child])

    return tree_nodes[root_node]


def parse_ete(T):
    """Returns a NetworkX :mod:`arborescence<tree>` from ETE Tree.

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
    >>> T = nx.generate_ete(nx.path_graph(42, create_using=nx.DiGraph))
    >>> G = nx.parse_ete(T)

    Notes
    -----
    - In ETE Tree every node contains three basic attributes: name(``TreeNode.name``),
      branch length(``TreeNode.dist``) and branch support(``TreeNode.support``)
      which can have different meanings in the NetworkX :mod:`arborescence<tree>`.

    References
    ----------
    .. [1] http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    .. [2] http://etetoolkit.org/
    """
    try:
        import ete3
    except ImportError as e:
        raise ImportError("parse_ete() requires ete3: http://etetoolkit.org/") from e

    G = nx.DiGraph()

    for tree_node in T.iter_search_nodes():
        node_name = tree_node.name
        node_features = {
            k: getattr(tree_node, k) for k in tree_node.features - {"name"}
        }

        G.add_node(node_name, **node_features)

    queue = deque([T])

    while queue:
        parent = queue.popleft()

        for child in parent.children:
            queue.append(child)
            G.add_edge(parent.name, child.name)

    return G
