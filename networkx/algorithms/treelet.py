"""
A treelet is a small, connected, acyclic subgraph (tree-like structure)
of a graph, typically limited to 6 nodes. Treelets capture local structural
patterns and are useful in applications such as graph kernels and pattern
recognition.

The following functions are meant to extract and analyze treelets, either
considering only topology (unlabeled) or incorporating node and edge labels
(labeled). The extraction follows the methodology described in `this paper
<https://hal.science/hal-00773283/document>`_.
"""

from itertools import chain, combinations, product

import networkx as nx

STAR_INDEX_LEAVES = {
    "G_6": 3,
    "G_8": 4,
    "G_13": 5,
}

EXT_1_STAR = {
    3: "G_7",
    4: "G_11",
}


def treelets(G, nodes=None, patterns=None):
    """
    Compute treelets of a graph.

    A treelet is a small, connected, acyclic subgraph (tree-like structure)
    of a graph, typically limited to 6 nodes. Treelets capture local structural
    patterns and are useful in applications such as graph kernels and pattern
    recognition.

    This function extracts treelets from a NetworkX graph. It returns the
    treelet indices (see *Notes*) and their occurrences. The extraction follows
    the approach from [1]_,  identifying different treelet patterns like "path"
    and "star" within the graph, and counting how often they appear.

    Parameters
    ----------
    G : NetworkX Graph
        Input graph from which to extract treelets.
    nodes : int, list[int], or None, optional
        A single node or a list of nodes for which treelets are extracted.
        If None, treelets are computed for all nodes in G.
    patterns : str, list[str] or None, optional
        A string or a list of strings specifying the treelet patterns to extract.
        Available patterns include `"path"`, `"star"`, and `"star-path"`. Each
        pattern corresponds to a specific set of treelet indices (see *Notes*).
        If None, all available patterns are used, including both linear and
        star-based motifs.

    Returns
    -------
    dict
        A dictionary where the keys are treelet indices (following the
        convention in [1]_) and the values are their respective counts in
        the graph G.

    Notes
    -----
    - For detailed information on the treelet indices and their corresponding
      patterns, refer to [1]_ or the *Treelets* example in the Gallery. The
      patterns are composed as follows:
        - `"path"` corresponds to indices :math:`G_0` to :math:`G_5`.
        - `"star"` corresponds to indices :math:`G_6`, :math:`G_8` and
          :math:`G_{13}`.
        - `"star-path"` corresponds to indices :math:`G_7`, :math:`G_9`,
          :math:`G_{10}`, :math:`G_{11}` and :math:`G_{12}`.
    - This function does not consider node or edge labels. For labeled
      treelets, use `labeled_treelets`.
    - Extracting all treelets from a large graph can be computationally
      expensive, with a complexity of :math:`O(nd^5)`, where :math:`n` is the
      number of nodes and :math:`d` is the maximum degree of the graph.

    Examples
    --------
    Treelet extraction from an undirected 5-path graph:

        >>> G = nx.path_graph(5)
        >>> nx.treelets(G)
        {'G_0': 5, 'G_1': 4, 'G_2': 3, 'G_3': 2, 'G_4': 1}

    Treelet extraction from an directed 5-path graph:

        >>> G = nx.path_graph(5).to_directed()
        >>> nx.treelets(G)
        {'G_0': 5, 'G_1': 8, 'G_2': 6, 'G_3': 4, 'G_4': 2}

    Treelet extraction centered on node 1 from an directed 5-path graph:

        >>> G = nx.path_graph(5)
        >>> nx.treelets(G, 1)
        {'G_0': 1, 'G_1': 2, 'G_2': 1, 'G_3': 1}

    Treelet extraction centered on nodes 1 and 3 from an directed 5-path graph:

        >>> G = nx.path_graph(5)
        >>> nx.treelets(G, [1, 3])
        {'G_0': 2, 'G_1': 4, 'G_2': 1, 'G_3': 2}

    Treelet extraction from a 5-star graph:

        >>> G = nx.star_graph(5)
        >>> nx.treelets(G)
        {'G_0': 6, 'G_1': 5, 'G_2': 10, 'G_6': 10, 'G_8': 5, 'G_13': 1}

    Treelet extraction from a two connected 3-stars graph:

        >>> G = nx.star_graph(3)
        >>> G.add_edges_from([(3, 4), (3, 5)])
        >>> nx.treelets(G)
        {'G_0': 6, 'G_1': 5, 'G_2': 6, 'G_3': 4, 'G_6': 2, 'G_7': 4, 'G_12': 1}

    Treelet extraction from a two connected 3-stars graph with pattern filters:

        >>> G = nx.star_graph(3)
        >>> G.add_edges_from([(3, 4), (3, 5)])
        >>> nx.treelets(G, patterns="star-path")
        {'G_7': 4, 'G_12': 1}
        >>> nx.treelets(G, patterns=["path", "star"])
        {'G_0': 6, 'G_1': 5, 'G_2': 6, 'G_3': 4, 'G_6': 2}

    See also
    --------
    labeled_treelets

    References
    ----------
    .. [1] B. Gaüzère, L. Brun, D. Villemin, "Two New Graphs Kernels in
        Chemoinformatics", Pattern Recognition Letters, 2012, 33 (15),
        2038-2047.
    """
    return _treelets(G, nodes, False, None, None, patterns)


def labeled_treelets(G, nodes=None, patterns=None, node_attrs=None, edge_attrs=None):
    """
    Compute labeled treelets of a graph.

    A labeled treelet is a small, connected, acyclic subgraph (tree-like structure)
    of a graph, typically limited to 6 nodes, where node and edge attributes are also
    considered. Treelets capture local structural patterns and are useful in
    applications such as graph kernels and pattern recognition.

    This function extracts labeled treelets from a NetworkX graph. It returns the
    treelet codes (see *Notes*) and their occurrences. The extraction follows
    the approach described in [1]_, identifying different treelet patterns like
    "path" and "star" within the graph, and counting how often they appear, while
    taking into account node and edge attributes.

    Parameters
    ----------
    G : NetworkX Graph
        Input graph from which to extract labeled treelets.
    nodes : int, list[int], or None, optional
        A single node or a list of nodes for which treelets are extracted.
        If None, treelets are computed for all nodes in G.
    patterns : str, list[str] or None, optional
        A string or a list of strings specifying the treelet patterns to extract.
        Available patterns include `"path"`, `"star"`, and `"star-path"`. Each
        pattern corresponds to a specific set of treelet indices (see *Notes*).
        If None, all available patterns are used, including both linear and
        star-based motifs.
    node_attrs : list[str], optional
        A list of node attribute names to consider for labeling the nodes, selected from
        the available attributes in the graph. If None, node attributes are inferred
        from the graph.
    edge_attrs : list[str], optional
        A list of edge attribute names to consider for labeling the edges, selected
        from the available attributes in the graph. If None, edge attributes are inferred
        from the graph.

    Returns
    -------
    dict
        A dictionary where the keys are treelet codes and the values are their
        respective counts in the graph G. Each key is a tuple where the first
        element corresponds to the treelet index, and the subsequent elements
        correspond to the canonical key of the labeled treelet (see *Notes*).

    Notes
    -----
    - For detailed information on the treelet indices and their corresponding
      patterns, refer to [1]_ or the *Treelets* example in the Gallery. The
      patterns are composed as follows:
        - `"path"` corresponds to indices :math:`G_0` to :math:`G_5`.
        - `"star"` corresponds to indices :math:`G_6`, :math:`G_8` and :math:`G_{13}`.
        - `"star-path"` corresponds to indices :math:`G_7`, :math:`G_9`,
          :math:`G_{10}`, :math:`G_{11}` and :math:`G_{12}`.
    - The treelet codes consist of the treelet index as the first element,
      followed by the canonical key of the labeled treelet, which is a sequence
      of node and edge attributes. Each node and edge can have multiple attributes,
      and the canonical key uniquely encodes the combination of these attributes.
      Two treelets with identical structure and identical attributes will have the
      same canonical key. See [1]_ for details on the algorithms used to generate
      the canonical keys.
    - Extracting all labeled treelets from a large graph can be computationally
      expensive, with a complexity of :math:`O(nd^5)`, where :math:`n` is the
      number of nodes and :math:`d` is the maximum degree of the graph.

    Examples
    --------
    Labeled treelet extraction from a simple molecule :math:`(CH_2O)`:

        >>> G = nx.Graph()
        >>> atoms = ["C", "H", "H", "O"]
        >>> for i, atom in enumerate(atoms):
        ...     G.add_node(i, atom_symbol=atom)
        >>> bond_types = ["1", "1", "2"]
        >>> edges = [(0, 1), (0, 2), (0, 3)]
        >>> for (u, v), bond in zip(edges, bond_types):
        ...     G.add_edge(u, v, bond_type=bond)
        >>> nx.labeled_treelets(G)
        {('G_0', ('C',)): 1,
         ('G_0', ('H',)): 2,
         ('G_0', ('O',)): 1,
         ('G_1', ('C',), ('1',), ('H',)): 2,
         ('G_1', ('C',), ('2',), ('O',)): 1,
         ('G_2', ('H',), ('1',), ('C',), ('1',), ('H',)): 1,
         ('G_2', ('H',), ('1',), ('C',), ('2',), ('O',)): 2,
         ('G_6', ('C',), ('1',), ('H',), ('1',), ('H',), ('2',), ('O',)): 1}

    Labeled treelet extraction from a directed version of a simple molecule
    :math:`(CH_2O)`:

        >>> G = nx.DiGraph()
        >>> atoms = ["C", "H", "H", "O"]
        >>> for i, atom in enumerate(atoms):
        ...     G.add_node(i, atom_symbol=atom)
        >>> bond_types = ["1", "1", "2"]
        >>> edges = [(0, 1), (0, 2), (0, 3)]
        >>> for (u, v), bond in zip(edges, bond_types):
        ...     G.add_edge(u, v, bond_type=bond)
        >>> nx.labeled_treelets(G, node_attrs=["atom_symbol"], edge_attrs=["bond_type"])
        {('G_0', ('C',)): 1,
         ('G_0', ('H',)): 2,
         ('G_0', ('O',)): 1,
         ('G_1', ('C',), ('1',), ('H',)): 2,
         ('G_1', ('C',), ('2',), ('O',)): 1,
         ('G_6', ('C',), ('1',), ('H',), ('1',), ('H',), ('2',), ('O',)): 1}

    Labeled treelet extraction centered on node 0 (Carbon) from a simple molecule
    :math:`(CH_2O)`:

        >>> G = nx.Graph()
        >>> atoms = ["C", "H", "H", "O"]
        >>> for i, atom in enumerate(atoms):
        ...     G.add_node(i, atom_symbol=atom)
        >>> bond_types = ["1", "1", "2"]
        >>> edges = [(0, 1), (0, 2), (0, 3)]
        >>> for (u, v), bond in zip(edges, bond_types):
        ...     G.add_edge(u, v, bond_type=bond)
        >>> nx.labeled_treelets(G, 0)
        {('G_0', ('C',)): 1,
         ('G_1', ('C',), ('1',), ('H',)): 2,
         ('G_1', ('C',), ('2',), ('O',)): 1,
         ('G_6', ('C',), ('1',), ('H',), ('1',), ('H',), ('2',), ('O',)): 1}

    Labeled treelet extraction with pattern filters from a simple molecule
    :math:`(CH_2O)`:

        >>> G = nx.Graph()
        >>> atoms = ["C", "H", "H", "O"]
        >>> for i, atom in enumerate(atoms):
        ...     G.add_node(i, atom_symbol=atom)
        >>> bond_types = ["1", "1", "2"]
        >>> edges = [(0, 1), (0, 2), (0, 3)]
        >>> for (u, v), bond in zip(edges, bond_types):
        ...     G.add_edge(u, v, bond_type=bond)
        >>> nx.labeled_treelets(G, patterns="star")
        {('G_6', ('C',), ('1',), ('H',), ('1',), ('H',), ('2',), ('O',)): 1}
        >>> nx.labeled_treelets(G, patterns=["path"])
        {('G_0', ('C',)): 1,
         ('G_0', ('H',)): 2,
         ('G_0', ('O',)): 1,
         ('G_1', ('C',), ('1',), ('H',)): 2,
         ('G_1', ('C',), ('2',), ('O',)): 1,
         ('G_2', ('H',), ('1',), ('C',), ('1',), ('H',)): 1,
         ('G_2', ('H',), ('1',), ('C',), ('2',), ('O',)): 2}

    See also
    --------
    treelets

    References
    ----------
    .. [1] B. Gaüzère, L. Brun, D. Villemin, "Two New Graphs Kernels in
        Chemoinformatics", Pattern Recognition Letters, 2012, 33 (15),
        2038-2047.
    """
    if node_attrs is None:
        node_attrs = list({key for _, attrs in G.nodes(data=True) for key in attrs})
    if edge_attrs is None:
        edge_attrs = list({key for _, _, attrs in G.edges(data=True) for key in attrs})
    return _treelets(G, nodes, True, node_attrs, edge_attrs, patterns)


def _treelets(G, nodes, labeled, node_attrs, edge_attrs, patts):
    """Extracts treelets from the graph based on predefined patterns.

    If `labeled` is True, node and edge attributes are considered to generate
    canonical representations. Supports path, star, and star-path
    treelets. The function processes a subset of nodes if `nodes` is specified.
    """
    unlabeled = not labeled
    patterns = [patts] if isinstance(patts, str) else patts
    all_patterns = False
    if patterns is None:
        all_patterns = True
    else:
        if any(patt not in ["path", "star", "star-path"] for patt in patterns):
            raise ValueError(
                "Invalid treelet pattern(s). Use 'path', 'star', or 'star-path'."
            )
    codes = {}

    if nodes is None:
        nodes_list = G.nodes
    elif isinstance(nodes, int):
        nodes_list = [nodes]
    else:
        nodes_list = nodes

    # G_{0, ..., 5} : path treelets
    if all_patterns or "path" in patterns:
        codes.update(_linear_treelets(G, nodes_list, unlabeled, node_attrs, edge_attrs))

    # G_{6, ..., 13} : star-based treelets
    if all_patterns or "star" in patterns or "star-path" in patterns:
        codes.update(
            _star_based_treelets(
                G,
                nodes_list,
                unlabeled,
                node_attrs,
                edge_attrs,
                all_patterns or "star" in patterns,
                all_patterns or "star-path" in patterns,
            )
        )

    return codes


def _linear_treelets(G, nodes, unlabeled, node_attrs, edge_attrs):
    """Extracts path-based treelets (G_0 to G_5) from the graph.

    These treelets represent linear substructures up to 6 nodes. If `unlabeled`
    is False, node and edge attributes are used to generate labeled treelets.
    If `nodes` is specified, only treelets centered on those nodes are extracted.
    """
    # --- Manual implementation for better performance ---
    codes = {}

    # G_0
    for node in nodes:
        path_0_key = (
            "G_0"
            if unlabeled
            else (
                "G_0",
                tuple(G.nodes[node].get(node_attr, None) for node_attr in node_attrs),
            )
        )
        if path_0_key in codes:
            codes[path_0_key] += 1
        else:
            codes[path_0_key] = 1

    # G_{1, ..., 5}
    LENGTH = 5
    for path in nx.all_bounded_simple_paths(G, nodes, length=LENGTH):
        if unlabeled:
            path_code = "G_" + str(len(path) - 1)
        else:
            path_keys = []
            for i in range(len(path)):
                path_keys.append(
                    tuple(
                        G.nodes[path[i]].get(node_attr, None)
                        for node_attr in node_attrs
                    )
                )
                if i + 1 < len(path):
                    path_keys.append(
                        tuple(
                            G[path[i]][path[i + 1]].get(edge_attr, None)
                            for edge_attr in edge_attrs
                        )
                    )
            path_code = tuple(
                ["G_" + str(len(path) - 1)]
                + (path_keys if G.is_directed() else min(path_keys, path_keys[::-1]))
            )
        if path_code in codes:
            codes[path_code] += 1
        else:
            codes[path_code] = 1

    return codes


def _star_based_treelets(
    G, nodes, unlabeled, node_attrs, edge_attrs, return_star, return_star_path
):
    """Extracts star-based treelets (G_6 to G_13) from the graph.

    Supports both pure star patterns and star-path extensions. If `unlabeled`
    is False, the function incorporates node and edge attributes into the
    canonical representation. The `return_star` and `return_star_path` parameters
    control whether only star-shaped treelets or both star and star-path treelets
    are extracted.
    """
    # --- Manual implementation for better performance ---
    codes = {}

    # G_{6, ..., 13}
    for index in STAR_INDEX_LEAVES:
        n_leaves = STAR_INDEX_LEAVES[index]
        star_treelets = [
            [node] + list(comb)
            for node in nodes
            for comb in combinations(G[node], n_leaves)
            if len(G[node]) >= n_leaves
        ]
        for star_nodes in star_treelets:
            # G_{6, 8, 13}
            if return_star:
                if unlabeled:
                    star_code = index
                else:
                    star_keys = []
                    for i in range(1, len(star_nodes)):
                        star_keys.append(
                            (
                                tuple(
                                    G[star_nodes[0]][star_nodes[i]].get(edge_attr, None)
                                    for edge_attr in edge_attrs
                                ),
                                tuple(
                                    G.nodes[star_nodes[i]].get(node_attr, None)
                                    for node_attr in node_attrs
                                ),
                            )
                        )
                    star_keys.sort()
                    star_code = tuple(
                        [index]
                        + [
                            tuple(
                                G.nodes[star_nodes[0]].get(node_attr, None)
                                for node_attr in node_attrs
                            )
                        ]
                        + list(chain.from_iterable(star_keys))
                    )
                if star_code in codes:
                    codes[star_code] += 1
                else:
                    codes[star_code] = 1

            # G_{7, 9, 10, 11, 12}
            if return_star_path:
                if n_leaves in [3, 4]:
                    for leaf in star_nodes[1:]:
                        for node in G[leaf]:
                            if node not in star_nodes:
                                # G_{7, 11}
                                if unlabeled:
                                    g_7_11_code = EXT_1_STAR[n_leaves]
                                else:
                                    g_7_11_keys = []
                                    for i in range(1, len(star_nodes)):
                                        if star_nodes[i] == leaf:
                                            g_7_11_keys.append(
                                                (
                                                    tuple(
                                                        G[star_nodes[0]][leaf].get(
                                                            edge_attr, None
                                                        )
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[leaf].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                    tuple(
                                                        G[leaf][node].get(
                                                            edge_attr, None
                                                        )
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[node].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                )
                                            )
                                        else:
                                            g_7_11_keys.append(
                                                (
                                                    tuple(
                                                        G[star_nodes[0]][
                                                            star_nodes[i]
                                                        ].get(edge_attr, None)
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[star_nodes[i]].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                )
                                            )
                                    g_7_11_keys.sort()
                                    g_7_11_code = tuple(
                                        [EXT_1_STAR[n_leaves]]
                                        + [
                                            tuple(
                                                G.nodes[star_nodes[0]].get(
                                                    node_attr, None
                                                )
                                                for node_attr in node_attrs
                                            )
                                        ]
                                        + list(chain.from_iterable(g_7_11_keys))
                                    )
                                if g_7_11_code in codes:
                                    codes[g_7_11_code] += 1
                                else:
                                    codes[g_7_11_code] = 1

                                # G_10
                                if n_leaves == 3:
                                    for node_ext in G[node]:
                                        if node_ext not in star_nodes:
                                            if unlabeled:
                                                g_10_code = "G_10"
                                            else:
                                                g_10_keys = [
                                                    (
                                                        tuple(
                                                            G[leaf][node].get(
                                                                edge_attr, None
                                                            )
                                                            for edge_attr in edge_attrs
                                                        ),
                                                        tuple(
                                                            G.nodes[node].get(
                                                                node_attr, None
                                                            )
                                                            for node_attr in node_attrs
                                                        ),
                                                        tuple(
                                                            G[node][node_ext].get(
                                                                edge_attr, None
                                                            )
                                                            for edge_attr in edge_attrs
                                                        ),
                                                        tuple(
                                                            G.nodes[node_ext].get(
                                                                node_attr, None
                                                            )
                                                            for node_attr in node_attrs
                                                        ),
                                                    )
                                                ]
                                                star_keys = []
                                                for i in range(1, len(star_nodes)):
                                                    if star_nodes[i] != leaf:
                                                        star_keys.append(
                                                            (
                                                                tuple(
                                                                    G[star_nodes[0]][
                                                                        star_nodes[i]
                                                                    ].get(
                                                                        edge_attr, None
                                                                    )
                                                                    for edge_attr in edge_attrs
                                                                ),
                                                                tuple(
                                                                    G.nodes[
                                                                        star_nodes[i]
                                                                    ].get(
                                                                        node_attr, None
                                                                    )
                                                                    for node_attr in node_attrs
                                                                ),
                                                            )
                                                        )
                                                star_keys.sort()
                                                g_10_keys.append(
                                                    (
                                                        tuple(
                                                            G[leaf][star_nodes[0]].get(
                                                                edge_attr, None
                                                            )
                                                            for edge_attr in edge_attrs
                                                        ),
                                                        tuple(
                                                            G.nodes[star_nodes[0]].get(
                                                                node_attr, None
                                                            )
                                                            for node_attr in node_attrs
                                                        ),
                                                        *chain.from_iterable(star_keys),
                                                    )
                                                )
                                                g_10_keys.sort()
                                                g_10_code = tuple(
                                                    ["G_10"]
                                                    + [
                                                        tuple(
                                                            G.nodes[leaf].get(
                                                                node_attr, None
                                                            )
                                                            for node_attr in node_attrs
                                                        )
                                                    ]
                                                    + list(
                                                        chain.from_iterable(g_10_keys)
                                                    )
                                                )
                                            if g_10_code in codes:
                                                codes[g_10_code] += 1
                                            else:
                                                codes[g_10_code] = 1

                        # G_12
                        if n_leaves == 3:
                            for star_leaves in combinations(G[leaf], 2):
                                if all(n not in star_nodes for n in star_leaves):
                                    if unlabeled:
                                        g_12_code = "G_12"
                                    else:
                                        leaves = [
                                            n for n in star_nodes[1:] if n != leaf
                                        ]
                                        g_12_codes = []
                                        for (
                                            first_node,
                                            first_leaves,
                                            second_node,
                                            second_leaves,
                                        ) in (
                                            (star_nodes[0], leaves, leaf, star_leaves),
                                            (leaf, star_leaves, star_nodes[0], leaves),
                                        ):
                                            g_12_keys = [
                                                (
                                                    tuple(
                                                        G[first_node][
                                                            first_leaves[0]
                                                        ].get(edge_attr, None)
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[first_leaves[0]].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                ),
                                                (
                                                    tuple(
                                                        G[first_node][
                                                            first_leaves[1]
                                                        ].get(edge_attr, None)
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[first_leaves[1]].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                ),
                                            ]
                                            other_star_keys = [
                                                (
                                                    tuple(
                                                        G[second_node][
                                                            second_leaves[0]
                                                        ].get(edge_attr, None)
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[second_leaves[0]].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                ),
                                                (
                                                    tuple(
                                                        G[second_node][
                                                            second_leaves[1]
                                                        ].get(edge_attr, None)
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[second_leaves[1]].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                ),
                                            ]
                                            other_star_keys.sort()
                                            g_12_keys.append(
                                                (
                                                    tuple(
                                                        G[first_node][second_node].get(
                                                            edge_attr, None
                                                        )
                                                        for edge_attr in edge_attrs
                                                    ),
                                                    tuple(
                                                        G.nodes[second_node].get(
                                                            node_attr, None
                                                        )
                                                        for node_attr in node_attrs
                                                    ),
                                                    *chain.from_iterable(
                                                        other_star_keys
                                                    ),
                                                )
                                            )
                                            g_12_keys.sort()
                                            g_12_codes.append(
                                                tuple(
                                                    ["G_12"]
                                                    + [
                                                        tuple(
                                                            G.nodes[first_node].get(
                                                                node_attr, None
                                                            )
                                                            for node_attr in node_attrs
                                                        )
                                                    ]
                                                    + list(
                                                        chain.from_iterable(g_12_keys)
                                                    )
                                                )
                                            )
                                        g_12_code = min(g_12_codes)
                                    if g_12_code in codes:
                                        codes[g_12_code] += 1
                                    else:
                                        codes[g_12_code] = 1

                # G_9
                if n_leaves == 3:
                    for star_leaves in combinations(star_nodes[1:], 2):
                        missing_leaf = next(
                            n for n in star_nodes[1:] if n not in star_leaves
                        )
                        for leaves in product(G[star_leaves[0]], G[star_leaves[1]]):
                            if all(leaf not in star_nodes for leaf in leaves):
                                if unlabeled:
                                    g_9_code = "G_9"
                                else:
                                    g_9_keys = [
                                        (
                                            tuple(
                                                G[star_nodes[0]][missing_leaf].get(
                                                    edge_attr, None
                                                )
                                                for edge_attr in edge_attrs
                                            ),
                                            tuple(
                                                G.nodes[missing_leaf].get(
                                                    node_attr, None
                                                )
                                                for node_attr in node_attrs
                                            ),
                                        ),
                                        (
                                            tuple(
                                                G[star_nodes[0]][star_leaves[0]].get(
                                                    edge_attr, None
                                                )
                                                for edge_attr in edge_attrs
                                            ),
                                            tuple(
                                                G.nodes[star_leaves[0]].get(
                                                    node_attr, None
                                                )
                                                for node_attr in node_attrs
                                            ),
                                            tuple(
                                                G[star_leaves[0]][leaves[0]].get(
                                                    edge_attr, None
                                                )
                                                for edge_attr in edge_attrs
                                            ),
                                            tuple(
                                                G.nodes[leaves[0]].get(node_attr, None)
                                                for node_attr in node_attrs
                                            ),
                                        ),
                                        (
                                            tuple(
                                                G[star_nodes[0]][star_leaves[1]].get(
                                                    edge_attr, None
                                                )
                                                for edge_attr in edge_attrs
                                            ),
                                            tuple(
                                                G.nodes[star_leaves[1]].get(
                                                    node_attr, None
                                                )
                                                for node_attr in node_attrs
                                            ),
                                            tuple(
                                                G[star_leaves[1]][leaves[1]].get(
                                                    edge_attr, None
                                                )
                                                for edge_attr in edge_attrs
                                            ),
                                            tuple(
                                                G.nodes[leaves[1]].get(node_attr, None)
                                                for node_attr in node_attrs
                                            ),
                                        ),
                                    ]
                                    g_9_keys.sort()
                                    g_9_code = tuple(
                                        ["G_9"]
                                        + [
                                            tuple(
                                                G.nodes[star_nodes[0]].get(
                                                    node_attr, None
                                                )
                                                for node_attr in node_attrs
                                            )
                                        ]
                                        + list(chain.from_iterable(g_9_keys))
                                    )
                                if g_9_code in codes:
                                    codes[g_9_code] += 1
                                else:
                                    codes[g_9_code] = 1

    # G_12 are counted twice
    if return_star_path:
        for key in codes:
            if (unlabeled and key == "G_12") or (not unlabeled and key[0] == "G_12"):
                codes[key] //= 2

    return codes
