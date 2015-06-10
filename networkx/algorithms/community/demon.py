# -*- coding: utf-8 -*-
#    Copyright (C) 2015
#    All rights reserved.
#    BSD license.

"""
Flat Merge version of DEMON (Democratic Estimate of the Modular Organization of
a Network) algorithm. DEMON uses a local-first approach to community discovery 
were each node democratically votes for the communities that it sees in its
surroundings. It provides a deterministic, fully incremental method for 
community discovery that has a limited time complexity.
"""

from __future__ import division
import networkx as nx
import random

__all__ = ["demon_communities"]


def demon_communities(G, epsilon=0.25, min_community_size=3, weight=None):
    """Finds the communities in a graph using the label Democratic Estimate of
    the Modular Organization of a Network (DEMON) algorithm[1]_. This method
    uses a local-first approach to community discovery were each node
    democratically votes for the communities that it sees in its surroundings.
    Communities in this algorithm can be overlapping.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    epsilon: real
        The tolerance required in order to merge communities. The epsilon
        factor is introduced to vary the percentage of common elements provided
        from each couple of communities: epsilon = 0 ensure that two
        communities are merged only if one of them is a proper subset of the
        other, on the other hand with a value of epsilon = 1 even communities
        that do not share a single node are merged together

    min_community_size: integer
        Min nodes needed to form a community

    weight: String
        If the graph is weighted, the edge parameter representing the weight

    Returns
    -------
    communities : list
        List of overlapping communities (sets)

    References
    ----------
    .. [1] Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
           DEMON: a local-first discovery method for overlapping communities.
           KDD 2012:615-623.
    """

    for n in G:
            G.node[n]['communities'] = [n]

    all_communities = []

    for ego in G:
        # EgoMinusEgo and LabelPropagation phase
        ego_minus_ego = nx.ego_graph(G, ego, 1, False)
        community_to_nodes = _overlapping_label_propagation(ego_minus_ego, ego, weight)

        # merging phase
        for c in community_to_nodes.keys():
            if len(community_to_nodes[c]) > min_community_size:
                actual_community = community_to_nodes[c]
                all_communities = _merge_communities(all_communities, set(actual_community), epsilon)

    for c in all_communities:
        yield c


def _overlapping_label_propagation(ego_minus_ego, ego, weight, max_iter=100):
    """
    Label propagation algorithm based on [2]_ used to find communities in the
    EgoMinusEgo Graph.

    Parameters
    ----------
    ego_minus_ego : graph
        ego network minus its center

    ego : string
        ego network cente

    weight : string
        If the graph is weighted, the edge parameter representing the weight

    max_iter : integer
        number of desired iteration for the label propagation

    Returns
    -------
    community_to_nodes : dict
        List of communities in the EgoMinusEgo graph

    References
    ----------
    .. [2] Raghavan, Usha Nandini, Réka Albert, and Soundar Kumara. "Near
           linear time algorithm to detect community structures in large-scale
           networks." Physical Review E 76.3 (2007): 036106.

    """
    old_node_to_coms = {}

    for t in range(max_iter):
        node_to_coms = {}
        nodes = list(ego_minus_ego)
        random.shuffle(nodes)

        for n in nodes:
            label_freq = {}
            n_neighbors = nx.neighbors(ego_minus_ego, n)
            if len(n_neighbors) < 1:
                continue
            for nn in n_neighbors:
                communities_nn = [nn]
                if nn in old_node_to_coms:
                    communities_nn = old_node_to_coms[nn]
                for nn_c in communities_nn:
                    if nn_c in label_freq:
                        # case of weighted graph
                        if weight:
                            label_freq[nn_c] = label_freq[nn_c] + ego_minus_ego.edge[nn][n][weight]
                        else:
                            label_freq[nn_c] += 1
                    else:
                        # case of weighted graph
                        if weight:
                            label_freq[nn_c] = ego_minus_ego.edge[nn][n][weight]
                        else:
                            label_freq[nn_c] = 1

            # first run, random choosing of the communities among the neighbors labels
            if t == 0:
                if not len(n_neighbors) == 0:
                    r_label = random.sample(label_freq.keys(), 1)
                    ego_minus_ego.node[n]['communities'] = r_label
                    old_node_to_coms[n] = r_label

            # choosing the majority
            else:
                max_freq = max(label_freq.values())
                labels = [l for l in label_freq if label_freq[l] == max_freq]
                node_to_coms[n] = labels
                if n not in old_node_to_coms or not set(node_to_coms[n]) == set(old_node_to_coms[n]):
                    old_node_to_coms[n] = node_to_coms[n]
                    ego_minus_ego.node[n]['communities'] = labels

    # build the communities reintroducing the ego
    community_to_nodes = {}
    for n in nx.nodes(ego_minus_ego):
        if len(ego_minus_ego[n]) == 0:
            ego_minus_ego.node[n]['communities'] = [n]
        c_n = ego_minus_ego.node[n]['communities']
        for c in c_n:
            if c in community_to_nodes:
                community_to_nodes[c].append(n)
            else:
                community_to_nodes[c] = [n, ego]

    return community_to_nodes


def _merge_communities(communities, actual_community, epsilon):
    """
    Builds communities using the incomplete communities detected by the label
    propagation algorithm in the EgoMinusEgo graphs.

    Parameters
    ----------
    communities: dict
        Dictionary of communities

    actual_community: set
        A community

    epsilon: real
        The tolerance required in order to merge communities.

    Returns
    -------
    communities : list
        Merged communities
    """

    # if the community is already present return
    if actual_community in communities:
        return communities

    else:
        # search a community to merge with
        for test_community in communities:
            union = _generalized_inclusion(actual_community, test_community, epsilon)
            # community to merge with found
            if union:
                communities.pop(communities.index(test_community))
                communities.append(union)
                break
        # not merged: insert the original community
        else:
            communities.append(actual_community)

    return communities


def _generalized_inclusion(c1, c2, epsilon):
    """
    As explained in [1]_:
    "Two  communities C and I are  merged  if  and  only  if  at most the
    epsilon % of the smaller one is not included in the bigger one;  in  this
    case, C and I are removed from the community list and their union is added
    to the result set. The epsilon factor is introduced to vary the percentage
    of common elements provided from each couple of communities: epsilon = 0
    ensure that two communities are merged only if one of them is a proper
    subset of the other, on the other hand with a value of epsilon = 1 even
    communities that do not share a single node are merged together"

    Parameters
    ----------
    c1 : set
        Community 1.

    c2 : set
        Community 2.

    epsilon: real
        The tolerance required in order to merge communities

    Returns
    -------
    union : set
        Union of both communities if the similarity is greater than epsilon

    References
    ----------
    .. [1] Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
           DEMON: a local-first discovery method for overlapping communities.
           KDD 2012:615-623.
    """
    intersection = c2 & c1
    smaller_set_size = min(len(c1), len(c2))

    if len(intersection) > 0 and smaller_set_size > 0:
        inclusion_pct = len(intersection) / smaller_set_size

        if inclusion_pct > epsilon:
            union = c2 | c1
            return union

    return None
