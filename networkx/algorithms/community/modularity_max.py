# modularity_max.py - functions for finding communities based on modularity
#
# Copyright 2018 NetworkX developers.
#
# This file is part of NetworkX
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
# Contributors:
# Edward L. Platt <ed@elplatt.com>
#
"""Functions for detecting communities based on modularity.
"""
from __future__ import division

import heapq
import networkx as nx
from networkx.algorithms.community.quality import modularity

__all__ = ['greedy_modularity_communities']

def greedy_modularity_communities(G):
    """Find communities in graph using the greedy modularity maximization.

    Greedy modularity maximization begins with each node in its own community
    and joins the pair of communities that most increases modularity until no
    such pair exists.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    Yields sets of nodes, one for each community.

    Examples
    --------
    >>> from networkx.algorithms.community import greedy_modularity_communities
    >>> G = nx.karate_club_graph()
    >>> c = list(greedy_modularity_communities(G))
    >>> sorted(c[0])
    [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    
     References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', page 224
       Oxford University Press 2011.
    """
    
    # First create one community for each node
    communities = list([frozenset([u]) for u in G.nodes()])
    
    # Track merges
    merges = []
    
    # Greedily merge communities until no improvement is possible
    old_modularity = None
    new_modularity = modularity(G, communities)
    while old_modularity is None or new_modularity > old_modularity:
        # Save modularity for comparison
        old_modularity = new_modularity
        # Find best pair to merge
        trial_communities = list(communities)
        to_merge = None
        for i, u in enumerate(communities):
            for j, v in enumerate(communities):
                # Skip i=j and empty communities
                if j <= i or len(u) == 0 or len(v) == 0:
                    continue
                # Merge communities u and v
                trial_communities[j] = u | v
                trial_communities[i] = frozenset([])
                trial_modularity = modularity(G, trial_communities)
                if trial_modularity >= new_modularity:
                    # Check if strictly better or tie
                    if trial_modularity > new_modularity:
                        # Found new best, save modularity and group indexes
                        new_modularity = trial_modularity
                        to_merge = (i, j, new_modularity - old_modularity)
                    elif to_merge and min(i, j) < min(to_merge[0], to_merge[1]):
                        # Break ties by chosing pair with lowest min id
                        new_modularity = trial_modularity
                        to_merge = (i, j, new_modularity - old_modularity)                        
                # Un-merge
                trial_communities[i] = u
                trial_communities[j] = v
        if to_merge is not None:
            # If the best merge improves modularity, use it
            merges.append(to_merge)
            i, j, dq = to_merge
            u, v = communities[i], communities[j]
            communities[j] = u | v
            communities[i] = frozenset([])
    # Remove empty communities and sort
    communities = [c for c in communities if len(c) > 0]
    for com in sorted(communities, key=lambda x: len(x), reverse=True):
        yield com