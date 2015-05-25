#-*- coding: utf-8 -*-
#    Copyright (C) 2015 
#    All rights reserved.
#    BSD license.

"""
Flat Merge version of DEMON (Democratic Estimate of the Modular Organization of 
a Network) algorithm as described in:

Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
DEMON: a local-first discovery method for overlapping communities.
KDD 2012:615-623

DEMON uses a local-first approach to community discovery were each node
democratically votes for the communities that it sees in its surroundings. It 
provides a deterministic, fully incremental method for community discovery that
has a limited time complexity.

Based on the implementation by Giulio Rossetti <giulio.rossetti@isti.cnr.it>:
http://www.michelecoscia.com/wp-content/uploads/2013/07/demon_py.zip
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
    Communities in this algorithm can be overlapping
    
    Algorithm:
    ----------
    Require: G(V, E), C' = 0, epsilon = [0..1]
    Ensure: set of overlapping communities C'
        
    1: for all v in V do:
    2:   e <- EgoMinusEgo(v, G)    
    3:   C(v) <- LabelPropagation(e)
    4:   for all C in C'(v) do:
    5:     C <- C union v
    6:     C' <- Merge(C', C, v)
    7:   end for
    8: end for
    9: return C' 
       
    Parameters
    ----------
    G : graph
        An NetworkX graph. 
    
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
    
    for n in G.nodes():
            G.node[n]['communities'] = [n]                   
    
    all_communities = []

    for ego in nx.nodes(G):
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

def _overlapping_label_propagation(ego_minus_ego, ego, weight, max_iteration=100):
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
    
    max_iteration : integer
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
    t = 0

    old_node_to_coms = {}

    while t < max_iteration:
        t += 1

        node_to_coms = {}

        nodes = nx.nodes(ego_minus_ego)
        random.shuffle(nodes)

        count = -len(nodes)

        for n in nodes:
            label_freq = {}

            n_neighbors = nx.neighbors(ego_minus_ego, n)

            if len(n_neighbors) < 1:
                continue

            if count == 0:
                t += 1

            # compute the frequency of the labels
            for nn in n_neighbors:

                communities_nn = [nn]

                if nn in old_node_to_coms:
                    communities_nn = old_node_to_coms[nn]

                for nn_c in communities_nn:
                    if nn_c in label_freq:
                        v = label_freq.get(nn_c)
                        # case of weighted graph
                        if weight:
                            label_freq[nn_c] = v + ego_minus_ego.edge[nn][n][weight]
                        else:
                            label_freq[nn_c] = v + 1
                    else:
                        # case of weighted graph
                        if weight:
                            label_freq[nn_c] = ego_minus_ego.edge[nn][n][weight]
                        else:
                            label_freq[nn_c] = 1

            # first run, random choosing of the communities among the neighbors labels
            if t == 1:
                if not len(n_neighbors) == 0:
                    r_label = random.sample(label_freq.keys(), 1)
                    ego_minus_ego.node[n]['communities'] = r_label
                    old_node_to_coms[n] = r_label
                count += 1
                continue

            # choosing the majority
            else:
                labels = []
                max_freq = -1

                for l, c in label_freq.items():
                    if c > max_freq:
                        max_freq = c
                        labels = [l]
                    elif c == max_freq:
                        labels.append(l)

                node_to_coms[n] = labels

                if n not in old_node_to_coms or not set(node_to_coms[n]) == set(old_node_to_coms[n]):
                    old_node_to_coms[n] = node_to_coms[n]
                    ego_minus_ego.node[n]['communities'] = labels

        t += 1

    # build the communities reintroducing the ego
    community_to_nodes = {}
    for n in nx.nodes(ego_minus_ego):
        if len(nx.neighbors(ego_minus_ego, n)) == 0:
            ego_minus_ego.node[n]['communities'] = [n]

        c_n = ego_minus_ego.node[n]['communities']

        for c in c_n:
            if c in community_to_nodes:
                com = community_to_nodes.get(c)
                com.append(n)
            else:
                nodes = [n, ego]
                community_to_nodes[c] = nodes

    return community_to_nodes

def _merge_communities(communities, actual_community, epsilon):
    """
    Builds communities using the incomplete communities detected by the label
    propagation algorithm in the EgoMinusEgo graphs.
    
    Parameters
    ----------
    communities: dict
        Dictionary of communities
        
    actual_community: list
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
        inserted = False

        for test_community in communities:

            union = _generalized_inclusion(actual_community, test_community, epsilon)

            # communty to merge with found
            if union:
                communities.pop(test_community)
                communities.append(union)
                inserted = True
                break

        # not merged: insert the original community
        if not inserted:
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
    c1 : list
        Community 1. 
        
    c2 : list
        Community 2. 
    
    epsilon: real
        The tolerance required in order to merge communities
        
    Returns
    -------
    union : list
        Union of both communities if the similarity is greater than epsilon 
    
    References
    ----------
    .. [1] Michele Coscia, Giulio Rossetti, Fosca Giannotti, Dino Pedreschi:
           DEMON: a local-first discovery method for overlapping communities.
           KDD 2012:615-623.
    """
    intersection = c2 & c1
    smaller_set = min(len(c1), len(c2))
    
    if len(intersection) > 0 and smaller_set > 0:
        inclusion_pct = len(intersection) / smaller_set 

        if inclusion_pct > epsilon:
            union = c2 | c1
            return union
            
    return None


if __name__ == '__main__':
    
    test = nx.Graph()
    
    # community 1
    test.add_edge('a', 'b')
    test.add_edge('c', 'b')
    test.add_edge('a', 'c')
    test.add_edge('a', 'd')
    test.add_edge('b', 'd')
    test.add_edge('c', 'd')
    
    # community 2
    test.add_edge('e', 'f')
    test.add_edge('e', 'g')
    test.add_edge('e', 'h')
    test.add_edge('f', 'g')
    test.add_edge('f', 'h')
    test.add_edge('h', 'g')

    # connection from community 1 to community 2
    test.add_edge('a', 'middle')
    test.add_edge('e', 'middle')
   
    communities = demon_communities(test, 0.25, 3, None)
    for c in communities:
        print c
 
    
    
    