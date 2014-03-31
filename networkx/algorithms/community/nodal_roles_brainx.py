#Author: Maxwell Bertolero, bertolero@berkeley.edu, mbertolero@gmail.com

import numpy as np
from random import choice
import networkx as nx

def within_community_degree(weighted_partition, nan = 0.0, catch_edgeless_node=True):
    ''' Computes "within-module degree" (z-score) for each node (Guimera 2007, J Stat Mech)

    ------
    Parameters
    ------
    weighted_partition: Louvain Weighted Partition
        louvain = weighted_modularity.LouvainCommunityDetection(graph)
        weighted_partitions = louvain.run()
        weighted_partition = weighted_partition[0], where index is the partition level
    nan : int
        number to replace unexpected values (e.g., -infinity) with
        default = 0.0
    catch_edgeless_node: Boolean
        raise ValueError if node degree is zero
        default = True

    ------
    Returns
    ------
    within_community_degree: dict
        Dictionary of the within community degree of each node.

    '''
    wc_dict = {}
    for c, community in enumerate(weighted_partition.communities):
        community_degrees = []
        for node in community: #get average within-community-degree
            node_degree = weighted_partition.node_degree(node)
            if node_degree == 0.0: #catch edgeless nodes
                if catch_edgeless_node:
                    raise ValueError("Node {} is edgeless".format(node))
                wc_dict[node] = 0.0
                continue
            community_degrees.append(weighted_partition.node_degree_by_community(node)[c])
        for node in community: #get node's within_community-degree z-score
            within_community_degree = weighted_partition.node_degree_by_community(node)[c]
            std = np.std(community_degrees) # std of community's degrees
            mean = np.mean(community_degrees) # mean of community's degrees
            if std == 0.0: #so we don't divide by 0
                wc_dict[node] = (within_community_degree - mean) #z_score
                continue
            wc_dict[node] = (within_community_degree - mean / std) #z_score
    return wc_dict

def participation_coefficient(weighted_partition, catch_edgeless_node=True):
    '''
    Computes the participation coefficient for each node (Guimera 2007, J Stat Mech)

    ------
    Parameters
    ------
    weighted_partition: Louvain Weighted Partition
        louvain = weighted_modularity.LouvainCommunityDetection(graph)
        weighted_partitions = louvain.run()
        weighted_partition = weighted_partition[0], where index is the partition level
    catch_edgeless_node: Boolean
        raise ValueError if node degree is zero
        default = True

    ------
    Returns
    ------
    participation_coefficient: dict
        Dictionary of the participation coefficient of each node.
    '''
    pc_dict = {}
    graph = weighted_partition.graph
    for node in graph:
        node_degree = weighted_partition.node_degree(node)
        if node_degree == 0.0: 
            if catch_edgeless_node:
                raise ValueError("Node {} is edgeless".format(node))
            pc_dict[node] = 0.0
            continue    
        deg_per_comm = weighted_partition.node_degree_by_community(node)
        deg_per_comm.pop(weighted_partition.get_node_community(node))
        bc_degree = sum(deg_per_comm) #between community degree
        if bc_degree == 0.0:
            pc_dict[node] = 0.0
            continue
        pc = 1 - ((float(bc_degree) / float(node_degree))**2)
        pc_dict[node] = pc
    return pc_dict