# modularity.py - functions for finding communities based on modularity
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
    >>> c = greedy_modularity_communities(k)
    >>> list(c)
    [frozenset({8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33}),
     frozenset({1, 2, 3, 7, 12, 13, 17, 19, 21}),
     frozenset({0, 4, 5, 6, 10, 11, 16})]
     
     References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', page 224
       Oxford University Press 2011.
    .. [2] Clauset, A., Newman, M. E., & Moore, C.
       "Finding community structure in very large networks."
       Physical Review E 70(6), 2004.
    """
    
    # First create one community for each node
    old_communities = list([frozenset([u]) for u in G.nodes()])
    
    # Greedily merge communities until no improvement is possible
    old_modularity = modularity(G, old_communities)
    new_modularity = None
    while new_modularity is None or new_modularity > old_modularity:
        # Find best pair to merge
        if new_modularity is not None:
            old_modularity = new_modularity
        new_communities = list(old_communities)
        to_merge = None
        for i, u in enumerate(old_communities):
            for j, v in enumerate(old_communities):
                if j <= i:
                    continue
                # Merge communities u and v
                new_communities[i] = u | v
                new_communities[j] = frozenset([])
                trial_modularity = modularity(G, new_communities)
                if trial_modularity > old_modularity:
                    # Found new best, save modularity and group indexes
                    new_modularity = trial_modularity
                    to_merge = (i, j)
                # Un-merge
                new_communities[i] = u
                new_communities[j] = v
        if to_merge is not None:
            # If the best merge improves modularity, use it
            i, j = to_merge
            u, v = new_communities[i], new_communities[j]
            new_communities[i] = u | v
            # Faster than removing empty community from middle of list:
            # Swap empty community and last, then remove last
            new_communities[j] = new_communities[-1]
            new_communities.pop()
            old_communities = new_communities
    for com in sorted(new_communities, key=lambda x: (len(x), len(x) or x[0]), reverse=True):
        yield com
