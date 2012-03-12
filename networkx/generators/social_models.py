#!/usr/bin/env python

"""
Generator for online social network models, Updated 03/12/2012

References
----------
[1] Sala A., Cao L., Wilson, C., Zablit, R., Zheng, H., Zhao, B. 
Measurement-calibrated graph models for social network experiments.
In Proc. of WWW (2010).

The paper describes 6 social graph models proposed to use as models
to replace social graphs: Barabasi-Albert, Forest Fire (modified),
Random Walk (modified), Nearest Neighbor (modified), Kronecker Graphs,
and dK-2.
* Models marked as "modified" have been modified to use undirected
graphs instead of the original directed

A Barabasi-Albert generator has already been implemented for NetworkX
as networkx.generators.random_graphs.barabasi_albert_graph()

As of 03/12/2012, modified Random Walk and Nearest Neighbor are implemented.
"""

#       Copyright (C) 2011 by
#       Alessandra Sala <alessandra@cs.ucsb.edu>
#       Lili Cao <lilicao@cs.ucsb.edu>
#       Christo Wilson <bowlin@cs.ucsb.edu>
#       Robert Zablit <rzablit.cs.ucsb.edu>
#       Haitao Zheng <htzheng@cs.ucsb.edu>
#       Ben Y. Zhao <ravenben@cs.ucsb.edu>
#       All rights reserved.
#       BSD License.

__author__ = 'Lili Cao (lilicao@cs.ucsb.edu), Adelbert Chang (adelbert_chang@cs.ucsb.edu)'

__all__ = ['undirected_random_walk', 'undirected_nearest_neighbor']

import networkx as nx
import random
import bisect

def undirected_random_walk(n, qe, qv):
    """
    Generates a graph based on a modified Random Walk model.

    This is a modified version of the Random Walk model that creates
    undirected edges instead of directed ones in the edge creation
    process. [1]

    Input:
        n = number of nodes in the graph (integer)
        qe = probability of continuing the walk at each step (float)
        qv = probability of attaching to a visited note (float)
    Output:
        nx.Graph()
    """
    # Prepare graph..
    G = nx.Graph()

    # Keeps track of next available node ID
    nodeCounter = 0

    while nodeCounter < n:
        # Add node to graph and increment nodeCounter
        target = nodeCounter
        G.add_node(target)
        nodeCounter += 1

        # If only 1 node is in the graph, there are nothing to do
        if target == 0: 
            continue

        # Attach node to random node in graph to ensure connectivity
        walkedNode = random.randrange(0, target)
        G.add_edge(target, walkedNode)

        # Do random walk
        while True:
            # With probability 'qv' attach to current node
            if random.random() <= qv:
                # No self-loops
                if walkedNode != target:
                    G.add_edge(target, walkedNode)
            # With probability 'qe' continue the random walk, else break out
            if random.random() <= qe:
                if len(G.neighbors(walkedNode)) > 0:
                    walkedNode = random.sample(G.neighbors(walkedNode), 1)[0]
            else:
                break
    return G

def undirected_nearest_neighbor(n, u, k):
    """
    Generates a graph based on a modified Nearest Neighbor model.

    This is a modified version of the Nearest Neighbor model that
    creates an undirected graph with power-law exponent between 1.5
    and 1.75 to match that of online social networks. This is done
    so that each time a new node is added, 'k' random pairs of nodes
    in the connected component of the graph are connected. [1]

    Input:
        n = number of nodes in the graph (int)
        u = probability that determines if a new node is added or
            if a pair of 2 hop neighbors is connected (float)
        k = each time a new node is added, 'k' pairs of random nodes
            in the connected component are connected (int)
    Output:
        nx.Graph()
    """
    G = nx.Graph()
    nodeCounter = 0 # Keeps track of ID of next available node

    degreeArray = [0 for i in range(0,n)]
    d = []
    N = [0 for i in range(0,2)]

    while nodeCounter < n: # Until we reach 'n' nodes...
        if random.random() < u:
            if len(d) == 0:
                continue

            x = random.choice(d) # Pick a node from list
            N = random.sample(G.neighbors(x), 2) # Pick 2 unique nodes in the list of neighbors

            if not G.has_edge(N[0], N[1]): # If no edge exists between the 2, connect
                G.add_edge(N[0], N[1])
                degreeArray[N[0]] += 1
                degreeArray[N[1]] += 1
                if degreeArray[N[0]] == 2:
                    bisect.insort(d, N[0])

                if degreeArray[N[1]] == 2:
                    bisect.insort(d, N[1])

        else:
            nodesSoFar = nodeCounter
            G.add_node(nodeCounter)
            nodeCounter += 1

            if nodeCounter == 1: # No use in continuing if there is only one node in the graph
                continue

            a = random.randrange(0, nodesSoFar) # Pick a node in the graph
            G.add_edge(a, nodesSoFar)
            degreeArray[a] += 1
            degreeArray[nodesSoFar] += 1

            if degreeArray[a] == 2:
                bisect.insort(d, a)
            if degreeArray[nodesSoFar] == 2:
                bisect.insort(d, nodesSoFar)

            for i in range(0, k): # Connect k random pairs in the graph
                N[0] = random.randint(0, nodeCounter - 1)
                N[1] = N[0]

                while N[1] == N[0]: # Ensure the two nodes are different (no self-loops)
                    N[1] = random.randint(0, nodeCounter - 1)

                if not G.has_edge(N[0], N[1]):
                    G.add_edge(N[0], N[1])

                    degreeArray[N[0]] += 1
                    degreeArray[N[1]] += 1

                    if degreeArray[N[0]] == 2:
                        bisect.insort(d, N[0])
                    if degreeArray[N[1]] == 2:
                        bisect.insort(d, N[1])

    return G
