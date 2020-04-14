# -*- coding: utf-8 -*-
"""
This module implements useful functions to prepare data for
drawing dendrograms of community detections performed by the
Girvan-Newman algorithm on graphs.

You can look at some other examples on
[github](https://github.com/FrancescoBonacina/dendrogram_girvan-newman).
"""

import numpy as np
import networkx as nx

from networkx.algorithms.community.quality import modularity
from networkx.algorithms.community.centrality import girvan_newman

__author__ = """Francesco Bonacina (francesco.bonacina@edu.unito.it)"""
#    Copyright (C) 2020 by
#    Francesco Bonacina (francesco.bonacina@edu.unito.it)
#    All rights reserved.
#    BSD license.

__all__ = ['girvan_newman_partitions',
           'agglomerative_matrix',
           'girvan_newman_best_partition',
           'distance_of_partition']


def girvan_newman_partitions(G):
    """ Returns the list of graph partitions detected by `girvan_newman`.

    Parameters
    ----------
    G : NetworkX graph
        `G` must meet 2 conditions:
        1. `G` must contain only one connected component
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    Returns
    -------
    list
        List of lists of sets of nodes in `G`. Each set of nodes
        is a community, each list is a sequence of communities at a
        particular level of the algorithm. The sets in each list
        will be sorted according to the smallest node they contain.
        e.g.:
        [ {0}, {4}, {1,3}, {2,6,7}, {5} ]    will be sorted in this way:
        [ {0}, {1,3}, {2,6,7}, {4}, {5} ]
        The list of partitions has length equal to (number_of_nodes - 1)

    Raises
    ------
    TypeError
        If `G` does not meet the conditions:
        1. `G` must contain only one connected componet
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    Example
    --------
    To get the list of partitions detected using the Girvan-Newman algorithm::

        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> for part in partitions:
        ...     print (part)
        ...
        [{0, 1, 2}, {3, 4, 5}]
        [{0}, {1, 2}, {3, 4, 5}]
        [{0}, {1, 2}, {3}, {4, 5}]
        [{0}, {1}, {2}, {3}, {4, 5}]
        [{0}, {1}, {2}, {3}, {4}, {5}]

    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively
    removing edges from the original graph. The algorithm removes the
    "most valuable" edge, traditionally the edge with the highest
    betweenness centrality, at each step. As the graph breaks down into
    pieces, the tightly knit community structure is exposed and the
    result can be depicted as a dendrogram.
    """

    # Does G meet the conditions?
    if nx.number_connected_components(G) > 1:
        raise TypeError("Bad graph type: do not use a graph with " +
                        "more connected components")
    _nodes = nx.nodes(G)
    _nn = nx.number_of_nodes(G)
    _good_nodes = np.arange(_nn)
    if not set(_nodes) == set(_good_nodes):
        raise TypeError("Bad graph type: use a graph with nodes " +
                        "which are integers from 0 to (number_of_nodes - 1)")

    # Get list of partitions using
    # 'networkx.algorithms.community.centrality.girvan_newman'
    _gn_partitions = list(girvan_newman(G))

    # Sort each partition: each partition contains communities (sets of nodes)
    # which will be sorted according to the smallest node they contain.
    gn_partitions = []
    for part in _gn_partitions:
        sorted_part = sorted(part, key=lambda x: min(x))
        gn_partitions.append(sorted_part)

    return gn_partitions


def _list2dict(list_partitions, number_nodes):
    """ Rearranges the `list_partitions' into a list of dictionaries.

    Parameters
    ----------
    list_partitions : list
        List of (number_nodes -1) lists got using `girvan_newman_partitions`.
        Each list contains the information about the partition of that level.

    number_nodes : integer
        number of nodes in the graph.

    Returns
    -------
    list
        List of dictionaries. The list has length (number_of_nodes - 1).
        The dictionary ith contains the information about the partition of the
        level ith and it has this form:
            - key: integer, label of the node;
            - value: integer, label of the community the node belongs to.
    """
    list_of_dict = [0]*(number_nodes-1)
    c = 0

    for part in list_partitions:
        # Transform to a dict
        tmp_dict = {}
        for i, part_i in enumerate(part):
            for j in part_i:
                tmp_dict[j] = i
        list_of_dict[c] = tmp_dict
        c += 1

    return list_of_dict


def _informative_dict(list_of_dict, number_nodes):
    """ Creates a list of dictionaries, each one containing information about
    the partition of that level.

    Parameters
    ----------
    list_of_dict : list of dictionaries
        List of (`number_nodes` - 1) dictionaries. It is the output
        of `_list2dict`.

    number_nodes : integer
        number of nodes in the graph.

    Returns
    -------
    list
        List of dictionaries. The list has length (`number_nodes` - 1).
        The dictionary ith contains the information about the partition of the
        level ith and it has this form:
            - key: integer, label of the node;
            - value: list of integers,
                [label of the community the node belongs to,
                distance of the community from the ground level,
                number of nodes in the community]
     """
    _list_of_dict = list_of_dict[::-1]
    informative_dict = [0] * (number_nodes-1)

    # Compute newdict_0, the first dict of the list 'informative_dict'
    dict_0 = dict(_list_of_dict[0])
    newkey_0 = list(dict_0.keys())
    newval_0 = [[i, 0, 1] for i in list(dict_0.values())]
    newdict_0 = {k : v for k, v in zip(newkey_0, newval_0)}

    informative_dict[0] = newdict_0

    # Compute newdict_i
    dict_cur = dict(dict_0)

    c = 0
    for dict_i in _list_of_dict:
        dict_pre = dict(dict_cur)  # Old dict with info about previous partitio
        dict_cur = dict(dict_i)    # Old dict with info about current partition

        if c > 0:
            # The new dict with info about the previous partition
            newdict_pre = informative_dict[c-1]

            # Look for key with different val in dict_pre and in dict_cur
            mykey = -999
            for i in range(number_nodes):
                if dict_pre[i] != dict_cur[i]:
                    mykey = i
                    break
            if mykey == -999:
                raise ValueError('ERROR: New community not found,' +
                                 ' fix list_of_dict')

            # Update info of nodes belonging to the new community.
            # Community A and B are the two communities that are joined
            # to form the new community.
            mycom = dict_cur[mykey]
            info_nodeA = newdict_pre[mykey]
            info_nodeB = []
            for k, v in dict_cur.items():
                if (k != mykey) and (v == mycom):
                    if newdict_pre[k] != info_nodeA:
                        info_nodeB = newdict_pre[k]
                        break
            info_newcom = [number_nodes - 1 + c,
                           max(info_nodeA[1], info_nodeB[1]) + 1,
                           info_nodeA[2] + info_nodeB[2]]

            # Create newdict_cur, the new dictionary with info about
            # the current partition
            newdict_cur = dict(newdict_pre)

            comA_pre = info_nodeA[0]
            comB_pre = info_nodeB[0]
            j = 0
            for k, v in newdict_pre.items():
                if (v[0] == comA_pre) or (v[0] == comB_pre):
                    newdict_cur[k] = info_newcom
                    j += 1
                if j == info_newcom[2]:
                    break
            if j < info_newcom[2]:
                raise ValueError('ERROR: not found the %d nodes belonging to' +
                                 ' the new community' % info_newcom[2])

            informative_dict[c] = newdict_cur

        c += 1

    return informative_dict


def agglomerative_matrix(G, list_partitions):
    """ Perform hierarchical/agglomerative clustering.

    Creates the "agglomerative matrix" of a graph from the community detection
    performed with the Girvan-Newman algorithm.
    The Girvan–Newman algorithm detects communities by progressively removing
    edges from the original graph. The algorithm removes the "most valuable"
    edge, traditionally the edge with the highest betweenness centrality, at
    each step. As the graph breaks down into pieces, the tightly knit community
    structure is exposed and the result can be depicted as a dendrogram.
    The Girvan_Newman algorithm detects (number_nodes - 1) partitions: in
    particular the first partition will contain 2 communities while in the last
    one each node will be a different community (so, there will be
    'number_nodes' different communities). The idea is to start from the last
    partition and retrace the path that unites the communities to the first
    partition. That is to reconstruct the process of agglomeration of the
    communities. The "agglomerative matrix" will contain this information.

    This is a matrix of the same type of the one created by the
    `scipy.cluster.hierarchy.linkage` function.

    The purpose of the `agglomerative_matrix` function is to create a
    matrix we can use to plot a dendrogram with
    `scipy.cluster.hierarchy.dendrogram`.

    To look at some other examples go to [github]
    (https://github.com/FrancescoBonacina/dendrogram_girvan-newman).

    Parameters
    ----------
    G : NetworkX graph
        `G` must meet 2 conditions:
        1. `G` must contain only one connected componet
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    list_partitions : list
        List of (number_nodes -1) lists got using `girvan_newman_partitions`.
        Each list contains the information about the partition of that level.

    Returns
    -------
    numpy.ndarray
        The "agglomerative matrix" (AM) is a numpy.ndarray with shape
        (number_nodes -1)x4. The ith row contains information about the new
        community created at that level by merging 2 existing communities.
        So the first row contains information about the first new community,
        which will contain 2 nodes, while the last row contains information
        about the 2 communities which merge to generate the entire graph
        (with 'number_nodes' nodes).
        The 4 columns contain the following information:
            AM[i,0] = integer, label of the existing community A. The community
                      A will be merge to the existing community B to form the
                      ith new community.
            AM[i,1] = integer, label of the existing community B.
                      (With AM[i,0] < AM[i,1]).
            AM[i,2] = integer, distance of the ith new community from the
                      level zero.
            AM[i,3] = integer, number of nodes in the ith new community.
        A community with an index less than 'number_nodes' corresponds to one
        which contains only that single node. A community with an index
        belonging to [number_nodes, 2*number_nodes - 3] corresponds to one of
        the new communities formed in the agglomeration process.

    Raises
    ------
    TypeError
        If `G` does not meet the conditions:
        1. `G` must contain inly one connected componet
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    Example
    --------
    To get the "agglomerative matrix" of graph G::

        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> agglomerative_mat = agglomerative_matrix(G, partitions)
        >>> print (agglomerative_mat)
        [[4. 5. 1. 2.]
         [1. 2. 1. 2.]
         [3. 6. 2. 3.]
         [0. 7. 2. 3.]
         [8. 9. 5. 6.]]

    To plot the dendrogram of community detection performed on graph G::

        >>> from scipy.cluster.hierarchy import dendrogram
        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> agglomerative_mat = agglomerative_matrix(G, partitions)
        >>> dendro_G = dendrogram(agglomerative_mat)

     """
    # Does G meet the conditions?
    if nx.number_connected_components(G) > 1:
        raise TypeError("Bad graph type: do not use a graph with more " +
                        " connected components")
    _nodes = nx.nodes(G)
    nn = nx.number_of_nodes(G)
    _good_nodes = np.arange(nn)
    if not set(_nodes) == set(_good_nodes):
        raise TypeError("Bad graph type: use a graph with nodes which are " +
                        "integers from 0 to (number_of_nodes - 1)")

    # Set out the list of partitions in a list of dictionaries containing
    # information on the agglomeration of communities.
    list_of_dict = _list2dict(list_partitions, nn)
    list_info_dict = _informative_dict(list_of_dict, nn)

    # Create the 'agglomerative matrix'
    AM = np.zeros((nn - 1, 4), dtype='float')

    row = 0
    comA = 0
    comB = 0
    dist = 0
    nn_com = 0

    for row in range(nn - 1):
        # For row from 0 to nn-2
        if row < nn-2:
            # dict of info about previous partition and current partition
            dict_pre = dict(list_info_dict[row])
            dict_cur = dict(list_info_dict[row + 1])

            # Which are the nodes who belong to the new community?
            new_com = nn + row   # Label of community created at this level
            n_found = 0
            number_nodes = -1
            nodes_in_newcom = []
            for i in range(nn):                # Look for all nodes belonging
                if dict_cur[i][0] == new_com:  # to the new community. Their
                    nodes_in_newcom.append(i)  # labels will be stored in
                    if n_found == 0:           # 'nodes_in_newcom'
                        info_newcom = dict_cur[i]
                        number_nodes = info_newcom[2]
                    n_found += 1
                if n_found == number_nodes:
                    break

            # Look for info of communities A and B which are merged to form
            # the new community
            if number_nodes < 2:
                raise ValueError('ERROR: the new community has less ' +
                                 'than 2 nodes')
            elif number_nodes == 2:
                comA = min(nodes_in_newcom[0], nodes_in_newcom[1])
                comB = max(nodes_in_newcom[0], nodes_in_newcom[1])
                dist = info_newcom[1]
                nn_com = number_nodes
            else:
                tmp_comA = dict_pre[nodes_in_newcom[0]][0]
                for i in range(number_nodes):
                    if dict_pre[nodes_in_newcom[i + 1]][0] != tmp_comA:
                        tmp_comB = dict_pre[nodes_in_newcom[i + 1]][0]
                        break
                comA = min(tmp_comA, tmp_comB)
                comB = max(tmp_comA, tmp_comB)
                dist = info_newcom[1]
                nn_com = number_nodes

            # Fill the agglomerative matrix
            AM[row] = [comA, comB, dist, nn_com]

        # For row number nn-2, the last one. (Rows go from 0 to nn-2)
        if row == nn-2:
            dict_pre = dict(list_info_dict[row])

            info_comA = dict_pre[nn - 1]
            info_comB = []
            for i in range(nn):
                if dict_pre[i][0] != info_comA[0]:
                    info_comB = dict_pre[i]
                    break
            comA = min(info_comA[0], info_comB[0])
            comB = max(info_comA[0], info_comB[0])
            dist = max(info_comA[1], info_comB[1]) + 1
            nn_com = info_comA[2] + info_comB[2]

            # Check: does the last community contain all the nodes?
            if nn_com != nn:
                raise ValueError('ERROR: the last community (which is' +
                                 ' the entire graph) does not contain' +
                                 ' "number_nodes" nodes')

            # Fill the last row of the 'agglomerative_matrix'
            AM[row] = [comA, comB, dist, nn_com]

    return AM


def girvan_newman_best_partition(G, list_partitions):
    """ Returns the best partition on the `list_partitions`.

    Returns the best partition among those generated by the Girvan-Newman
    algorithm. The best partition is selected according to modularity,
    computed using `networkx.algorithms.community.quality.modularity`.

    Parameters
    ----------
    G : NetworkX graph
        `G` must meet 2 conditions:
        1. `G` must contain only one connected componet
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    list_partitions : list
        List of (number_nodes -1) lists got using `girvan_newman_partitions`.
        Each list contains the information about the partition of that level.

    Returns
    -------
    tupla
        Tupla of 2 elements:
        Fisrt element: list with information about the best partition.
                       It is a list of sets of nodes, each set of nodes
                       is a community.
        Second element: integer, position of the partition in `list_partitions`
                        which corresponds to the best partition.

    Raises
    ------
    TypeError
        If `G` does not meet the conditions:
        1. `G` must contain only one connected componet
        2. The nodes must be integers from 0 to (number_of_nodes - 1)

    Example
    --------
    To get the best partition of `G` among those detected by the
    Girvan-Newman algorithm::

        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> bp_G, index_bp_G = girvan_newman_best_partition(G, partitions)
        >>> print (bp_G)
        ... [{0, 1, 2}, {3, 4, 5}]
        >>> print (index_bp_G)
        ... 0

    To plot the dendrogram of community detection performed on graph G,
    highlighting the best partition::

        >>> from scipy.cluster.hierarchy import dendrogram
        >>> # Create graph and perform community detection with Girvan-Newman
        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> # Compute the agglomerative matrix
        >>> agglomerative_mat = agglomerative_matrix(G, partitions)
        >>> # Find the best partition and its distance from the ground level
        >>> bp_G, idx_bp_G = girvan_newman_best_partition(G, partitions)
        >>> n_communities_bp = len(bp_G)
        >>> dis_bp = distance_of_partition(agglomerative_mat, n_communities_bp)
        >>> # Plot the dendrogram highlighting the best partition
        >>> dendro_bp = dendrogram(agglomerative_mat, color_threshold=dis_bp)

     """
    # Does G meet the conditions?
    if nx.number_connected_components(G) > 1:
        raise TypeError("Bad graph type: do not use a graph with more" +
                        " connected components")
    _nodes = nx.nodes(G)
    nn = nx.number_of_nodes(G)
    _good_nodes = np.arange(nn)
    if not set(_nodes) == set(_good_nodes):
        raise TypeError("Bad graph type: use a graph with nodes which" +
                        " are integers from 0 to (number_of_nodes - 1)")

    # Look for the best partition
    best_partition = []
    MAX_mod = -99
    c = 0
    for part in list_partitions:
        # Compute modularity
        tmp_mod = modularity(G, part)

        # If modularity icreases, then update `best_partition`
        if tmp_mod > MAX_mod:
            MAX_mod = tmp_mod
            best_partition = part
            id_best_part = c

        c += 1

    return (best_partition, id_best_part)


def distance_of_partition(agglomerative_matrix, n_communities):
    """ Returns the distance of the partition from the ground level.

    The partition considered is the one which splits the graph into
    `n_communities` different communities.

    Parameters
    ----------
    agglomerative_matrix: numpy.ndarray
        Matrix which encodes the hierarchical clustering to render as
        a dendrogram. The hierarchical clustering is detected using the
        Girvan-Newman algorithm. See the `agglomerative_matrix` function
        for more information on the format of `agglomerative_matrix`.

    n_comunities: integer
        The number of communities into which the partition we are
        interested in is split.

    Returns
    -------
    integer
        Distance of the partition we are interested in from the ground level.
        Which is the distance from the hierarchy level where all nodes are
        disconnected.

    Raises
    ------
    TypeError
        If n_communities does not belong to [1, number_nodes]

    Example
    --------
    To get the distance of the partition with 2 communities from the
    ground level::

        >>> G = nx.path_graph(6)
        >>> partitions = girvan_newman_partitions(G)
        >>> agglomerative_mat = agglomerative_matrix(G, partitions)
        >>> n_communities = 2
        >>> dist_2comm = distance_of_partition(agglomerative_mat,
                                               n_communities)
        >>> print (dist_2comm)
        ... 3

    To plot the dendrogram highlighting the partition which splits the graph
    into 2 communities::

        >>> from scipy.cluster.hierarchy import dendrogram
        >>> dendro_2comm = dendrogram(agglomerative_mat,
                                      color_threshold=dist_2comm)

     """
    # Check if 'n_communities' belongs to the interval [1, number_nodes].
    nn = len(agglomerative_matrix[:, 0]) + 1
    if (n_communities < 1) or (n_communities > nn):
        raise TypeError('Bad number of communities: n_communities must be' +
                        ' an integer between 1 and number_nodes')

    # High of the level of the hierarchy in which the graph is split
    # into 'n_communities' different partitions.
    high_max = int(agglomerative_matrix[-1, 2])
    partition_height = high_max - (n_communities - 2)

    return partition_height
