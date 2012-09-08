from copy import copy
import random
import networkx as nx

#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.

__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Ben Edwards (bedwards@cs.unm.edu)'])


def random_partition(N,
                    number_of_partitions=None,
                    partition_sizes=None):
    """Partition a container of objects N.

    Can either specify the number of partitions or the
    size of each partition.

    Parameters
    ----------
    N : iterable
      Iterable container of hashable objects
    number_of_partitions : int
      Number of partitions
    partition_sizes : iterable of ints
      Sizes of partitions

    Returns
    -------
    C : list of sets
      Partition of N

    Raises
    ------
    NetworkXError
      If neither the number of partitions or partitions sizes
      are included or if the sum of the partitions sizes is not
      the same as the number of objects in N

    Examples
    --------
    >>> nx.random_partition(range(10),number_of_partitions=2)
    [set([1, 3, 4, 7, 8]), set([0, 2, 5, 6, 9])]
    >>> nx.random_partition(range(10),partition_sizes=[3,7])
    [set([2, 5, 6]), set([0, 1, 3, 4, 7, 8, 9])]
    """
    
    if partition_sizes is None and number_of_partitions is None:
        raise nx.NetworkXError("Must include either number of paritions \
                            or parition sizes")

    if partition_sizes is None:
        C = [set() for _ in range(number_of_partitions)]
        for n in N:
            C[random.randrange(0,number_of_partitions)].add(n)
    else:
        if not sum(partition_sizes) == len(N):
            raise nx.NetworkXError("Size of partitions must sum to the number \
                                 of objects")
        C = [set() for _ in range(len(partition_sizes))]
        ns = copy(N)
        i = 0
        for s in partition_sizes:
            for _ in range(s):
                n = ns.pop(random.randrange(0,len(ns)))
                C[i].add(n)
            i+=1
    return C

def random_p_community(N,p,number_of_communities=None):
    """Create a random set of communities from iterable N.

    Each n in N is a member of a community with probability p
    p can either be a single value, in which case the number of
    communiites must be specified, or it can be a iterable of values
    containing the probability of an object being a member of a
    community at that index.

    Parameters
    ----------
    N : iterable
      Iterable container of hashable objects
    p : float or container of floats
      Probability of an object being in a community
    number_of_communities: int
      Inferred from p if p is a container, otherwise
      must be specified

    Returns
    -------
    C : list of sets
       Community division of N

    Raises
    ------
    NetworkXError
      If p is not specified correctly

    See Also
    --------
      random_m_community

    Examples
    --------
    >>> nx.random_p_community(range(10),.1,number_of_communities = 4)
    [set(), set([1, 2]), set([5]), set()]
    >>> nx.random_p_community(range(10),[.1,.5,.1])
    [set([0, 1]), set([0, 3, 6, 8]), set([3])]
    """
    if number_of_communities is None:
        try:
            number_of_communities = len(p)
        except TypeError:
            raise nx.NetworkXError("Must specify number of communities or probabilty \
                                 p of being in each community")
    else:
        p = [p]*number_of_communities

    C = [set() for _ in range(number_of_communities)]
    for n in N:
        i = 0
        for c in range(number_of_communities):
            if random.random() < p[i]:
                C[c].add(n)
            i += 1
    return C

def random_m_community(N,m,number_of_communities=None):
    """Create a random set of communities from iterable N.

    Each community has size exactly m. m can either be a single
    int or a containter of ints containing the sizes of each
    community.

    Parameters
    ----------
    N : iterable
      Iterable container of hashable objects
    m : int or container of ints
      Sizes of each community
    number_of_communities : int
      Number of communities to create, inferred from m if m is a
      container.

    Returns
    -------
    C : list of sets
      Communities of objects

    Raises
    ------
    NetworkXError
      If m is not specified correctly or if the size of a community
      exceeds the number of objects in N

    See Also
    --------
    random_p_community

    Examples
    --------
    >>> nx.random_m_community(range(10),2,number_of_communities=3)
    [set([1, 6]), set([8, 9]), set([8, 9])]
    >>> nx.random_m_community(range(10),[2,3,3,3])
    [set([0, 8]), set([3, 7, 9]), set([2, 7, 8]), set([1, 2, 8])]
    """
    
    if number_of_communities is None:
        try:
            number_of_communities = len(m)
        except TypeError:
            raise nx.NetworkXError("Must specify number of communities or \
                                    size m of each community")
    else:
        m = [m]*number_of_communities

    C = []
    for c in range(number_of_communities):
        C.append(set())
        if m[c] > len(N):
            raise nx.NetworkXError("Community size %i is greater than \
                                    size of N"%c)
        while len(C[c]) < m[c]:
            C[c].add(random.choice(N))
    return C
            
