from collections import defaultdict
import itertools
import networkx as nx
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])

def is_partition(N,C):
    """Determines whether C partitions N

    Parameters
    ----------
    G : Container
    C : list of sets

    Returns
    -------
    is_partition : boolean
       Whether C is a partition of G

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> nx.is_partition(G.nodes(),[set(range(3)),set(range(3,6))])
    True
    >>> nx.is_partition(G.nodes(),[set(range(3)),set(range(2,6))])
    False

    References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', pages 359
       Oxford University Press 2011.
    """
    for n in N:
        aff = affiliation(n,C)
        if not len(aff) == 1:
            return False
    return True

def affiliation(n,C):
    """Return the affiliation of n for a given
    community C

    Parameters
    ----------
    n : object
    C : list of sets
      Community structure to search in

    Returns
    -------
    aff : list of ints
      Index of affiliation of n

    Examples
    --------
    >>> C = [set(['a','b']),set(['a'])]
    >>> nx.affiliation('a',C)
    [0,1]
    >>> nx.affiliation('b',C)
    [0]
    """
    aff = []
    i = 0
    for c in C:
        if n in c:
            aff.append(i)
        i+=1
    return aff

def draw_partition(G,C,*args,**kwargs):
    """Not for release, just for testing"""
    try:
        import nx_opengl
        draw = nx_opengl.draw_opengl
    except ImportError:
        draw = nx.draw
            
    colors = ['r','b','g','c','m','k','y']

    nc = []
    for n in G:
        aff = nx.affiliation(n,C)[0]
        nc.append(colors[aff % 7])

    draw(G,*args,node_color=nc,**kwargs)

def affiliation_dict(community):
    """Return dictionary mapping node to a list of community labels.
    The community labels are arbitrary.
    """
    aff=defaultdict(list)
    for i,partition in enumerate(community):
        for n in partition:
            aff[n].append(i)
    return aff
            
def community_sets(affiliation):
    """Return list of community sets from affiliation dictionary
    """
    communities=defaultdict(set)
    for n,cc in affiliation.items():
        try: # overlapping communites, dict value is list
            for c in cc:
                communities[c].add(n)
        except TypeError: # non-overlapping, dict value is single item
            communities[cc].add(n)
    return list(communities.values())

def unique_community(G,community):
    """Return True if community partitions G into unique sets.
    """
    community_size=sum(len(c) for c in community)
    # communitity size must have same number of nodes as G
    if not len(G)==community_size:
        return False  
    # check that the set of nodes in the communities is the same as G
    if not set(G)==set.union(*community):
        return False
    return True
    
def overlapping_community(G,community):
    """Return True if community partitions G into overlapping sets.
    """
    community_size=sum(len(c) for c in community)
    # community size must be larger to be overlapping
    if not len(G) < community_size:
        return False
    # check that the set of nodes in the communities is the same as G
    if not set(G)==set.union(*community):
        return False
    return True

