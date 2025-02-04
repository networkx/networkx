from itertools import chain, combinations, product
from typing import Optional, Union

import networkx as nx
from networkx.algorithms.simple_paths import all_bounded_simple_paths

STAR_INDEX_LEAVES = {
    "G_6": 3,
    "G_8": 4,
    "G_13": 5,
}


def treelets(
    G: nx.Graph,
    nodes: int | list[int] | None = None,
    patterns: list[str] | None = None,
) -> list:
    return _treelets(G, nodes, False, None, None, patterns)


def labeled_treelets(
    G: nx.Graph,
    nodes: int | list[int] | None = None,
    patterns: list[str] | None = None,
    node_labels: list[str] | None = None,
    edge_labels: list[str] | None = None,
) -> list:
    if node_labels is None:
        node_labels = list({key for _, attrs in G.nodes(data=True) for key in attrs})
    if edge_labels is None:
        edge_labels = list({key for _, _, attrs in G.edges(data=True) for key in attrs})
    return _treelets(G, nodes, True, node_labels, edge_labels, patterns)


def _treelets(G, nodes, labeled, node_labels, edge_labels, patterns):
    unlabeled = not labeled
    all_patterns = patterns is None
    canonkeys = {}

    if nodes is None:
        nodes_list = G.nodes
    elif isinstance(nodes, int):
        nodes_list = [nodes]
    else:
        nodes_list = nodes

    # G_{0, ..., 5} : path treelets
    if all_patterns or "path" in patterns:
        canonkeys.update(
            _linear_treelets(G, nodes_list, unlabeled, node_labels, edge_labels)
        )

    # G_{6, ..., 13} : star-based treelets
    if all_patterns or "star" in patterns or "star-path" in patterns:
        canonkeys.update(
            _star_based_treelets(
                G,
                nodes_list,
                unlabeled,
                node_labels,
                edge_labels,
                all_patterns or "star" in patterns,
                all_patterns or "star-path" in patterns,
            )
        )

    return canonkeys


def _linear_treelets(G, nodes, unlabeled, node_labels, edge_labels):
    # --- Manual implementation for better performance ---
    canonkeys = {}

    # G_0
    for node in nodes:
        path_0_key = (
            "G_0"
            if unlabeled
            else (
                "G_0",
                tuple(
                    G.nodes[node].get(node_label, None) for node_label in node_labels
                ),
            )
        )
        if path_0_key in canonkeys:
            canonkeys[path_0_key] += 1
        else:
            canonkeys[path_0_key] = 1

    # G_{1, ..., 5}
    LENGTH = 5
    for path in all_bounded_simple_paths(G, nodes, length=LENGTH):
        if unlabeled:
            path_canonkey = "G_" + str(len(path) - 1)
        else:
            path_keys = []
            for i in range(len(path)):
                path_keys.append(
                    tuple(
                        G.nodes[path[i]].get(node_label, None)
                        for node_label in node_labels
                    )
                )
                if i + 1 < len(path):
                    path_keys.append(
                        tuple(
                            G[path[i]][path[i + 1]].get(edge_label, None)
                            for edge_label in edge_labels
                        )
                    )
            path_canonkey = tuple(
                ["G_" + str(len(path) - 1)]
                + (path_keys if G.is_directed() else min(path_keys, path_keys[::-1]))
            )
        if path_canonkey in canonkeys:
            canonkeys[path_canonkey] += 1
        else:
            canonkeys[path_canonkey] = 1

    return canonkeys


def _star_based_treelets(
    G, nodes, unlabeled, node_labels, edge_labels, return_star, return_star_path
):
    # --- Manual implementation for better performance ---
    canonkeys = {}

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
                    star_canonkey = index
                else:
                    star_keys = []
                    for i in range(1, len(star_nodes)):
                        star_keys.append(
                            (
                                tuple(
                                    G[star_nodes[0]][star_nodes[i]].get(
                                        edge_label, None
                                    )
                                    for edge_label in edge_labels
                                ),
                                tuple(
                                    G.nodes[star_nodes[i]].get(node_label, None)
                                    for node_label in node_labels
                                ),
                            )
                        )
                    star_keys.sort()
                    star_canonkey = tuple(
                        [index]
                        + [
                            tuple(
                                G.nodes[star_nodes[0]].get(node_label, None)
                                for node_label in node_labels
                            )
                        ]
                        + list(chain.from_iterable(star_keys))
                    )
                if star_canonkey in canonkeys:
                    canonkeys[star_canonkey] += 1
                else:
                    canonkeys[star_canonkey] = 1

            # G_{7, 9, 10, 11, 12}
            if return_star_path:
                g_7_11 = {
                    3: "G_7",
                    4: "G_11",
                }
                if n_leaves in [3, 4]:
                    for leaf in star_nodes[1:]:
                        for node in G[leaf]:
                            if node not in star_nodes:
                                # G_{7, 11}
                                if unlabeled:
                                    g_7_11_canonkey = g_7_11[n_leaves]
                                else:
                                    g_7_11_keys = []
                                    for i in range(1, len(star_nodes)):
                                        if star_nodes[i] == leaf:
                                            g_7_11_keys.append(
                                                (
                                                    tuple(
                                                        G[star_nodes[0]][leaf].get(
                                                            edge_label, None
                                                        )
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[leaf].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                    tuple(
                                                        G[leaf][node].get(
                                                            edge_label, None
                                                        )
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[node].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                )
                                            )
                                        else:
                                            g_7_11_keys.append(
                                                (
                                                    tuple(
                                                        G[star_nodes[0]][
                                                            star_nodes[i]
                                                        ].get(edge_label, None)
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[star_nodes[i]].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                )
                                            )
                                    g_7_11_keys.sort()
                                    g_7_11_canonkey = tuple(
                                        [g_7_11[n_leaves]]
                                        + [
                                            tuple(
                                                G.nodes[star_nodes[0]].get(
                                                    node_label, None
                                                )
                                                for node_label in node_labels
                                            )
                                        ]
                                        + list(chain.from_iterable(g_7_11_keys))
                                    )
                                if g_7_11_canonkey in canonkeys:
                                    canonkeys[g_7_11_canonkey] += 1
                                else:
                                    canonkeys[g_7_11_canonkey] = 1

                                # G_10
                                if n_leaves == 3:
                                    for node_ext in G[node]:
                                        if node_ext not in star_nodes:
                                            if unlabeled:
                                                g_10_canonkey = "G_10"
                                            else:
                                                g_10_keys = [
                                                    (
                                                        tuple(
                                                            G[leaf][node].get(
                                                                edge_label, None
                                                            )
                                                            for edge_label in edge_labels
                                                        ),
                                                        tuple(
                                                            G.nodes[node].get(
                                                                node_label, None
                                                            )
                                                            for node_label in node_labels
                                                        ),
                                                        tuple(
                                                            G[node][node_ext].get(
                                                                edge_label, None
                                                            )
                                                            for edge_label in edge_labels
                                                        ),
                                                        tuple(
                                                            G.nodes[node_ext].get(
                                                                node_label, None
                                                            )
                                                            for node_label in node_labels
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
                                                                        edge_label, None
                                                                    )
                                                                    for edge_label in edge_labels
                                                                ),
                                                                tuple(
                                                                    G.nodes[
                                                                        star_nodes[i]
                                                                    ].get(
                                                                        node_label, None
                                                                    )
                                                                    for node_label in node_labels
                                                                ),
                                                            )
                                                        )
                                                star_keys.sort()
                                                g_10_keys.append(
                                                    (
                                                        tuple(
                                                            G[leaf][star_nodes[0]].get(
                                                                edge_label, None
                                                            )
                                                            for edge_label in edge_labels
                                                        ),
                                                        tuple(
                                                            G.nodes[star_nodes[0]].get(
                                                                node_label, None
                                                            )
                                                            for node_label in node_labels
                                                        ),
                                                        *chain.from_iterable(star_keys),
                                                    )
                                                )
                                                g_10_keys.sort()
                                                g_10_canonkey = tuple(
                                                    ["G_10"]
                                                    + [
                                                        tuple(
                                                            G.nodes[leaf].get(
                                                                node_label, None
                                                            )
                                                            for node_label in node_labels
                                                        )
                                                    ]
                                                    + list(
                                                        chain.from_iterable(g_10_keys)
                                                    )
                                                )
                                            if g_10_canonkey in canonkeys:
                                                canonkeys[g_10_canonkey] += 1
                                            else:
                                                canonkeys[g_10_canonkey] = 1

                        # G_12
                        if n_leaves == 3:
                            for star_leaves in combinations(G[leaf], 2):
                                if all(n not in star_nodes for n in star_leaves):
                                    if unlabeled:
                                        g_12_canonkey = "G_12"
                                    else:
                                        leaves = [
                                            n for n in star_nodes[1:] if n != leaf
                                        ]
                                        g_12_canonkeys = []
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
                                                        ].get(edge_label, None)
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[first_leaves[0]].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                ),
                                                (
                                                    tuple(
                                                        G[first_node][
                                                            first_leaves[1]
                                                        ].get(edge_label, None)
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[first_leaves[1]].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                ),
                                            ]
                                            other_star_keys = [
                                                (
                                                    tuple(
                                                        G[second_node][
                                                            second_leaves[0]
                                                        ].get(edge_label, None)
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[second_leaves[0]].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                ),
                                                (
                                                    tuple(
                                                        G[second_node][
                                                            second_leaves[1]
                                                        ].get(edge_label, None)
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[second_leaves[1]].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                ),
                                            ]
                                            other_star_keys.sort()
                                            g_12_keys.append(
                                                (
                                                    tuple(
                                                        G[first_node][second_node].get(
                                                            edge_label, None
                                                        )
                                                        for edge_label in edge_labels
                                                    ),
                                                    tuple(
                                                        G.nodes[second_node].get(
                                                            node_label, None
                                                        )
                                                        for node_label in node_labels
                                                    ),
                                                    *chain.from_iterable(
                                                        other_star_keys
                                                    ),
                                                )
                                            )
                                            g_12_keys.sort()
                                            g_12_canonkeys.append(
                                                tuple(
                                                    ["G_12"]
                                                    + [
                                                        tuple(
                                                            G.nodes[first_node].get(
                                                                node_label, None
                                                            )
                                                            for node_label in node_labels
                                                        )
                                                    ]
                                                    + list(
                                                        chain.from_iterable(g_12_keys)
                                                    )
                                                )
                                            )
                                        g_12_canonkey = min(g_12_canonkeys)
                                    if g_12_canonkey in canonkeys:
                                        canonkeys[g_12_canonkey] += 1
                                    else:
                                        canonkeys[g_12_canonkey] = 1

                # G_9
                if n_leaves == 3:
                    for star_leaves in combinations(star_nodes[1:], 2):
                        missing_leaf = next(
                            n for n in star_nodes[1:] if n not in star_leaves
                        )
                        for leaves in product(G[star_leaves[0]], G[star_leaves[1]]):
                            if all(leaf not in star_nodes for leaf in leaves):
                                if unlabeled:
                                    g_9_canonkey = "G_9"
                                else:
                                    g_9_keys = [
                                        (
                                            tuple(
                                                G[star_nodes[0]][missing_leaf].get(
                                                    edge_label, None
                                                )
                                                for edge_label in edge_labels
                                            ),
                                            tuple(
                                                G.nodes[missing_leaf].get(
                                                    node_label, None
                                                )
                                                for node_label in node_labels
                                            ),
                                        ),
                                        (
                                            tuple(
                                                G[star_nodes[0]][star_leaves[0]].get(
                                                    edge_label, None
                                                )
                                                for edge_label in edge_labels
                                            ),
                                            tuple(
                                                G.nodes[star_leaves[0]].get(
                                                    node_label, None
                                                )
                                                for node_label in node_labels
                                            ),
                                            tuple(
                                                G[star_leaves[0]][leaves[0]].get(
                                                    edge_label, None
                                                )
                                                for edge_label in edge_labels
                                            ),
                                            tuple(
                                                G.nodes[leaves[0]].get(node_label, None)
                                                for node_label in node_labels
                                            ),
                                        ),
                                        (
                                            tuple(
                                                G[star_nodes[0]][star_leaves[1]].get(
                                                    edge_label, None
                                                )
                                                for edge_label in edge_labels
                                            ),
                                            tuple(
                                                G.nodes[star_leaves[1]].get(
                                                    node_label, None
                                                )
                                                for node_label in node_labels
                                            ),
                                            tuple(
                                                G[star_leaves[1]][leaves[1]].get(
                                                    edge_label, None
                                                )
                                                for edge_label in edge_labels
                                            ),
                                            tuple(
                                                G.nodes[leaves[1]].get(node_label, None)
                                                for node_label in node_labels
                                            ),
                                        ),
                                    ]
                                    g_9_keys.sort()
                                    g_9_canonkey = tuple(
                                        ["G_9"]
                                        + [
                                            tuple(
                                                G.nodes[star_nodes[0]].get(
                                                    node_label, None
                                                )
                                                for node_label in node_labels
                                            )
                                        ]
                                        + list(chain.from_iterable(g_9_keys))
                                    )
                                if g_9_canonkey in canonkeys:
                                    canonkeys[g_9_canonkey] += 1
                                else:
                                    canonkeys[g_9_canonkey] = 1

    # G_12 are counted twice
    if return_star_path:
        for key in canonkeys:
            if (unlabeled and key == "G_12") or (not unlabeled and key[0] == "G_12"):
                canonkeys[key] //= 2

    return canonkeys
